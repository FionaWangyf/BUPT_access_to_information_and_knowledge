"""
信息抽取管理器
协调多个抽取器，管理抽取流程，提供统一的接口
文件位置：src/extraction/extraction_manager.py
"""

import time
import json
import os
from typing import List, Dict, Any, Optional, Union
from collections import defaultdict
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.extraction.extractor_base import BaseExtractor, ExtractionResult
from src.extraction.regex_extractor import RegexExtractor

class ExtractionManager:
    """信息抽取管理器：整合多个抽取器，管理抽取流程"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化抽取管理器
        
        Args:
            config: 配置参数字典
        """
        self.config = config or self._get_default_config()
        self.extractors = {}  # 抽取器集合
        self.is_initialized = False
        
        # 统计信息
        self.stats = {
            'total_documents_processed': 0,
            'total_extractions': 0,
            'total_processing_time': 0.0,
            'extractions_by_type': defaultdict(int),
            'extractions_by_extractor': defaultdict(int),
            'average_confidence': 0.0,
            'documents_with_extractions': 0
        }
        
        # 结果缓存
        self.results_cache = {}
        self.enable_cache = self.config.get('enable_cache', True)
        
        print(f"🔧 初始化抽取管理器")
        print(f"⚙️ 配置: {self.config}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'enable_regex_extractor': True,
            'regex_confidence_threshold': 0.6,
            'enable_cache': True,
            'merge_duplicate_entities': True,
            'min_entity_confidence': 0.5,
            'max_entities_per_type': 100,
            'enable_post_processing': True,
            'save_detailed_stats': True
        }
    
    def initialize(self) -> bool:
        """初始化所有抽取器"""
        try:
            print("🔧 初始化抽取管理器...")
            
            # 初始化正则表达式抽取器
            if self.config.get('enable_regex_extractor', True):
                regex_threshold = self.config.get('regex_confidence_threshold', 0.6)
                regex_extractor = RegexExtractor(confidence_threshold=regex_threshold)
                
                if regex_extractor.initialize():
                    self.extractors['regex'] = regex_extractor
                    print(f"✅ 正则表达式抽取器初始化成功 (阈值: {regex_threshold})")
                else:
                    print(f"❌ 正则表达式抽取器初始化失败")
                    return False
            
            # 可以在这里添加其他抽取器
            # if self.config.get('enable_ml_extractor', False):
            #     ml_extractor = MLExtractor()
            #     if ml_extractor.initialize():
            #         self.extractors['ml'] = ml_extractor
            
            if not self.extractors:
                print("❌ 没有可用的抽取器")
                return False
            
            self.is_initialized = True
            print(f"✅ 抽取管理器初始化完成，加载了 {len(self.extractors)} 个抽取器")
            return True
            
        except Exception as e:
            print(f"❌ 抽取管理器初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def extract_from_text(self, text: str, doc_id: int, field: str = "content") -> List[ExtractionResult]:
        """
        从单个文本中抽取信息
        
        Args:
            text: 待抽取的文本
            doc_id: 文档ID
            field: 字段名称
            
        Returns:
            抽取结果列表
        """
        if not self.is_initialized:
            print("❌ 抽取管理器未初始化")
            return []
        
        if not text or not text.strip():
            return []
        
        # 检查缓存
        cache_key = f"{doc_id}_{field}_{hash(text)}"
        if self.enable_cache and cache_key in self.results_cache:
            return self.results_cache[cache_key]
        
        start_time = time.time()
        all_results = []
        
        # 使用所有可用的抽取器
        for extractor_name, extractor in self.extractors.items():
            try:
                extractor_results = extractor.extract_from_text(text, doc_id, field)
                
                # 为结果添加抽取器信息
                for result in extractor_results:
                    result.metadata['extractor'] = extractor_name
                
                all_results.extend(extractor_results)
                self.stats['extractions_by_extractor'][extractor_name] += len(extractor_results)
                
            except Exception as e:
                print(f"⚠️ 抽取器 {extractor_name} 处理失败: {e}")
                continue
        
        # 后处理
        if self.config.get('enable_post_processing', True):
            all_results = self._post_process_results(all_results)
        
        # 更新统计信息
        processing_time = time.time() - start_time
        self._update_stats(all_results, processing_time)
        
        # 缓存结果
        if self.enable_cache:
            self.results_cache[cache_key] = all_results
        
        return all_results
    
    def extract_from_document(self, document: Any) -> List[ExtractionResult]:
        """
        从文档对象中抽取信息
        
        Args:
            document: 文档对象（需要有 doc_id, title, content 等属性）
            
        Returns:
            抽取结果列表
        """
        if not self.is_initialized:
            print("❌ 抽取管理器未初始化")
            return []
        
        all_results = []
        
        # 从标题抽取
        if hasattr(document, 'title') and document.title:
            title_results = self.extract_from_text(
                document.title, document.doc_id, 'title'
            )
            all_results.extend(title_results)
        
        # 从摘要抽取
        if hasattr(document, 'summary') and document.summary:
            summary_results = self.extract_from_text(
                document.summary, document.doc_id, 'summary'
            )
            all_results.extend(summary_results)
        
        # 从内容抽取
        if hasattr(document, 'content') and document.content:
            content_results = self.extract_from_text(
                document.content, document.doc_id, 'content'
            )
            all_results.extend(content_results)
        
        return all_results
    
    def extract_from_documents(self, documents: List[Any], 
                             progress_callback: Optional[callable] = None) -> Dict[int, List[ExtractionResult]]:
        """
        批量处理多个文档
        
        Args:
            documents: 文档列表
            progress_callback: 进度回调函数
            
        Returns:
            文档ID到抽取结果的映射
        """
        if not self.is_initialized:
            print("❌ 抽取管理器未初始化")
            return {}
        
        print(f"🔍 开始批量抽取，共 {len(documents)} 个文档")
        start_time = time.time()
        
        results_by_doc = {}
        
        for i, document in enumerate(documents):
            try:
                doc_results = self.extract_from_document(document)
                results_by_doc[document.doc_id] = doc_results
                
                # 调用进度回调
                if progress_callback:
                    progress = (i + 1) / len(documents)
                    progress_callback(i + 1, len(documents), progress)
                
                # 每处理100个文档输出一次进度
                if (i + 1) % 100 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / (i + 1)
                    remaining = (len(documents) - i - 1) * avg_time
                    print(f"📊 已处理 {i + 1}/{len(documents)} 个文档，预计剩余时间: {remaining:.1f}秒")
                
            except Exception as e:
                print(f"⚠️ 处理文档 {document.doc_id} 失败: {e}")
                results_by_doc[document.doc_id] = []
                continue
        
        total_time = time.time() - start_time
        total_extractions = sum(len(results) for results in results_by_doc.values())
        
        print(f"✅ 批量抽取完成:")
        print(f"  📄 处理文档: {len(documents)} 个")
        print(f"  🔍 总抽取数: {total_extractions} 个实体")
        print(f"  ⏱️ 总耗时: {total_time:.2f} 秒")
        print(f"  📊 平均每文档: {total_extractions/len(documents):.1f} 个实体")
        print(f"  🚀 处理速度: {len(documents)/total_time:.1f} 文档/秒")
        
        return results_by_doc
    
    def _post_process_results(self, results: List[ExtractionResult]) -> List[ExtractionResult]:
        """后处理抽取结果"""
        if not results:
            return results
        
        # 1. 过滤低置信度结果
        min_confidence = self.config.get('min_entity_confidence', 0.5)
        filtered_results = [r for r in results if r.confidence >= min_confidence]
        
        # 2. 去重相似实体
        if self.config.get('merge_duplicate_entities', True):
            filtered_results = self._merge_duplicate_entities(filtered_results)
        
        # 3. 限制每种类型的实体数量
        max_per_type = self.config.get('max_entities_per_type', 100)
        filtered_results = self._limit_entities_per_type(filtered_results, max_per_type)
        
        # 4. 按置信度排序
        filtered_results.sort(key=lambda x: (-x.confidence, x.entity_type, x.start_position))
        
        return filtered_results
    
    def _merge_duplicate_entities(self, results: List[ExtractionResult]) -> List[ExtractionResult]:
        """合并重复的实体"""
        merged_results = []
        
        # 按实体类型和值分组
        entity_groups = defaultdict(list)
        for result in results:
            key = (result.entity_type, result.entity_value.lower().strip())
            entity_groups[key].append(result)
        
        # 每组保留置信度最高的
        for group in entity_groups.values():
            if len(group) == 1:
                merged_results.append(group[0])
            else:
                # 选择置信度最高的
                best_result = max(group, key=lambda x: x.confidence)
                
                # 合并元数据
                all_extractors = set()
                all_patterns = set()
                for result in group:
                    if 'extractor' in result.metadata:
                        all_extractors.add(result.metadata['extractor'])
                    if 'pattern_description' in result.metadata:
                        all_patterns.add(result.metadata['pattern_description'])
                
                best_result.metadata['merged_from'] = len(group)
                best_result.metadata['all_extractors'] = list(all_extractors)
                best_result.metadata['all_patterns'] = list(all_patterns)
                
                merged_results.append(best_result)
        
        return merged_results
    
    def _limit_entities_per_type(self, results: List[ExtractionResult], 
                                max_per_type: int) -> List[ExtractionResult]:
        """限制每种类型的实体数量"""
        if max_per_type <= 0:
            return results
        
        # 按类型分组
        type_groups = defaultdict(list)
        for result in results:
            type_groups[result.entity_type].append(result)
        
        # 每种类型只保留置信度最高的前N个
        limited_results = []
        for entity_type, type_results in type_groups.items():
            # 按置信度排序
            type_results.sort(key=lambda x: x.confidence, reverse=True)
            limited_results.extend(type_results[:max_per_type])
        
        return limited_results
    
    def _update_stats(self, results: List[ExtractionResult], processing_time: float):
        """更新统计信息"""
        self.stats['total_documents_processed'] += 1
        self.stats['total_extractions'] += len(results)
        self.stats['total_processing_time'] += processing_time
        
        if results:
            self.stats['documents_with_extractions'] += 1
            
            # 更新各类型统计
            for result in results:
                self.stats['extractions_by_type'][result.entity_type] += 1
            
            # 更新平均置信度
            total_confidence = sum(r.confidence for r in results)
            total_results = self.stats['total_extractions']
            if total_results > 0:
                self.stats['average_confidence'] = (
                    self.stats['average_confidence'] * (total_results - len(results)) + 
                    total_confidence
                ) / total_results
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """获取汇总统计信息"""
        stats = dict(self.stats)
        
        # 添加计算指标
        if stats['total_documents_processed'] > 0:
            stats['avg_extractions_per_document'] = (
                stats['total_extractions'] / stats['total_documents_processed']
            )
            stats['avg_processing_time_per_document'] = (
                stats['total_processing_time'] / stats['total_documents_processed']
            )
            stats['documents_with_extractions_ratio'] = (
                stats['documents_with_extractions'] / stats['total_documents_processed']
            )
        
        # 转换 defaultdict 为普通字典
        stats['extractions_by_type'] = dict(stats['extractions_by_type'])
        stats['extractions_by_extractor'] = dict(stats['extractions_by_extractor'])
        
        return stats
    
    def save_statistics(self, filepath: str):
        """保存统计信息到文件"""
        try:
            stats = self.get_summary_statistics()
            
            # 添加时间戳和配置信息
            stats['timestamp'] = time.time()
            stats['config'] = self.config
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"📊 统计信息已保存到: {filepath}")
            
        except Exception as e:
            print(f"❌ 保存统计信息失败: {e}")
    
    def export_results(self, results: Union[List[ExtractionResult], Dict[int, List[ExtractionResult]]], 
                      filepath: str, format: str = 'json'):
        """
        导出抽取结果
        
        Args:
            results: 抽取结果
            filepath: 输出文件路径
            format: 输出格式 ('json', 'csv', 'txt')
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            if format == 'json':
                self._export_json(results, filepath)
            elif format == 'csv':
                self._export_csv(results, filepath)
            elif format == 'txt':
                self._export_txt(results, filepath)
            else:
                raise ValueError(f"不支持的格式: {format}")
                
            print(f"📤 结果已导出到: {filepath}")
            
        except Exception as e:
            print(f"❌ 导出结果失败: {e}")
    
    def _export_json(self, results: Union[List[ExtractionResult], Dict[int, List[ExtractionResult]]], 
                    filepath: str):
        """导出为JSON格式"""
        if isinstance(results, dict):
            export_data = {
                doc_id: [result.to_dict() for result in doc_results]
                for doc_id, doc_results in results.items()
            }
        else:
            export_data = [result.to_dict() for result in results]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def _export_csv(self, results: Union[List[ExtractionResult], Dict[int, List[ExtractionResult]]], 
                   filepath: str):
        """导出为CSV格式"""
        import csv
        
        # 展平结果
        if isinstance(results, dict):
            all_results = []
            for doc_results in results.values():
                all_results.extend(doc_results)
        else:
            all_results = results
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入表头
            writer.writerow([
                'doc_id', 'entity_type', 'entity_value', 'confidence',
                'start_position', 'end_position', 'field', 'context'
            ])
            
            # 写入数据
            for result in all_results:
                writer.writerow([
                    result.doc_id, result.entity_type, result.entity_value,
                    result.confidence, result.start_position, result.end_position,
                    result.field, result.context
                ])
    
    def _export_txt(self, results: Union[List[ExtractionResult], Dict[int, List[ExtractionResult]]], 
                   filepath: str):
        """导出为文本格式"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("信息抽取结果报告\n")
            f.write("=" * 50 + "\n\n")
            
            if isinstance(results, dict):
                for doc_id, doc_results in results.items():
                    f.write(f"文档 {doc_id}:\n")
                    f.write("-" * 30 + "\n")
                    
                    if doc_results:
                        # 按类型分组
                        by_type = defaultdict(list)
                        for result in doc_results:
                            by_type[result.entity_type].append(result)
                        
                        for entity_type, type_results in by_type.items():
                            f.write(f"\n{entity_type.upper()}:\n")
                            for result in sorted(type_results, key=lambda x: x.confidence, reverse=True):
                                f.write(f"  - {result.entity_value} (置信度: {result.confidence:.3f})\n")
                    else:
                        f.write("  (无抽取结果)\n")
                    
                    f.write("\n")
            else:
                # 单个结果列表
                by_type = defaultdict(list)
                for result in results:
                    by_type[result.entity_type].append(result)
                
                for entity_type, type_results in by_type.items():
                    f.write(f"\n{entity_type.upper()}:\n")
                    f.write("-" * 20 + "\n")
                    for result in sorted(type_results, key=lambda x: x.confidence, reverse=True):
                        f.write(f"  - {result.entity_value} (置信度: {result.confidence:.3f})\n")
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_documents_processed': 0,
            'total_extractions': 0,
            'total_processing_time': 0.0,
            'extractions_by_type': defaultdict(int),
            'extractions_by_extractor': defaultdict(int),
            'average_confidence': 0.0,
            'documents_with_extractions': 0
        }
        print("📊 统计信息已重置")
    
    def clear_cache(self):
        """清空缓存"""
        self.results_cache.clear()
        print("🗑️ 缓存已清空")
    
    def get_supported_entity_types(self) -> List[str]:
        """获取所有支持的实体类型"""
        all_types = set()
        for extractor in self.extractors.values():
            all_types.update(extractor.get_supported_entity_types())
        return sorted(list(all_types))


