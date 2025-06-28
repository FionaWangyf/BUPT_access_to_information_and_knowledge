#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息抽取评价器
文件位置：src/evaluation/extraction_evaluator.py
"""

import json
import random
import os
from typing import List, Dict, Any, Optional
from collections import defaultdict


class MockDocument:
    """模拟文档对象（与现有测试代码兼容）"""

    def __init__(self, doc_id: int, title: str, content: str, summary: str = ""):
        self.doc_id = doc_id
        self.title = title
        self.content = content
        self.summary = summary


class ExtractionEvaluator:
    """信息抽取人工评价器"""

    def __init__(self, extraction_manager, config: Dict[str, Any]):
        self.extraction_manager = extraction_manager
        self.config = config
        self.evaluation_data = {}

    def create_sample(self, articles: List[Dict]) -> List[MockDocument]:
        """创建评价样本"""
        sample_size = self.config.get('sample_size', 50)

        # 随机采样
        if len(articles) > sample_size:
            sampled_articles = random.sample(articles, sample_size)
        else:
            sampled_articles = articles

        # 创建文档对象
        sample_docs = []
        for i, article in enumerate(sampled_articles):
            doc = MockDocument(
                doc_id=i,
                title=article.get('title', ''),
                content=article.get('content', ''),
                summary=article.get('summary', '')
            )
            sample_docs.append(doc)

        # 保存样本信息
        sample_info = {
            'sample_size': len(sample_docs),
            'documents': [
                {
                    'doc_id': doc.doc_id,
                    'title': doc.title,
                    'content_preview': doc.content[:200] + '...' if len(doc.content) > 200 else doc.content
                }
                for doc in sample_docs
            ]
        }

        sample_file = self.config.get('sample_file', 'results/evaluation_sample.json')
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(sample_info, f, indent=2, ensure_ascii=False)

        return sample_docs

    def extract_from_sample(self, sample_docs: List[MockDocument]) -> Dict[int, List]:
        """对样本文档进行信息抽取"""
        results = {}

        print("📊 正在对样本文档进行信息抽取...")

        for i, doc in enumerate(sample_docs):
            print(f"  处理文档 {i + 1}/{len(sample_docs)}: {doc.title[:50]}...")

            # 构建完整文本
            full_text = f"{doc.title}. {doc.summary} {doc.content}"

            # 执行抽取
            entities = self.extraction_manager.extract_from_text(full_text, doc.doc_id, "evaluation")

            # 限制每篇文档的实体数量
            max_entities = self.config.get('entities_per_doc', 10)
            if len(entities) > max_entities:
                # 按置信度排序，取前N个
                entities = sorted(entities, key=lambda x: x.confidence, reverse=True)[:max_entities]

            results[doc.doc_id] = entities

        # 保存抽取结果
        sample_results = {}
        for doc_id, entities in results.items():
            sample_results[doc_id] = {
                'document_info': {
                    'doc_id': doc_id,
                    'title': sample_docs[doc_id].title,
                    'content_preview': sample_docs[doc_id].content[:300]
                },
                'extracted_entities': [
                    {
                        'entity_type': entity.entity_type,
                        'entity_value': entity.entity_value,
                        'confidence': entity.confidence,
                        'field': entity.field,
                        'context': entity.context[:100] if entity.context else '',
                        'start_pos': getattr(entity, 'start_pos', -1),
                        'end_pos': getattr(entity, 'end_pos', -1)
                    }
                    for entity in entities
                ]
            }

        # 保存到文件
        sample_file = self.config.get('sample_file', 'results/evaluation_sample.json')
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(sample_results, f, indent=2, ensure_ascii=False)

        return sample_results

    def load_sample_results(self) -> Optional[Dict]:
        """加载已有的样本抽取结果"""
        sample_file = self.config.get('sample_file', 'results/evaluation_sample.json')

        if not os.path.exists(sample_file):
            return None

        try:
            with open(sample_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载样本文件失败: {e}")
            return None

    def start_manual_evaluation(self, sample_results: Dict[int, Dict]):
        """开始人工评价"""
        eval_file = self.config.get('evaluation_file', 'results/extraction_evaluation.json')

        # 加载已有的评价结果
        if os.path.exists(eval_file):
            try:
                with open(eval_file, 'r', encoding='utf-8') as f:
                    self.evaluation_data = json.load(f)
                print(f"📋 已加载现有评价数据，包含 {len(self.evaluation_data)} 篇文档的评价")
            except:
                self.evaluation_data = {}
        else:
            self.evaluation_data = {}

        # 开始评价流程
        docs_to_evaluate = list(sample_results.keys())
        evaluated_count = 0

        for doc_id in docs_to_evaluate:
            doc_id_str = str(doc_id)

            # 检查是否已经评价过
            if doc_id_str in self.evaluation_data:
                response = input(f"\n文档 {doc_id} 已评价过，是否重新评价？(y/n): ").strip().lower()
                if response != 'y':
                    continue

            # 评价单个文档
            if self._evaluate_document(doc_id, sample_results[doc_id]):
                evaluated_count += 1

                # 定期保存
                if evaluated_count % 5 == 0:
                    self._save_evaluation_data()
                    print(f"✅ 已保存评价进度 ({evaluated_count} 篇文档)")

            # 询问是否继续
            if doc_id != docs_to_evaluate[-1]:  # 不是最后一个文档
                response = input(f"\n继续评价下一篇文档？(y/n/q退出): ").strip().lower()
                if response == 'q':
                    break
                elif response == 'n':
                    break

        # 最终保存
        self._save_evaluation_data()
        print(f"\n✅ 评价完成！共评价了 {evaluated_count} 篇文档")

    def _evaluate_document(self, doc_id: int, doc_data: Dict) -> bool:
        """评价单个文档"""
        print(f"\n{'=' * 80}")
        print(f"📄 文档 {doc_id}: {doc_data['document_info']['title']}")
        print(f"{'=' * 80}")

        # 显示文档内容预览
        content_preview = doc_data['document_info']['content_preview']
        print(f"\n📝 内容预览:")
        print(f"{content_preview}...")

        extracted_entities = doc_data['extracted_entities']
        print(f"\n🔍 抽取到 {len(extracted_entities)} 个实体")

        if not extracted_entities:
            print("❌ 该文档没有抽取到任何实体")
            return False

        # 评价每个抽取的实体
        evaluated_entities = []

        for i, entity in enumerate(extracted_entities):
            print(f"\n--- 实体 {i + 1}/{len(extracted_entities)} ---")
            print(f"类型: {entity['entity_type']}")
            print(f"值: {entity['entity_value']}")
            print(f"置信度: {entity['confidence']:.3f}")
            print(f"字段: {entity['field']}")
            if entity['context']:
                print(f"上下文: {entity['context']}")

            while True:
                try:
                    evaluation = input("评价 [✓(y)正确 / ✗(n)错误 / ?(s)跳过 / q退出]: ").strip().lower()

                    if evaluation == 'q':
                        return False
                    elif evaluation in ['y', 'yes', '✓', '1']:
                        evaluated_entities.append({
                            **entity,
                            'human_evaluation': 'correct',
                            'evaluation_notes': ''
                        })
                        print("✅ 标记为正确")
                        break
                    elif evaluation in ['n', 'no', '✗', '0']:
                        notes = input("  请说明错误原因（可选）: ").strip()
                        evaluated_entities.append({
                            **entity,
                            'human_evaluation': 'incorrect',
                            'evaluation_notes': notes
                        })
                        print("❌ 标记为错误")
                        break
                    elif evaluation in ['s', 'skip', '?']:
                        evaluated_entities.append({
                            **entity,
                            'human_evaluation': 'skipped',
                            'evaluation_notes': ''
                        })
                        print("⏭️ 跳过")
                        break
                    else:
                        print("❌ 无效输入，请输入 y/n/s/q")
                except KeyboardInterrupt:
                    print("\n❌ 评价被中断")
                    return False

        # 询问遗漏的实体
        print(f"\n🔍 是否有遗漏的实体？")
        print("请输入遗漏的实体，格式：类型:值 （如 PERSON:张三）")
        print("输入 'done' 完成，'skip' 跳过")

        missed_entities = []
        while True:
            try:
                missed_input = input("遗漏实体: ").strip()

                if missed_input.lower() in ['done', 'finish', '完成']:
                    break
                elif missed_input.lower() in ['skip', '跳过']:
                    break
                elif ':' in missed_input:
                    try:
                        entity_type, entity_value = missed_input.split(':', 1)
                        entity_type = entity_type.strip().upper()
                        entity_value = entity_value.strip()

                        if entity_type and entity_value:
                            missed_entities.append({
                                'entity_type': entity_type,
                                'entity_value': entity_value,
                                'human_added': True
                            })
                            print(f"✅ 已添加遗漏实体: {entity_type}:{entity_value}")
                    except:
                        print("❌ 格式错误，请使用 类型:值 的格式")
                else:
                    print("❌ 格式错误，请使用 类型:值 的格式")
            except KeyboardInterrupt:
                print("\n评价被中断")
                break

        # 保存评价结果
        doc_evaluation = {
            'document_info': doc_data['document_info'],
            'extraction_timestamp': doc_data.get('extraction_timestamp', ''),
            'evaluated_entities': evaluated_entities,
            'missed_entities': missed_entities,
            'evaluation_summary': {
                'total_extracted': len(extracted_entities),
                'evaluated_count': len([e for e in evaluated_entities if e['human_evaluation'] != 'skipped']),
                'correct_count': len([e for e in evaluated_entities if e['human_evaluation'] == 'correct']),
                'incorrect_count': len([e for e in evaluated_entities if e['human_evaluation'] == 'incorrect']),
                'missed_count': len(missed_entities)
            }
        }

        self.evaluation_data[str(doc_id)] = doc_evaluation

        # 显示本文档评价摘要
        summary = doc_evaluation['evaluation_summary']
        print(f"\n📊 文档 {doc_id} 评价摘要:")
        print(f"  抽取实体: {summary['total_extracted']} 个")
        print(f"  已评价: {summary['evaluated_count']} 个")
        print(f"  正确: {summary['correct_count']} 个")
        print(f"  错误: {summary['incorrect_count']} 个")
        print(f"  遗漏: {summary['missed_count']} 个")

        return True

    def _save_evaluation_data(self):
        """保存评价数据"""
        eval_file = self.config.get('evaluation_file', 'results/extraction_evaluation.json')

        try:
            with open(eval_file, 'w', encoding='utf-8') as f:
                json.dump(self.evaluation_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存评价数据失败: {e}")

    def load_evaluation_results(self) -> Optional[Dict]:
        """加载评价结果"""
        eval_file = self.config.get('evaluation_file', 'results/extraction_evaluation.json')

        if not os.path.exists(eval_file):
            return None

        try:
            with open(eval_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载评价结果失败: {e}")
            return None