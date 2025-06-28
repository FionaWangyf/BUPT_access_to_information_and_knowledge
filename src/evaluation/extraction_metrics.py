#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息抽取评价指标计算器
文件位置：src/evaluation/extraction_metrics.py
"""

from typing import Dict, List, Any, Tuple
from collections import defaultdict
import statistics


class ExtractionMetrics:
    """信息抽取评价指标计算器"""

    def __init__(self):
        self.entity_types = ['PERSON', 'LOCATION', 'ORGANIZATION', 'TIME', 'MONEY', 'CONTACT', 'QUOTE']

    def calculate_overall_metrics(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算总体评价指标"""

        # 收集所有评价数据
        all_correct = 0
        all_incorrect = 0
        all_missed = 0
        all_extracted = 0

        by_type_stats = defaultdict(lambda: {
            'correct': 0, 'incorrect': 0, 'missed': 0, 'extracted': 0
        })

        confidence_scores = []
        confidence_correct = []
        confidence_incorrect = []

        for doc_id, doc_data in evaluation_data.items():
            # 处理评价过的实体
            for entity in doc_data.get('evaluated_entities', []):
                entity_type = entity['entity_type']
                confidence = entity['confidence']
                evaluation = entity['human_evaluation']

                all_extracted += 1
                by_type_stats[entity_type]['extracted'] += 1
                confidence_scores.append(confidence)

                if evaluation == 'correct':
                    all_correct += 1
                    by_type_stats[entity_type]['correct'] += 1
                    confidence_correct.append(confidence)
                elif evaluation == 'incorrect':
                    all_incorrect += 1
                    by_type_stats[entity_type]['incorrect'] += 1
                    confidence_incorrect.append(confidence)

            # 处理遗漏的实体
            for missed_entity in doc_data.get('missed_entities', []):
                entity_type = missed_entity['entity_type']
                all_missed += 1
                by_type_stats[entity_type]['missed'] += 1

        # 计算总体指标
        overall_metrics = self._calculate_prf_metrics(all_correct, all_incorrect, all_missed)
        overall_metrics.update({
            'total_extracted': all_extracted,
            'correct_entities': all_correct,
            'incorrect_entities': all_incorrect,
            'missed_entities': all_missed,
            'evaluated_documents': len(evaluation_data)
        })

        # 计算各类型指标
        by_type_metrics = {}
        for entity_type, stats in by_type_stats.items():
            type_metrics = self._calculate_prf_metrics(
                stats['correct'], stats['incorrect'], stats['missed']
            )
            type_metrics.update({
                'extracted_count': stats['extracted'],
                'correct_count': stats['correct'],
                'incorrect_count': stats['incorrect'],
                'missed_count': stats['missed']
            })
            by_type_metrics[entity_type] = type_metrics

        # 置信度分析
        confidence_analysis = self._analyze_confidence(
            confidence_scores, confidence_correct, confidence_incorrect
        )

        # 错误分析
        error_analysis = self._analyze_errors(evaluation_data)

        return {
            'overall': overall_metrics,
            'by_type': by_type_metrics,
            'confidence_analysis': confidence_analysis,
            'error_analysis': error_analysis
        }

    def _calculate_prf_metrics(self, correct: int, incorrect: int, missed: int) -> Dict[str, float]:
        """计算精确率、召回率、F1分数"""

        # 计算精确率 = 正确抽取的实体数 / 总抽取实体数
        total_extracted = correct + incorrect
        precision = correct / total_extracted if total_extracted > 0 else 0.0

        # 计算召回率 = 正确抽取的实体数 / (正确抽取的实体数 + 遗漏的实体数)
        total_should_extract = correct + missed
        recall = correct / total_should_extract if total_should_extract > 0 else 0.0

        # 计算F1分数 = 2 * (精确率 * 召回率) / (精确率 + 召回率)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        }

    def _analyze_confidence(self, all_scores: List[float],
                            correct_scores: List[float],
                            incorrect_scores: List[float]) -> Dict[str, Any]:
        """分析置信度分布"""

        if not all_scores:
            return {}

        analysis = {
            'average_confidence': statistics.mean(all_scores),
            'median_confidence': statistics.median(all_scores),
            'min_confidence': min(all_scores),
            'max_confidence': max(all_scores)
        }

        if correct_scores:
            analysis['average_confidence_correct'] = statistics.mean(correct_scores)

        if incorrect_scores:
            analysis['average_confidence_incorrect'] = statistics.mean(incorrect_scores)

        # 置信度区间分析
        high_conf = [s for s in all_scores if s > 0.8]
        medium_conf = [s for s in all_scores if 0.5 <= s <= 0.8]
        low_conf = [s for s in all_scores if s < 0.5]

        analysis.update({
            'high_confidence_count': len(high_conf),
            'medium_confidence_count': len(medium_conf),
            'low_confidence_count': len(low_conf),
            'high_confidence_ratio': len(high_conf) / len(all_scores),
            'medium_confidence_ratio': len(medium_conf) / len(all_scores),
            'low_confidence_ratio': len(low_conf) / len(all_scores)
        })

        return analysis

    def _analyze_errors(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析错误类型和模式"""

        error_types = defaultdict(int)
        error_examples = defaultdict(list)
        missed_by_type = defaultdict(int)

        for doc_id, doc_data in evaluation_data.items():
            # 分析错误的抽取
            for entity in doc_data.get('evaluated_entities', []):
                if entity['human_evaluation'] == 'incorrect':
                    entity_type = entity['entity_type']
                    error_types[entity_type] += 1

                    error_info = {
                        'entity_value': entity['entity_value'],
                        'confidence': entity['confidence'],
                        'context': entity.get('context', ''),
                        'notes': entity.get('evaluation_notes', ''),
                        'doc_id': doc_id
                    }
                    error_examples[entity_type].append(error_info)

            # 分析遗漏的实体
            for missed_entity in doc_data.get('missed_entities', []):
                entity_type = missed_entity['entity_type']
                missed_by_type[entity_type] += 1

        return {
            'error_count_by_type': dict(error_types),
            'missed_count_by_type': dict(missed_by_type),
            'error_examples': dict(error_examples),
            'total_errors': sum(error_types.values()),
            'total_missed': sum(missed_by_type.values())
        }

    def generate_performance_summary(self, metrics: Dict[str, Any]) -> str:
        """生成性能摘要报告"""

        overall = metrics.get('overall', {})
        by_type = metrics.get('by_type', {})
        confidence = metrics.get('confidence_analysis', {})
        errors = metrics.get('error_analysis', {})

        summary = []
        summary.append("=" * 60)
        summary.append("信息抽取系统性能评价报告")
        summary.append("=" * 60)

        # 总体性能
        summary.append(f"\n🎯 总体性能:")
        summary.append(f"  精确率: {overall.get('precision', 0):.1%}")
        summary.append(f"  召回率: {overall.get('recall', 0):.1%}")
        summary.append(f"  F1分数: {overall.get('f1_score', 0):.1%}")
        summary.append(f"  评价文档数: {overall.get('evaluated_documents', 0)}")
        summary.append(f"  抽取实体总数: {overall.get('total_extracted', 0)}")
        summary.append(f"  正确实体数: {overall.get('correct_entities', 0)}")
        summary.append(f"  错误实体数: {overall.get('incorrect_entities', 0)}")
        summary.append(f"  遗漏实体数: {overall.get('missed_entities', 0)}")

        # 各类型性能
        if by_type:
            summary.append(f"\n📊 各实体类型性能:")
            summary.append(f"{'类型':<12} {'精确率':<8} {'召回率':<8} {'F1分数':<8}")
            summary.append("-" * 50)

            for entity_type, type_metrics in by_type.items():
                precision = type_metrics.get('precision', 0)
                recall = type_metrics.get('recall', 0)
                f1 = type_metrics.get('f1_score', 0)
                summary.append(f"{entity_type:<12} {precision:<8.1%} {recall:<8.1%} {f1:<8.1%}")

        # 置信度分析
        if confidence:
            summary.append(f"\n🎚️ 置信度分析:")
            summary.append(f"  平均置信度: {confidence.get('average_confidence', 0):.3f}")
            summary.append(f"  高置信度实体比例 (>0.8): {confidence.get('high_confidence_ratio', 0):.1%}")
            summary.append(f"  中置信度实体比例 (0.5-0.8): {confidence.get('medium_confidence_ratio', 0):.1%}")
            summary.append(f"  低置信度实体比例 (<0.5): {confidence.get('low_confidence_ratio', 0):.1%}")

            if 'average_confidence_correct' in confidence and 'average_confidence_incorrect' in confidence:
                summary.append(f"  正确实体平均置信度: {confidence['average_confidence_correct']:.3f}")
                summary.append(f"  错误实体平均置信度: {confidence['average_confidence_incorrect']:.3f}")

        # 错误分析
        if errors:
            summary.append(f"\n❌ 错误分析:")
            summary.append(f"  总错误数: {errors.get('total_errors', 0)}")
            summary.append(f"  总遗漏数: {errors.get('total_missed', 0)}")

            error_by_type = errors.get('error_count_by_type', {})
            if error_by_type:
                summary.append(f"  各类型错误分布:")
                for entity_type, count in error_by_type.items():
                    summary.append(f"    {entity_type}: {count} 个")

            missed_by_type = errors.get('missed_count_by_type', {})
            if missed_by_type:
                summary.append(f"  各类型遗漏分布:")
                for entity_type, count in missed_by_type.items():
                    summary.append(f"    {entity_type}: {count} 个")

        summary.append("=" * 60)

        return "\n".join(summary)

    def calculate_confidence_threshold_performance(self, evaluation_data: Dict[str, Any],
                                                   thresholds: List[float] = None) -> Dict[float, Dict[str, float]]:
        """计算不同置信度阈值下的性能"""

        if thresholds is None:
            thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

        threshold_performance = {}

        for threshold in thresholds:
            # 筛选高于阈值的实体
            filtered_correct = 0
            filtered_incorrect = 0
            all_missed = 0

            for doc_id, doc_data in evaluation_data.items():
                for entity in doc_data.get('evaluated_entities', []):
                    if entity['confidence'] >= threshold:
                        if entity['human_evaluation'] == 'correct':
                            filtered_correct += 1
                        elif entity['human_evaluation'] == 'incorrect':
                            filtered_incorrect += 1

                # 遗漏的实体数量不变
                all_missed += len(doc_data.get('missed_entities', []))

            # 计算该阈值下的指标
            metrics = self._calculate_prf_metrics(filtered_correct, filtered_incorrect, all_missed)
            metrics['total_extracted'] = filtered_correct + filtered_incorrect

            threshold_performance[threshold] = metrics

        return threshold_performance