import math
from typing import List, Dict, Tuple, Any
import numpy as np

class EvaluationMetrics:
    """评价指标计算器：计算各种信息检索评价指标"""
    
    def __init__(self):
        pass
    
    def precision_at_k(self, relevant_docs: List[int], retrieved_docs: List[int], k: int) -> float:
        """计算Precision@K：前K个结果中相关文档的比例"""
        if k <= 0 or not retrieved_docs:
            return 0.0
        
        top_k_docs = retrieved_docs[:k]
        relevant_in_top_k = len(set(top_k_docs) & set(relevant_docs))
        
        return relevant_in_top_k / len(top_k_docs)
    
    def recall_at_k(self, relevant_docs: List[int], retrieved_docs: List[int], k: int) -> float:
        """计算Recall@K：前K个结果中找到的相关文档占总相关文档的比例"""
        if not relevant_docs or k <= 0:
            return 0.0
        
        top_k_docs = retrieved_docs[:k]
        relevant_in_top_k = len(set(top_k_docs) & set(relevant_docs))
        
        return relevant_in_top_k / len(relevant_docs)
    
    def f1_score_at_k(self, relevant_docs: List[int], retrieved_docs: List[int], k: int) -> float:
        """计算F1-Score@K：Precision和Recall的调和平均"""
        precision = self.precision_at_k(relevant_docs, retrieved_docs, k)
        recall = self.recall_at_k(relevant_docs, retrieved_docs, k)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
    def average_precision(self, relevant_docs: List[int], retrieved_docs: List[int]) -> float:
        """计算Average Precision (AP)：所有相关文档位置的精确率平均值"""
        if not relevant_docs or not retrieved_docs:
            return 0.0
        
        relevant_set = set(relevant_docs)
        num_relevant_found = 0
        precision_sum = 0.0
        
        for i, doc_id in enumerate(retrieved_docs):
            if doc_id in relevant_set:
                num_relevant_found += 1
                precision_at_i = num_relevant_found / (i + 1)
                precision_sum += precision_at_i
        
        if num_relevant_found == 0:
            return 0.0
        
        return precision_sum / len(relevant_docs)
    
    def mean_average_precision(self, queries_results: List[Tuple[List[int], List[int]]]) -> float:
        """计算Mean Average Precision (MAP)：多个查询的AP平均值"""
        if not queries_results:
            return 0.0
        
        ap_scores = []
        for relevant_docs, retrieved_docs in queries_results:
            ap = self.average_precision(relevant_docs, retrieved_docs)
            ap_scores.append(ap)
        
        return sum(ap_scores) / len(ap_scores)
    
    def dcg_at_k(self, relevance_scores: List[int], k: int) -> float:
        """计算Discounted Cumulative Gain@K"""
        if k <= 0 or not relevance_scores:
            return 0.0
        
        dcg = 0.0
        for i in range(min(k, len(relevance_scores))):
            if i == 0:
                dcg += relevance_scores[i]
            else:
                dcg += relevance_scores[i] / math.log2(i + 1)
        
        return dcg
    
    def ndcg_at_k(self, relevance_scores: List[int], k: int) -> float:
        """计算Normalized Discounted Cumulative Gain@K"""
        if k <= 0 or not relevance_scores:
            return 0.0
        
        # 计算DCG@K
        dcg = self.dcg_at_k(relevance_scores, k)
        
        # 计算IDCG@K (理想情况下的DCG)
        ideal_relevance = sorted(relevance_scores, reverse=True)
        idcg = self.dcg_at_k(ideal_relevance, k)
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def reciprocal_rank(self, relevant_docs: List[int], retrieved_docs: List[int]) -> float:
        """计算Reciprocal Rank：第一个相关文档的倒数排名"""
        if not relevant_docs or not retrieved_docs:
            return 0.0
        
        relevant_set = set(relevant_docs)
        
        for i, doc_id in enumerate(retrieved_docs):
            if doc_id in relevant_set:
                return 1.0 / (i + 1)
        
        return 0.0
    
    def mean_reciprocal_rank(self, queries_results: List[Tuple[List[int], List[int]]]) -> float:
        """计算Mean Reciprocal Rank (MRR)：多个查询的RR平均值"""
        if not queries_results:
            return 0.0
        
        rr_scores = []
        for relevant_docs, retrieved_docs in queries_results:
            rr = self.reciprocal_rank(relevant_docs, retrieved_docs)
            rr_scores.append(rr)
        
        return sum(rr_scores) / len(rr_scores)
    
    def rank_biased_precision(self, relevant_docs: List[int], retrieved_docs: List[int], 
                            p: float = 0.8) -> float:
        """计算Rank-Biased Precision (RBP)：考虑用户持续性的评价指标"""
        if not relevant_docs or not retrieved_docs:
            return 0.0
        
        relevant_set = set(relevant_docs)
        rbp = 0.0
        
        for i, doc_id in enumerate(retrieved_docs):
            if doc_id in relevant_set:
                rbp += (p ** i)
        
        return (1 - p) * rbp
    
    def calculate_all_metrics(self, relevant_docs: List[int], retrieved_docs: List[int], 
                            relevance_scores: List[int] = None, k_values: List[int] = None) -> Dict[str, Any]:
        """计算所有评价指标"""
        if k_values is None:
            k_values = [1, 3, 5, 10]
        
        if relevance_scores is None:
            # 如果没有提供相关度评分，假设所有相关文档的评分为1
            relevance_scores = []
            relevant_set = set(relevant_docs)
            for doc_id in retrieved_docs:
                if doc_id in relevant_set:
                    relevance_scores.append(1)
                else:
                    relevance_scores.append(0)
        
        metrics = {}
        
        # 计算不同k值下的指标
        for k in k_values:
            metrics[f'Precision@{k}'] = self.precision_at_k(relevant_docs, retrieved_docs, k)
            metrics[f'Recall@{k}'] = self.recall_at_k(relevant_docs, retrieved_docs, k)
            metrics[f'F1@{k}'] = self.f1_score_at_k(relevant_docs, retrieved_docs, k)
            metrics[f'NDCG@{k}'] = self.ndcg_at_k(relevance_scores, k)
        
        # 计算其他指标
        metrics['Average_Precision'] = self.average_precision(relevant_docs, retrieved_docs)
        metrics['Reciprocal_Rank'] = self.reciprocal_rank(relevant_docs, retrieved_docs)
        metrics['RBP'] = self.rank_biased_precision(relevant_docs, retrieved_docs)
        
        return metrics
    
    def compare_systems(self, system1_results: List[Tuple[List[int], List[int]]], 
                       system2_results: List[Tuple[List[int], List[int]]]) -> Dict[str, Any]:
        """比较两个检索系统的性能"""
        metrics1 = self._calculate_system_metrics(system1_results)
        metrics2 = self._calculate_system_metrics(system2_results)
        
        comparison = {}
        for metric in metrics1:
            diff = metrics2[metric] - metrics1[metric]
            improvement = (diff / metrics1[metric] * 100) if metrics1[metric] > 0 else 0
            
            comparison[metric] = {
                'system1': metrics1[metric],
                'system2': metrics2[metric],
                'difference': diff,
                'improvement_pct': improvement
            }
        
        return comparison
    
    def _calculate_system_metrics(self, results: List[Tuple[List[int], List[int]]]) -> Dict[str, float]:
        """计算系统级别的评价指标"""
        if not results:
            return {}
        
        # 计算各查询的指标
        all_metrics = []
        for relevant_docs, retrieved_docs in results:
            query_metrics = self.calculate_all_metrics(relevant_docs, retrieved_docs)
            all_metrics.append(query_metrics)
        
        # 计算平均值
        system_metrics = {}
        for metric in all_metrics[0]:
            values = [m[metric] for m in all_metrics]
            system_metrics[metric] = sum(values) / len(values)
        
        # 添加MAP和MRR
        system_metrics['MAP'] = self.mean_average_precision(results)
        system_metrics['MRR'] = self.mean_reciprocal_rank(results)
        
        return system_metrics
    
    def statistical_significance_test(self, scores1: List[float], scores2: List[float]) -> Dict[str, Any]:
        """简单的统计显著性测试（配对t检验）"""
        if len(scores1) != len(scores2) or len(scores1) < 2:
            return {"error": "样本大小不足或不匹配"}
        
        # 计算差值
        differences = [s2 - s1 for s1, s2 in zip(scores1, scores2)]
        n = len(differences)
        
        # 计算均值和标准差
        mean_diff = sum(differences) / n
        variance = sum((d - mean_diff) ** 2 for d in differences) / (n - 1)
        std_dev = math.sqrt(variance)
        
        # 计算t统计量
        if std_dev == 0:
            return {"mean_difference": mean_diff, "significant": False, "note": "标准差为零"}
        
        t_stat = mean_diff / (std_dev / math.sqrt(n))
        
        # 简单的显著性判断 (|t| > 2 大致对应 p < 0.05)
        significant = abs(t_stat) > 2.0
        
        return {
            "mean_difference": mean_diff,
            "t_statistic": t_stat,
            "significant": significant,
            "sample_size": n,
            "std_dev": std_dev
        }