# 测试代码
if __name__ == "__main__":
    print("=== 抽取管理器测试 ===")
    
    # 创建管理器
    config = {
        'enable_regex_extractor': True,
        'regex_confidence_threshold': 0.6,
        'merge_duplicate_entities': True,
        'max_entities_per_type': 20
    }
    
    manager = ExtractionManager(config)
    
    if not manager.initialize():
        print("❌ 管理器初始化失败")
        exit(1)
    
    # 测试文本
    test_texts = [
        "President Biden announced $2.5 billion aid to Ukraine yesterday.",
        "NPR's David Folkenflik reported from Washington, D.C.",
        '"This is crucial for democracy," said Secretary Austin.',
        "The meeting took place at the White House on March 15, 2024.",
    ]
    
    print(f"\n📋 支持的实体类型: {manager.get_supported_entity_types()}")
    
    # 测试单个文本抽取
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 测试文本 {i}: {text}")
        results = manager.extract_from_text(text, doc_id=i, field="test")
        
        if results:
            for result in results:
                print(f"  ✓ {result.entity_type}: '{result.entity_value}' (置信度: {result.confidence:.3f})")
        else:
            print("  (无抽取结果)")
    
    # 显示统计信息
    print(f"\n📊 抽取统计:")
    stats = manager.get_summary_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")
    
    print("\n✅ 抽取管理器测试完成！")