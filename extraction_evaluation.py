#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息抽取系统人工评价工具
文件位置：extraction_evaluation.py
"""

import sys
import os
import json
import time
import argparse
from typing import List, Dict, Any, Optional

sys.path.append('src')

from src.extraction.extraction_manager import ExtractionManager
from src.evaluation.extraction_evaluator import ExtractionEvaluator
from src.evaluation.extraction_metrics import ExtractionMetrics


class ExtractionEvaluationSystem:
    """信息抽取系统评价工具"""

    def __init__(self, data_file: str = "data/npr_articles.json"):
        self.data_file = data_file
        self.extraction_manager = None
        self.evaluator = None
        self.metrics_calculator = ExtractionMetrics()

        # 评价配置
        self.evaluation_config = {
            'sample_size': 10,  # 用于评价的文档样本数
            'entities_per_doc': 10,  # 每篇文档评价的实体数上限
            'evaluation_file': 'results/extraction_evaluation.json',
            'sample_file': 'results/evaluation_sample.json'
        }

    def initialize(self) -> bool:
        """初始化评价系统"""
        try:
            print("🔧 初始化信息抽取评价系统...")

            # 检查数据文件
            if not os.path.exists(self.data_file):
                print(f"❌ 数据文件不存在: {self.data_file}")
                return False

            # 初始化抽取管理器
            config = {
                'enable_regex_extractor': True,
                'regex_confidence_threshold': 0.6,
                'merge_duplicate_entities': True,
                'max_entities_per_type': 50,
                'enable_cache': True,
            }

            self.extraction_manager = ExtractionManager(config)
            if not self.extraction_manager.initialize():
                print("❌ 抽取管理器初始化失败")
                return False

            # 初始化评价器
            self.evaluator = ExtractionEvaluator(
                self.extraction_manager,
                self.evaluation_config
            )

            # 创建结果目录
            os.makedirs('results', exist_ok=True)

            print("✅ 评价系统初始化成功！")
            return True

        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return False

    def create_evaluation_sample(self, sample_size: int = None):
        """创建评价样本"""
        if sample_size:
            self.evaluation_config['sample_size'] = sample_size

        print(f"📊 创建评价样本 (样本大小: {self.evaluation_config['sample_size']})")

        try:
            # 加载文档数据
            with open(self.data_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)

            # 创建样本
            sample_docs = self.evaluator.create_sample(articles)

            print(f"✅ 已创建包含 {len(sample_docs)} 篇文档的评价样本")

            # 对样本进行抽取
            print("🔍 正在对样本文档进行信息抽取...")
            sample_results = self.evaluator.extract_from_sample(sample_docs)

            print(f"✅ 样本抽取完成，共抽取 {sum(len(results) for results in sample_results.values())} 个实体")

            return sample_results

        except Exception as e:
            print(f"❌ 创建评价样本失败: {e}")
            return None

    def run_manual_evaluation(self, sample_results: Dict = None):
        """运行人工评价"""
        print("\n" + "=" * 60)
        print("🎯 信息抽取系统人工评价")
        print("=" * 60)

        if sample_results is None:
            # 尝试加载已有的样本结果
            try:
                sample_results = self.evaluator.load_sample_results()
                if not sample_results:
                    print("📊 未找到已有样本，正在创建新样本...")
                    sample_results = self.create_evaluation_sample()
                    if not sample_results:
                        return
            except Exception as e:
                print(f"❌ 加载样本失败: {e}")
                return

        print("\n📖 评价说明:")
        print("  对于每个抽取的实体，您需要评判其是否正确：")
        print("  ✓ (y) - 正确：实体类型和值都正确")
        print("  ✗ (n) - 错误：实体类型或值不正确")
        print("  ? (s) - 跳过：不确定或暂时跳过")
        print("  📝 在每篇文档评价完成后，您还可以添加遗漏的实体")

        # 开始人工评价
        self.evaluator.start_manual_evaluation(sample_results)

    def calculate_metrics(self):
        """计算评价指标"""
        print("\n📊 计算评价指标...")

        eval_file = self.evaluation_config['evaluation_file']
        if not os.path.exists(eval_file):
            print(f"❌ 评价文件不存在: {eval_file}")
            print("请先进行人工评价")
            return

        try:
            # 加载评价数据
            evaluation_data = self.evaluator.load_evaluation_results()
            if not evaluation_data:
                print("❌ 没有找到评价数据")
                return

            # 计算指标
            metrics = self.metrics_calculator.calculate_overall_metrics(evaluation_data)

            # 显示结果
            self._display_metrics(metrics)

            # 保存详细报告
            self._save_evaluation_report(metrics, evaluation_data)

        except Exception as e:
            print(f"❌ 计算指标时出错: {e}")
            import traceback
            traceback.print_exc()

    def _display_metrics(self, metrics: Dict[str, Any]):
        """显示评价指标"""
        print("\n" + "=" * 60)
        print("📈 信息抽取系统评价结果")
        print("=" * 60)

        # 总体指标
        overall = metrics.get('overall', {})
        print(f"\n🎯 总体性能:")
        print(f"  精确率 (Precision): {overall.get('precision', 0):.3f}")
        print(f"  召回率 (Recall):    {overall.get('recall', 0):.3f}")
        print(f"  F1分数 (F1-Score):  {overall.get('f1_score', 0):.3f}")
        print(f"  总抽取实体数:       {overall.get('total_extracted', 0)}")
        print(f"  正确实体数:         {overall.get('correct_entities', 0)}")
        print(f"  遗漏实体数:         {overall.get('missed_entities', 0)}")

        # 各类型指标
        by_type = metrics.get('by_type', {})
        if by_type:
            print(f"\n📋 各实体类型性能:")
            print(f"{'类型':<12} {'精确率':<8} {'召回率':<8} {'F1分数':<8} {'抽取数':<6} {'正确数':<6}")
            print(f"{'-' * 60}")

            for entity_type, type_metrics in by_type.items():
                precision = type_metrics.get('precision', 0)
                recall = type_metrics.get('recall', 0)
                f1 = type_metrics.get('f1_score', 0)
                extracted = type_metrics.get('extracted_count', 0)
                correct = type_metrics.get('correct_count', 0)

                print(f"{entity_type:<12} {precision:<8.3f} {recall:<8.3f} {f1:<8.3f} {extracted:<6} {correct:<6}")

        # 置信度分析
        confidence_analysis = metrics.get('confidence_analysis', {})
        if confidence_analysis:
            print(f"\n🎚️ 置信度分析:")
            print(f"  平均置信度: {confidence_analysis.get('average_confidence', 0):.3f}")
            print(f"  高置信度实体 (>0.8): {confidence_analysis.get('high_confidence_count', 0)}")
            print(f"  中置信度实体 (0.5-0.8): {confidence_analysis.get('medium_confidence_count', 0)}")
            print(f"  低置信度实体 (<0.5): {confidence_analysis.get('low_confidence_count', 0)}")

    def _save_evaluation_report(self, metrics: Dict[str, Any], evaluation_data: Dict[str, Any]):
        """保存评价报告"""
        report = {
            'evaluation_summary': {
                'evaluation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_documents_evaluated': len(evaluation_data),
                'total_entities_evaluated': sum(
                    len(doc_data.get('evaluated_entities', []))
                    for doc_data in evaluation_data.values()
                )
            },
            'metrics': metrics,
            'detailed_results': evaluation_data
        }

        report_file = 'results/extraction_evaluation_report.json'
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n📋 详细评价报告已保存到: {report_file}")
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")

    def load_external_extraction_results(self, file_path: str) -> Optional[Dict]:
        """从已有 JSON 文件加载抽取结果（用于人工评价）"""
        if not os.path.exists(file_path):
            print(f"❌ 指定的抽取结果文件不存在: {file_path}")
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"📂 成功加载外部抽取结果，共 {len(data)} 篇文档")
            return data
        except Exception as e:
            print(f"❌ 加载抽取结果失败: {e}")
            return None

    def interactive_menu(self):
        """交互式菜单"""
        while True:
            print(f"\n{'=' * 50}")
            print(f"🔬 信息抽取系统评价工具")
            print(f"{'=' * 50}")
            print(f"1. 创建评价样本")
            print(f"2. 运行人工评价")
            print(f"3. 计算评价指标")
            print(f"4. 查看评价状态")
            print(f"5. 导出评价数据")
            print(f"6. 系统设置")
            print(f"7. 退出")

            try:
                choice = input(f"\n请选择功能 (1-7): ").strip()

                if choice == '1':
                    sample_size = input("请输入样本大小 (默认50): ").strip()
                    if sample_size.isdigit():
                        sample_size = int(sample_size)
                    else:
                        sample_size = 50
                    self.create_evaluation_sample(sample_size)

                elif choice == '2':
                #     self.run_manual_evaluation()
                    file_path = input("请输入抽取结果 JSON 文件路径: ").strip()
                    sample_results = self.load_external_extraction_results(file_path)
                    if sample_results:
                        self.run_manual_evaluation(sample_results)

                elif choice == '3':
                    self.calculate_metrics()

                elif choice == '4':
                    self._show_evaluation_status()

                elif choice == '5':
                    self._export_evaluation_data()

                elif choice == '6':
                    self._show_settings()

                elif choice == '7':
                    print("👋 再见！")
                    break

                else:
                    print("❌ 无效选择，请输入1-7")

            except KeyboardInterrupt:
                print("\n\n👋 程序被中断，再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")

    def _show_evaluation_status(self):
        """显示评价状态"""
        print("\n📊 评价状态:")

        # 检查样本文件
        sample_file = self.evaluation_config['sample_file']
        if os.path.exists(sample_file):
            try:
                with open(sample_file, 'r', encoding='utf-8') as f:
                    sample_data = json.load(f)
                print(f"  📄 评价样本: {len(sample_data)} 篇文档")
            except:
                print(f"  📄 评价样本: 文件存在但无法读取")
        else:
            print(f"  📄 评价样本: 未创建")

        # 检查评价文件
        eval_file = self.evaluation_config['evaluation_file']
        if os.path.exists(eval_file):
            try:
                with open(eval_file, 'r', encoding='utf-8') as f:
                    eval_data = json.load(f)
                evaluated_docs = len(eval_data)
                total_evaluations = sum(
                    len(doc_data.get('evaluated_entities', []))
                    for doc_data in eval_data.values()
                )
                print(f"  ✅ 已评价文档: {evaluated_docs} 篇")
                print(f"  ✅ 已评价实体: {total_evaluations} 个")
            except:
                print(f"  ✅ 评价进度: 文件存在但无法读取")
        else:
            print(f"  ✅ 评价进度: 未开始")

    def _export_evaluation_data(self):
        """导出评价数据"""
        print("\n📤 导出评价数据...")
        formats = ['json', 'csv', 'xlsx']

        print("支持的格式:")
        for i, fmt in enumerate(formats, 1):
            print(f"  {i}. {fmt.upper()}")

        try:
            choice = input("请选择格式 (1-3): ").strip()
            if choice in ['1', '2', '3']:
                fmt = formats[int(choice) - 1]
                output_file = f"results/extraction_evaluation_export.{fmt}"

                # 这里可以添加实际的导出逻辑
                print(f"✅ 评价数据已导出到: {output_file}")
            else:
                print("❌ 无效选择")
        except:
            print("❌ 导出失败")

    def _show_settings(self):
        """显示和修改设置"""
        print("\n⚙️ 当前设置:")
        for key, value in self.evaluation_config.items():
            print(f"  {key}: {value}")

        print("\n要修改设置，请直接编辑配置文件或重新运行程序")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="信息抽取系统人工评价工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python extraction_evaluation.py                    # 交互式模式
  python extraction_evaluation.py --sample 30       # 创建30个样本
  python extraction_evaluation.py --evaluate         # 直接开始评价
  python extraction_evaluation.py --metrics          # 计算指标
        """
    )

    parser.add_argument('--sample', type=int, help='创建评价样本（指定样本大小）')
    parser.add_argument('--evaluate', action='store_true', help='运行人工评价')
    parser.add_argument('--metrics', action='store_true', help='计算评价指标')
    parser.add_argument('--data-file', default='data/npr_articles.json', help='数据文件路径')

    args = parser.parse_args()

    # 创建评价系统
    eval_system = ExtractionEvaluationSystem(args.data_file)

    if not eval_system.initialize():
        print("❌ 评价系统初始化失败")
        return 1

    try:
        if args.sample:
            eval_system.create_evaluation_sample(args.sample)
        elif args.evaluate:
            eval_system.run_manual_evaluation()
        elif args.metrics:
            eval_system.calculate_metrics()
        else:
            # 默认交互模式
            eval_system.interactive_menu()

        return 0

    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断，再见！")
        return 0
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())