class EvaluationReport:
    """评价报告生成器：生成详细的评价报告"""
    
    def __init__(self):
        self.metrics_calculator = EvaluationMetrics()
    
    def generate_query_report(self, query_id: int, query_text: str, 
                            relevant_docs: List[int], retrieved_docs: List[int],
                            relevance_scores: List[int] = None) -> Dict[str, Any]:
        """生成单个查询的评价报告"""
        metrics = self.metrics_calculator.calculate_all_metrics(
            relevant_docs, retrieved_docs, relevance_scores
        )
        
        # 计算基本统计
        total_relevant = len(relevant_docs)
        total_retrieved = len(retrieved_docs)
        relevant_retrieved = len(set(relevant_docs) & set(retrieved_docs))
        
        report = {
            'query_info': {
                'query_id': query_id,
                'query_text': query_text,
                'total_relevant_docs': total_relevant,
                'total_retrieved_docs': total_retrieved,
                'relevant_retrieved_docs': relevant_retrieved
            },
            'metrics': metrics,
            'analysis': {
                'overall_precision': relevant_retrieved / total_retrieved if total_retrieved > 0 else 0,
                'overall_recall': relevant_retrieved / total_relevant if total_relevant > 0 else 0,
                'coverage': relevant_retrieved / total_relevant if total_relevant > 0 else 0
            }
        }
        
        return report
    
    def generate_system_report(self, queries_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成系统级别的评价报告"""
        if not queries_data:
            return {}
        
        # 准备数据
        results = [(qd['relevant_docs'], qd['retrieved_docs']) for qd in queries_data]
        system_metrics = self.metrics_calculator._calculate_system_metrics(results)
        
        # 计算分布统计
        query_metrics = []
        for qd in queries_data:
            metrics = self.metrics_calculator.calculate_all_metrics(
                qd['relevant_docs'], qd['retrieved_docs']
            )
            query_metrics.append(metrics)
        
        # 计算指标分布
        metric_distributions = {}
        for metric in query_metrics[0]:
            values = [qm[metric] for qm in query_metrics]
            metric_distributions[metric] = {
                'mean': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'std': self._calculate_std(values)
            }
        
        report = {
            'system_summary': {
                'total_queries': len(queries_data),
                'total_relevant_docs': sum(len(qd['relevant_docs']) for qd in queries_data),
                'total_retrieved_docs': sum(len(qd['retrieved_docs']) for qd in queries_data),
                'avg_relevant_per_query': sum(len(qd['relevant_docs']) for qd in queries_data) / len(queries_data),
                'avg_retrieved_per_query': sum(len(qd['retrieved_docs']) for qd in queries_data) / len(queries_data)
            },
            'system_metrics': system_metrics,
            'metric_distributions': metric_distributions,
            'per_query_metrics': query_metrics
        }
        
        return report
    
    def _calculate_std(self, values: List[float]) -> float:
        """计算标准差"""
        if len(values) <= 1:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)
    
    def format_report(self, report: Dict[str, Any], report_type: str = "system") -> str:
        """格式化报告为可读文本"""
        if report_type == "query":
            return self._format_query_report(report)
        elif report_type == "system":
            return self._format_system_report(report)
        else:
            return str(report)
    
    def _format_query_report(self, report: Dict[str, Any]) -> str:
        """格式化查询报告"""
        lines = []
        lines.append("=" * 80)
        lines.append(f"查询评价报告")
        lines.append("=" * 80)
        
        info = report['query_info']
        lines.append(f"查询ID: {info['query_id']}")
        lines.append(f"查询文本: {info['query_text']}")
        lines.append(f"相关文档数: {info['total_relevant_docs']}")
        lines.append(f"检索文档数: {info['total_retrieved_docs']}")
        lines.append(f"相关且检索到的文档数: {info['relevant_retrieved_docs']}")
        
        lines.append(f"\n主要指标:")
        lines.append("-" * 40)
        metrics = report['metrics']
        for metric, value in metrics.items():
            lines.append(f"{metric}: {value:.3f}")
        
        return "\n".join(lines)
    
    def _format_system_report(self, report: Dict[str, Any]) -> str:
        """格式化系统报告"""
        lines = []
        lines.append("=" * 80)
        lines.append(f"系统评价报告")
        lines.append("=" * 80)
        
        summary = report['system_summary']
        lines.append(f"总查询数: {summary['total_queries']}")
        lines.append(f"总相关文档数: {summary['total_relevant_docs']}")
        lines.append(f"总检索文档数: {summary['total_retrieved_docs']}")
        lines.append(f"平均每查询相关文档数: {summary['avg_relevant_per_query']:.1f}")
        lines.append(f"平均每查询检索文档数: {summary['avg_retrieved_per_query']:.1f}")
        
        lines.append(f"\n系统平均指标:")
        lines.append("-" * 40)
        for metric, value in report['system_metrics'].items():
            lines.append(f"{metric}: {value:.3f}")
        
        return "\n".join(lines)


# 测试代码
if __name__ == "__main__":
    # 测试评价指标计算器
    print("=== 评价指标测试 ===")
    
    metrics_calc = EvaluationMetrics()
    
    # 测试数据
    relevant_docs = [1, 3, 5, 7, 9]  # 相关文档
    retrieved_docs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # 检索结果
    relevance_scores = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]  # 相关度评分
    
    print(f"相关文档: {relevant_docs}")
    print(f"检索结果: {retrieved_docs}")
    print(f"相关度评分: {relevance_scores}")
    
    # 计算所有指标
    all_metrics = metrics_calc.calculate_all_metrics(
        relevant_docs, retrieved_docs, relevance_scores
    )
    
    print(f"\n=== 评价指标结果 ===")
    for metric, value in all_metrics.items():
        print(f"{metric}: {value:.3f}")
    
    # 测试报告生成
    print(f"\n=== 报告生成测试 ===")
    report_gen = EvaluationReport()
    
    query_report = report_gen.generate_query_report(
        1, "test query", relevant_docs, retrieved_docs, relevance_scores
    )
    
    formatted_report = report_gen.format_report(query_report, "query")
    print(formatted_report)