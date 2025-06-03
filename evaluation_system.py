#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NPR文章信息检索系统 - 评价系统
包含人工评价工具和自动评价指标计算

作者: [你的姓名]
日期: 2025-05-30
"""

import sys
import os
sys.path.append('src')

from src.retrieval.search_engine import EnhancedSearchEngine
from src.evaluation.manual_evaluation import ManualEvaluator
from src.evaluation.evaluation_metrics import EvaluationMetrics, EvaluationReport
from src.evaluation.test_queries import TestQueryManager
import argparse
import json

class EvaluationSystem:
    """完整的评价系统：整合人工评价和自动指标计算"""
    
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.search_engine = None
        self.manual_evaluator = None
        self.metrics_calculator = EvaluationMetrics()
        self.report_generator = EvaluationReport()
        self.query_manager = TestQueryManager()
    
    def initialize(self) -> bool:
        """初始化评价系统"""
        print("🔧 初始化评价系统...")
        
        # 检查数据文件
        if not os.path.exists(self.data_file):
            print(f"❌ 数据文件不存在: {self.data_file}")
            return False
        
        # 初始化搜索引擎
        self.search_engine = EnhancedSearchEngine(self.data_file)
        if not self.search_engine.initialize():
            print("❌ 搜索引擎初始化失败")
            return False
        
        # 加载或创建测试查询
        print("正在加载测试查询...")
        if not self.query_manager.load_queries():
            print("创建默认测试查询集合...")
            self.query_manager.create_default_queries()
            self.query_manager.save_queries()
        
        # 显示加载的查询数量
        queries = self.query_manager.get_all_queries()
        print(f"已加载 {len(queries)} 个测试查询")
        for query in queries:
            print(f"查询 {query.query_id}: {query.query_text}")
        
        # 初始化人工评价器，传入查询管理器
        self.manual_evaluator = ManualEvaluator(self.search_engine, self.query_manager)
        
        print("✅ 评价系统初始化成功！")
        return True
    
    def run_manual_evaluation(self):
        """运行人工评估"""
        print("\n=== 人工评估模式 ===")
        print("输入 'help' 查看可用命令")
        
        while True:
            try:
                command = input("\n请输入命令: ").strip()
                
                if command == "help":
                    print("\n可用命令:")
                    print("  list - 显示所有测试查询")
                    print("  eval <query_id> - 评估指定查询")
                    print("  batch [query_ids] - 批量评估多个查询")
                    print("  summary - 显示评估摘要")
                    print("  add <query_text> [description] - 添加自定义查询")
                    print("  quit - 退出评估")
                
                elif command == "list":
                    self.query_manager.display_queries()
                
                elif command.startswith("eval "):
                    try:
                        query_id = int(command.split()[1])
                        self.manual_evaluator.evaluate_query(query_id)
                    except (IndexError, ValueError):
                        print("错误: 请提供有效的查询ID")
                
                elif command.startswith("batch "):
                    try:
                        query_ids = [int(id) for id in command.split()[1:]]
                        self.manual_evaluator.batch_evaluate(query_ids)
                    except (IndexError, ValueError):
                        print("错误: 请提供有效的查询ID列表")
                
                elif command == "summary":
                    self.manual_evaluator.show_summary()
                
                elif command.startswith("add "):
                    try:
                        # 解析命令参数
                        parts = command[4:].strip()
                        # 查找第一个空格作为查询文本和描述的分隔符
                        first_space = parts.find(" ")
                        if first_space == -1:
                            # 如果没有空格，整个文本都是查询
                            query_text = parts
                            description = ""
                        else:
                            # 分割查询文本和描述
                            query_text = parts[:first_space]
                            description = parts[first_space:].strip()
                        
                        # 添加新查询
                        query = self.query_manager.add_custom_query(query_text, description)
                        
                        # 立即评估新添加的查询
                        print("\n是否立即评估这个新查询？(y/n)")
                        if input().lower() == 'y':
                            self.manual_evaluator.evaluate_query(query.query_id)
                            
                    except Exception as e:
                        print(f"错误: 添加查询失败 - {str(e)}")
                
                elif command == "quit":
                    break
                
                else:
                    print("未知命令，输入 'help' 查看可用命令")
                    
            except KeyboardInterrupt:
                print("\n评估已中断")
                break
            except Exception as e:
                print(f"错误: {str(e)}")
    
    def calculate_system_metrics(self, evaluation_file: str = "results/manual_evaluation.json"):
        """计算系统评价指标"""
        print("📊 计算系统评价指标...")
        
        if not os.path.exists(evaluation_file):
            print(f"❌ 评价文件不存在: {evaluation_file}")
            print("请先进行人工评价")
            return
        
        try:
            # 加载评价数据
            with open(evaluation_file, 'r', encoding='utf-8') as f:
                evaluations = json.load(f)
            
            if not evaluations:
                print("❌ 没有找到评价数据")
                return
            
            # 准备查询数据
            queries_data = []
            for query_id, eval_data in evaluations.items():
                # 提取相关文档和检索结果
                relevant_docs = []
                retrieved_docs = []
                relevance_scores = []
                
                for result in eval_data.get('results_evaluated', []):
                    doc_id = result['doc_id']
                    relevance = result['relevance_score']
                    
                    retrieved_docs.append(doc_id)
                    relevance_scores.append(relevance)
                    
                    if relevance > 0:  # 相关文档（评分>0）
                        relevant_docs.append(doc_id)
                
                if retrieved_docs:  # 只包含有结果的查询
                    queries_data.append({
                        'query_id': int(query_id),
                        'query_text': eval_data['query_text'],
                        'relevant_docs': relevant_docs,
                        'retrieved_docs': retrieved_docs,
                        'relevance_scores': relevance_scores
                    })
            
            if not queries_data:
                print("❌ 没有有效的评价数据")
                return
            
            print(f"📈 分析 {len(queries_data)} 个查询的评价结果...")
            
            # 生成系统报告
            system_report = self.report_generator.generate_system_report(queries_data)
            
            # 显示报告
            formatted_report = self.report_generator.format_report(system_report, "system")
            print("\n" + formatted_report)
            
            # 生成详细的每查询报告
            print(f"\n{'='*80}")
            print(f"详细查询分析")
            print(f"{'='*80}")
            
            for qd in queries_data:
                query_report = self.report_generator.generate_query_report(
                    qd['query_id'], qd['query_text'], 
                    qd['relevant_docs'], qd['retrieved_docs'],
                    qd['relevance_scores']
                )
                
                print(f"\n查询 {qd['query_id']}: '{qd['query_text']}'")
                print(f"相关文档: {len(qd['relevant_docs'])}, 检索文档: {len(qd['retrieved_docs'])}")
                
                metrics = query_report['metrics']
                key_metrics = ['Precision@5', 'Recall@5', 'F1@5', 'NDCG@5', 'Average_Precision']
                for metric in key_metrics:
                    if metric in metrics:
                        print(f"  {metric}: {metrics[metric]:.3f}")
            
            # 保存详细报告
            report_file = "results/evaluation_report.json"
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            
            full_report = {
                'system_report': system_report,
                'query_reports': [
                    self.report_generator.generate_query_report(
                        qd['query_id'], qd['query_text'], 
                        qd['relevant_docs'], qd['retrieved_docs'],
                        qd['relevance_scores']
                    ) for qd in queries_data
                ]
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(full_report, f, indent=2, ensure_ascii=False)
            
            print(f"\n📋 详细报告已保存到: {report_file}")
            
        except Exception as e:
            print(f"❌ 计算指标时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def demo_evaluation(self):
        """演示评价功能"""
        print("🎯 演示评价功能...")
        
        # 创建一些示例评价数据
        demo_queries = [
            {
                'query_id': 1,
                'query_text': 'climate change',
                'relevant_docs': [0, 2, 5],
                'retrieved_docs': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                'relevance_scores': [3, 0, 2, 0, 0, 1, 0, 0, 0, 0]
            },
            {
                'query_id': 2,
                'query_text': 'health care',
                'relevant_docs': [1, 3, 7],
                'retrieved_docs': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                'relevance_scores': [0, 2, 0, 3, 0, 0, 0, 1, 0, 0]
            }
        ]
        
        print(f"📊 使用示例数据计算评价指标...")
        
        for qd in demo_queries:
            print(f"\n查询: '{qd['query_text']}'")
            
            # 计算指标
            metrics = self.metrics_calculator.calculate_all_metrics(
                qd['relevant_docs'], qd['retrieved_docs'], qd['relevance_scores']
            )
            
            # 显示关键指标
            key_metrics = ['Precision@5', 'Recall@5', 'F1@5', 'NDCG@5', 'Average_Precision']
            for metric in key_metrics:
                if metric in metrics:
                    print(f"  {metric}: {metrics[metric]:.3f}")
        
        # 计算系统级指标
        results = [(qd['relevant_docs'], qd['retrieved_docs']) for qd in demo_queries]
        map_score = self.metrics_calculator.mean_average_precision(results)
        mrr_score = self.metrics_calculator.mean_reciprocal_rank(results)
        
        print(f"\n系统级指标:")
        print(f"  MAP (Mean Average Precision): {map_score:.3f}")
        print(f"  MRR (Mean Reciprocal Rank): {mrr_score:.3f}")
    
    def interactive_menu(self):
        """交互式菜单"""
        while True:
            print(f"\n{'='*60}")
            print(f"🔍 NPR检索系统评价工具")
            print(f"{'='*60}")
            print(f"1. 运行人工评价")
            print(f"2. 计算系统评价指标")
            print(f"3. 演示评价功能")
            print(f"4. 查看系统信息")
            print(f"5. 退出")
            
            try:
                choice = input(f"\n请选择功能 (1-5): ").strip()
                
                if choice == '1':
                    self.run_manual_evaluation()
                
                elif choice == '2':
                    self.calculate_system_metrics()
                
                elif choice == '3':
                    self.demo_evaluation()
                
                elif choice == '4':
                    if self.search_engine:
                        info = self.search_engine.get_system_info()
                        print(f"\n📋 系统信息:")
                        for key, value in info.items():
                            if isinstance(value, dict):
                                print(f"{key}:")
                                for k, v in value.items():
                                    print(f"  {k}: {v}")
                            else:
                                print(f"{key}: {value}")
                
                elif choice == '5':
                    print("👋 再见！")
                    break
                
                else:
                    print("❌ 无效选择，请输入1-5")
                    
            except KeyboardInterrupt:
                print("\n\n👋 程序被中断，再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="NPR检索系统评价工具")
    parser.add_argument("--mode", choices=['manual', 'metrics', 'demo'], 
                       help="运行模式: manual=人工评价, metrics=计算指标, demo=演示")
    parser.add_argument("--eval-file", default="results/manual_evaluation.json",
                       help="评价结果文件路径")
    
    args = parser.parse_args()
    
    # 数据文件路径
    data_file = "data/npr_articles.json"
    
    # 创建评价系统
    eval_system = EvaluationSystem(data_file)
    
    if not eval_system.initialize():
        print("❌ 评价系统初始化失败")
        return
    
    try:
        if args.mode == 'manual':
            eval_system.run_manual_evaluation()
        elif args.mode == 'metrics':
            eval_system.calculate_system_metrics(args.eval_file)
        elif args.mode == 'demo':
            eval_system.demo_evaluation()
        else:
            # 默认交互模式
            eval_system.interactive_menu()
    
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断，再见！")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()