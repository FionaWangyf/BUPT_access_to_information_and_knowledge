"""
信息抽取基础类
定义抽取器接口和结果数据结构
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json

@dataclass
class ExtractionResult:
    """信息抽取结果类"""
    
    # 基本信息
    entity_type: str        # 实体类型（人名、地名等）
    entity_value: str       # 实体值
    confidence: float       # 置信度 [0-1]
    
    # 位置信息
    start_position: int     # 在原文中的开始位置
    end_position: int       # 在原文中的结束位置
    context: str           # 上下文信息
    
    # 文档信息
    doc_id: int            # 文档ID
    field: str             # 字段名（title/content/summary）
    
    # 附加信息
    metadata: Dict[str, Any] = None  # 额外元数据
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'entity_type': self.entity_type,
            'entity_value': self.entity_value,
            'confidence': self.confidence,
            'start_position': self.start_position,
            'end_position': self.end_position,
            'context': self.context,
            'doc_id': self.doc_id,
            'field': self.field,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtractionResult':
        """从字典创建对象"""
        return cls(**data)
    
    def __str__(self):
        return f"ExtractionResult({self.entity_type}: '{self.entity_value}', confidence={self.confidence:.3f})"


class BaseExtractor(ABC):
    """抽取器基类：定义统一的抽取接口"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_initialized = False
        self.statistics = {
            'total_documents_processed': 0,
            'total_extractions': 0,
            'extractions_by_type': {},
            'processing_time': 0.0
        }
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化抽取器"""
        pass
    
    @abstractmethod
    def extract_from_text(self, text: str, doc_id: int, field: str) -> List[ExtractionResult]:
        """从文本中抽取信息"""
        pass
    
    @abstractmethod
    def get_supported_entity_types(self) -> List[str]:
        """获取支持的实体类型列表"""
        pass
    
    def extract_from_document(self, document: Any) -> List[ExtractionResult]:
        """从文档对象中抽取信息"""
        results = []
        
        # 从标题抽取
        if hasattr(document, 'title') and document.title:
            title_results = self.extract_from_text(
                document.title, document.doc_id, 'title'
            )
            results.extend(title_results)
        
        # 从摘要抽取
        if hasattr(document, 'summary') and document.summary:
            summary_results = self.extract_from_text(
                document.summary, document.doc_id, 'summary'
            )
            results.extend(summary_results)
        
        # 从内容抽取
        if hasattr(document, 'content') and document.content:
            content_results = self.extract_from_text(
                document.content, document.doc_id, 'content'
            )
            results.extend(content_results)
        
        # 更新统计信息
        self._update_statistics(results)
        
        return results
    
    def _update_statistics(self, results: List[ExtractionResult]):
        """更新统计信息"""
        self.statistics['total_documents_processed'] += 1
        self.statistics['total_extractions'] += len(results)
        
        for result in results:
            entity_type = result.entity_type
            if entity_type not in self.statistics['extractions_by_type']:
                self.statistics['extractions_by_type'][entity_type] = 0
            self.statistics['extractions_by_type'][entity_type] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.statistics.copy()
    
    def reset_statistics(self):
        """重置统计信息"""
        self.statistics = {
            'total_documents_processed': 0,
            'total_extractions': 0,
            'extractions_by_type': {},
            'processing_time': 0.0
        }


# 测试代码
if __name__ == "__main__":
    print("=== 基础类测试 ===")
    
    # 测试ExtractionResult
    result = ExtractionResult(
        entity_type="person",
        entity_value="John Smith",
        confidence=0.85,
        start_position=10,
        end_position=20,
        context="President John Smith announced",
        doc_id=1,
        field="title",
        metadata={"pattern_type": "with_title"}
    )
    
    print(f"创建的结果: {result}")
    print(f"转为字典: {result.to_dict()}")
    
    # 从字典恢复
    result_dict = result.to_dict()
    restored_result = ExtractionResult.from_dict(result_dict)
    print(f"从字典恢复: {restored_result}")
    
    print("✅ 基础类测试通过")
