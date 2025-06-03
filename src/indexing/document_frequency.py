import math
from typing import List, Dict, Set
from collections import defaultdict

class DocumentFrequencyCalculator:
    """文档频率计算器：计算DF和IDF（Inverse Document Frequency）值"""
    
    def __init__(self):
        self.document_count = 0
        self.document_frequency = {}  # 每个词汇在多少个文档中出现
        self.vocabulary = set()
    
    def build_df_from_documents(self, documents_tokens: List[List[str]]) -> None:
        """从文档集合构建DF统计"""
        self.document_count = len(documents_tokens)
        self.document_frequency = defaultdict(int)
        self.vocabulary = set()
        
        print(f"开始构建DF统计，共{self.document_count}个文档...")
        
        for doc_tokens in documents_tokens:
            # 获取文档中的唯一词汇
            unique_tokens = set(doc_tokens)
            self.vocabulary.update(unique_tokens)
            
            # 更新每个词汇的文档频率
            for token in unique_tokens:
                self.document_frequency[token] += 1
        
        print(f"DF统计完成，词汇表大小: {len(self.vocabulary)}")
    
    def get_document_frequency(self, term: str) -> int:
        """获取词汇的文档频率"""
        return self.document_frequency.get(term, 0)
    
    def calculate_idf(self, term: str) -> float:
        """计算词汇的IDF值：log(总文档数 / 包含该词的文档数)"""
        df = self.get_document_frequency(term)
        if df == 0:
            return 0
        return math.log(self.document_count / df)
    
    def calculate_smooth_idf(self, term: str) -> float:
        """计算平滑IDF值：log(总文档数 / (1 + 包含该词的文档数))"""
        df = self.get_document_frequency(term)
        return math.log(self.document_count / (1 + df))
    
    def get_idf_dict(self, smooth: bool = False) -> Dict[str, float]:
        """获取所有词汇的IDF字典"""
        idf_dict = {}
        for term in self.vocabulary:
            if smooth:
                idf_dict[term] = self.calculate_smooth_idf(term)
            else:
                idf_dict[term] = self.calculate_idf(term)
        return idf_dict
    
    def get_vocabulary_stats(self) -> Dict[str, int]:
        """获取词汇表统计信息"""
        if not self.document_frequency:
            return {}
        
        df_values = list(self.document_frequency.values())
        return {
            "词汇总数": len(self.vocabulary),
            "最高文档频率": max(df_values),
            "最低文档频率": min(df_values),
            "平均文档频率": sum(df_values) / len(df_values),
            "只出现在1个文档中的词汇数": sum(1 for df in df_values if df == 1),
            "出现在所有文档中的词汇数": sum(1 for df in df_values if df == self.document_count)
        }
    
    def get_rare_terms(self, max_df: int = 2) -> List[str]:
        """获取稀有词汇（文档频率小于等于max_df的词汇）"""
        return [term for term, df in self.document_frequency.items() if df <= max_df]
    
    def get_common_terms(self, min_df_ratio: float = 0.1) -> List[str]:
        """获取常见词汇（文档频率比例大于min_df_ratio的词汇）"""
        min_df = int(self.document_count * min_df_ratio)
        return [term for term, df in self.document_frequency.items() if df >= min_df]


# 测试代码
if __name__ == "__main__":
    # 测试文档频率计算器
    print("=== 文档频率计算测试 ===")
    
    df_calculator = DocumentFrequencyCalculator()
    
    # 测试文档集合
    documents = [
        ["apple", "banana", "cherry"],
        ["banana", "date", "elderberry"],
        ["apple", "cherry", "fig"],
        ["banana", "apple", "grape"],
        ["date", "elderberry", "fig", "grape"]
    ]
    
    print("测试文档集合:")
    for i, doc in enumerate(documents):
        print(f"文档{i+1}: {doc}")
    
    # 构建DF统计
    df_calculator.build_df_from_documents(documents)
    
    # 显示DF统计
    print(f"\n=== 文档频率统计 ===")
    for term in sorted(df_calculator.vocabulary):
        df = df_calculator.get_document_frequency(term)
        idf = df_calculator.calculate_idf(term)
        smooth_idf = df_calculator.calculate_smooth_idf(term)
        print(f"{term}: DF={df}, IDF={idf:.3f}, 平滑IDF={smooth_idf:.3f}")
    
    # 显示统计信息
    print(f"\n=== 词汇表统计 ===")
    stats = df_calculator.get_vocabulary_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    # 显示稀有和常见词汇
    print(f"\n=== 稀有词汇(DF<=1) ===")
    rare_terms = df_calculator.get_rare_terms(1)
    print(f"稀有词汇: {rare_terms}")
    
    print(f"\n=== 常见词汇(DF>=40%) ===")
    common_terms = df_calculator.get_common_terms(0.4)
    print(f"常见词汇: {common_terms}")