import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from typing import List, Dict, Any, Tuple
from retrieval.search_engine import EnhancedSearchEngine
from evaluation.test_queries import TestQuery, TestQueryManager
import json
import time

class ManualEvaluator:
    """人工评价工具：帮助用户对搜索结果进行人工标注和评价"""
    
    def __init__(self, search_engine: EnhancedSearchEngine, query_manager: TestQueryManager):
        self.search_engine = search_engine
        self.query_manager = query_manager
        self.evaluation_file = "results/manual_evaluation.json"
        self.current_evaluations = {}  # {query_id: evaluation_data}
    
    def load_or_create_queries(self):
        """加载或创建测试查询"""
        if not self.query_manager.load_queries():
            print("创建默认测试查询集合...")
            self.query_manager.create_default_queries()
            self.query_manager.save_queries()
    
    def evaluate_query(self, query_id: int, max_results: int = 10) -> bool:
        """对单个查询进行人工评价"""
        query = self.query_manager.get_query(query_id)
        if not query:
            print(f"查询 ID {query_id} 不存在")
            return False
        
        print(f"\n{'='*80}")
        print(f"人工评价 - 查询 {query_id}")
        print(f"{'='*80}")
        print(f"查询文本: {query.query_text}")
        print(f"查询描述: {query.description}")
        
        # 执行搜索
        print(f"\n正在搜索...")
        results = self.search_engine.search(query.query_text, top_k=max_results)
        
        if not results:
            print("没有搜索结果")
            return False
        
        # 保存系统结果
        doc_ids = [r.doc_id for r in results]
        query.set_system_results(doc_ids)
        
        print(f"\n找到 {len(results)} 个结果，请逐一评价相关性:")
        print("评分标准:")
        print("  3 - 非常相关 (完全匹配查询意图)")
        print("  2 - 相关 (与查询有明确关联)")
        print("  1 - 部分相关 (有一定关联但不太符合)")
        print("  0 - 不相关 (与查询无关)")
        print("  s - 跳过当前结果")
        print("  q - 退出当前查询评价")
        
        evaluation_data = {
            'query_id': query_id,
            'query_text': query.query_text,
            'timestamp': time.time(),
            'results_evaluated': [],
            'relevance_judgments': {}
        }
        
        for i, result in enumerate(results):
            print(f"\n{'-'*60}")
            print(f"结果 {i+1}/{len(results)}")
            print(f"文档ID: {result.doc_id}")
            print(f"系统相似度: {result.similarity:.3f}")
            print(f"标题: {result.title}")
            print(f"URL: {result.url}")
            print(f"匹配词汇: {', '.join(result.matched_terms)}")
            print(f"内容摘要: {result.snippet}")
            
            while True:
                try:
                    score_input = input(f"\n请评价相关性 (0-3, s=跳过, q=退出): ").strip().lower()
                    
                    if score_input == 'q':
                        print("退出当前查询评价")
                        return True
                    elif score_input == 's':
                        print("跳过当前结果")
                        break
                    elif score_input in ['0', '1', '2', '3']:
                        score = int(score_input)
                        
                        # 记录评价
                        evaluation_data['results_evaluated'].append({
                            'doc_id': result.doc_id,
                            'rank': i + 1,
                            'similarity': result.similarity,
                            'relevance_score': score,
                            'title': result.title
                        })
                        evaluation_data['relevance_judgments'][str(result.doc_id)] = score
                        
                        # 更新查询的相关文档
                        if score > 0:
                            query.add_relevant_document(result.doc_id, score)
                        
                        break
                    else:
                        print("请输入有效的评分 (0-3, s, q)")
                        
                except KeyboardInterrupt:
                    print("\n\n评价被中断")
                    return True
                except Exception as e:
                    print(f"输入错误: {e}")
        
        # 保存评价结果
        self.current_evaluations[str(query_id)] = evaluation_data
        self._save_evaluation()
        
        # 显示评价总结
        self._show_evaluation_summary(evaluation_data)
        
        return True
    
    def _show_evaluation_summary(self, evaluation_data: Dict[str, Any]):
        """显示评价总结"""
        results = evaluation_data['results_evaluated']
        if not results:
            return
        
        print(f"\n{'='*60}")
        print(f"评价总结")
        print(f"{'='*60}")
        
        relevance_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        for result in results:
            score = result['relevance_score']
            relevance_counts[score] += 1
        
        print(f"已评价结果数: {len(results)}")
        print(f"相关性分布:")
        print(f"  非常相关 (3): {relevance_counts[3]} 个")
        print(f"  相关 (2): {relevance_counts[2]} 个")
        print(f"  部分相关 (1): {relevance_counts[1]} 个")
        print(f"  不相关 (0): {relevance_counts[0]} 个")
        
        relevant_count = relevance_counts[1] + relevance_counts[2] + relevance_counts[3]
        if len(results) > 0:
            precision = relevant_count / len(results)
            print(f"精确率 (Precision): {precision:.3f}")
    
    def batch_evaluate(self, query_ids: List[int] = None):
        """批量评价多个查询"""
        if query_ids is None:
            query_ids = [q.query_id for q in self.query_manager.get_all_queries()]
        
        print(f"开始批量评价 {len(query_ids)} 个查询...")
        
        completed = 0
        for query_id in query_ids:
            print(f"\n进度: {completed + 1}/{len(query_ids)}")
            
            if self.evaluate_query(query_id):
                completed += 1
            
            # 询问是否继续
            if completed < len(query_ids):
                response = input(f"\n按回车继续下一个查询，输入'q'退出批量评价: ").strip()
                if response.lower() == 'q':
                    break
        
        print(f"\n批量评价完成，共评价了 {completed} 个查询")
    
    def interactive_evaluation(self):
        """交互式评价界面"""
        self.load_or_create_queries()
        
        print(f"\n{'='*80}")
        print(f"🔍 人工评价系统")
        print(f"{'='*80}")
        print(f"可用命令:")
        print(f"  list - 显示所有测试查询")
        print(f"  eval <query_id> - 评价指定查询")
        print(f"  batch [query_ids] - 批量评价")
        print(f"  summary - 显示评价统计")
        print(f"  export - 导出评价结果")
        print(f"  help - 显示帮助")
        print(f"  quit - 退出")
        
        while True:
            try:
                command = input(f"\n📝 请输入命令: ").strip().lower()
                
                if command == 'quit':
                    print("再见！")
                    break
                
                elif command == 'list':
                    self.query_manager.display_queries()
                
                elif command.startswith('eval '):
                    try:
                        query_id = int(command.split()[1])
                        self.evaluate_query(query_id)
                    except (IndexError, ValueError):
                        print("用法: eval <query_id>")
                
                elif command == 'batch':
                    self.batch_evaluate()
                
                elif command.startswith('batch '):
                    try:
                        query_ids = [int(x) for x in command.split()[1:]]
                        self.batch_evaluate(query_ids)
                    except ValueError:
                        print("用法: batch [query_id1 query_id2 ...]")
                
                elif command == 'summary':
                    self._show_overall_summary()
                
                elif command == 'export':
                    self._export_results()
                
                elif command == 'help':
                    self._show_help()
                
                elif command:
                    print("未知命令，输入'help'查看可用命令")
                    
            except KeyboardInterrupt:
                print("\n\n程序被中断，再见！")
                break
            except Exception as e:
                print(f"发生错误: {e}")
    
    def _show_overall_summary(self):
        """显示总体评价统计"""
        if not self.current_evaluations:
            self._load_evaluation()
        
        print(f"\n{'='*60}")
        print(f"总体评价统计")
        print(f"{'='*60}")
        
        total_evaluated = len(self.current_evaluations)
        total_results = sum(len(eval_data['results_evaluated']) 
                          for eval_data in self.current_evaluations.values())
        
        all_scores = []
        for eval_data in self.current_evaluations.values():
            for result in eval_data['results_evaluated']:
                all_scores.append(result['relevance_score'])
        
        if all_scores:
            relevance_dist = {0: 0, 1: 0, 2: 0, 3: 0}
            for score in all_scores:
                relevance_dist[score] += 1
            
            print(f"已评价查询数: {total_evaluated}")
            print(f"已评价结果总数: {total_results}")
            print(f"平均每查询评价结果数: {total_results/total_evaluated:.1f}")
            print(f"\n相关性分布:")
            for score, count in relevance_dist.items():
                pct = count / len(all_scores) * 100
                print(f"  评分 {score}: {count} 个 ({pct:.1f}%)")
            
            relevant_count = sum(relevance_dist[i] for i in [1, 2, 3])
            overall_precision = relevant_count / len(all_scores)
            print(f"\n总体精确率: {overall_precision:.3f}")
        else:
            print("暂无评价数据")
    
    def _export_results(self):
        """导出评价结果"""
        if not self.current_evaluations:
            self._load_evaluation()
        
        export_file = "results/evaluation_export.json"
        os.makedirs(os.path.dirname(export_file), exist_ok=True)
        
        export_data = {
            'timestamp': time.time(),
            'total_queries_evaluated': len(self.current_evaluations),
            'evaluations': self.current_evaluations,
            'summary': self._calculate_summary_stats()
        }
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"评价结果已导出到: {export_file}")
    
    def _calculate_summary_stats(self) -> Dict[str, Any]:
        """计算总结统计"""
        if not self.current_evaluations:
            return {}
        
        all_scores = []
        query_precisions = []
        
        for eval_data in self.current_evaluations.values():
            scores = [r['relevance_score'] for r in eval_data['results_evaluated']]
            all_scores.extend(scores)
            
            if scores:
                relevant = sum(1 for s in scores if s > 0)
                precision = relevant / len(scores)
                query_precisions.append(precision)
        
        if all_scores:
            return {
                'total_results_evaluated': len(all_scores),
                'overall_precision': sum(1 for s in all_scores if s > 0) / len(all_scores),
                'average_query_precision': sum(query_precisions) / len(query_precisions),
                'relevance_distribution': {
                    str(i): all_scores.count(i) for i in range(4)
                }
            }
        return {}
    
    def _save_evaluation(self):
        """保存评价结果"""
        os.makedirs(os.path.dirname(self.evaluation_file), exist_ok=True)
        
        # 保存评价结果到manual_evaluation.json
        with open(self.evaluation_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_evaluations, f, indent=2, ensure_ascii=False)
        
        # 更新test_queries.json
        self.query_manager.save_queries()
        
        print("评价结果已保存")
    
    def _load_evaluation(self):
        """加载评价结果"""
        if os.path.exists(self.evaluation_file):
            try:
                with open(self.evaluation_file, 'r', encoding='utf-8') as f:
                    self.current_evaluations = json.load(f)
                print(f"加载了 {len(self.current_evaluations)} 个查询的评价结果")
            except Exception as e:
                print(f"加载评价文件时出错: {e}")
    
    def _show_help(self):
        """显示帮助信息"""
        print(f"\n{'='*60}")
        print(f"人工评价系统帮助")
        print(f"{'='*60}")
        print(f"命令说明:")
        print(f"  list - 显示所有可评价的测试查询")
        print(f"  eval <query_id> - 对指定ID的查询进行评价")
        print(f"  batch - 对所有查询进行批量评价")
        print(f"  batch <id1 id2...> - 对指定查询进行批量评价")
        print(f"  summary - 显示当前评价统计信息")
        print(f"  export - 将评价结果导出为JSON文件")
        print(f"  help - 显示此帮助信息")
        print(f"  quit - 退出评价系统")
        print(f"\n评价时的评分标准:")
        print(f"  3 - 非常相关: 完全符合查询意图")
        print(f"  2 - 相关: 与查询有明确关联")
        print(f"  1 - 部分相关: 有一定关联但不太符合")
        print(f"  0 - 不相关: 与查询完全无关")


# 测试代码
if __name__ == "__main__":
    print("=== 人工评价工具测试 ===")
    print("注意：这个测试需要完整的搜索引擎")
    print("请运行完整的评价系统：")
    print("python src/evaluation/manual_evaluation.py")