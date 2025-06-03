from collections import defaultdict
from typing import List, Dict, Set, Tuple
import json
import pickle

class PostingList:
    """倒排列表：存储包含某个词汇的文档信息"""
    
    def __init__(self):
        self.documents = []  # [(doc_id, term_frequency), ...]
        self.document_frequency = 0
    
    def add_document(self, doc_id: int, term_frequency: int):
        """添加文档到倒排列表"""
        self.documents.append((doc_id, term_frequency))
        self.document_frequency += 1
    
    def get_documents(self) -> List[Tuple[int, int]]:
        """获取包含该词汇的所有文档"""
        return self.documents
    
    def get_document_ids(self) -> List[int]:
        """获取包含该词汇的文档ID列表"""
        return [doc_id for doc_id, _ in self.documents]
    
    def __str__(self):
        return f"PostingList(df={self.document_frequency}, docs={self.documents})"


class InvertedIndex:
    """倒排索引：核心数据结构，支持快速检索"""
    
    def __init__(self):
        self.index = {}  # {term: PostingList}
        self.document_count = 0
        self.vocabulary = set()
        self.document_lengths = {}  # {doc_id: document_length}
    
    def build_index(self, documents_tokens: List[List[str]]) -> None:
        """从文档词汇列表构建倒排索引"""
        self.document_count = len(documents_tokens)
        self.index = {}
        self.vocabulary = set()
        self.document_lengths = {}
        
        print(f"开始构建倒排索引，共{self.document_count}个文档...")
        
        for doc_id, tokens in enumerate(documents_tokens):
            # 记录文档长度
            self.document_lengths[doc_id] = len(tokens)
            
            # 计算词频
            term_freq = {}
            for token in tokens:
                term_freq[token] = term_freq.get(token, 0) + 1
                self.vocabulary.add(token)
            
            # 更新倒排索引
            for term, freq in term_freq.items():
                if term not in self.index:
                    self.index[term] = PostingList()
                self.index[term].add_document(doc_id, freq)
            
            # 显示进度
            if (doc_id + 1) % 100 == 0:
                print(f"已处理 {doc_id + 1}/{self.document_count} 个文档")
        
        print(f"倒排索引构建完成！")
        print(f"词汇表大小: {len(self.vocabulary)}")
        print(f"索引条目数: {len(self.index)}")
    
    def get_posting_list(self, term: str) -> PostingList:
        """获取词汇的倒排列表"""
        return self.index.get(term, PostingList())
    
    def get_documents_containing_term(self, term: str) -> List[int]:
        """获取包含指定词汇的文档ID列表"""
        posting_list = self.get_posting_list(term)
        return posting_list.get_document_ids()
    
    def get_term_frequency_in_document(self, term: str, doc_id: int) -> int:
        """获取词汇在指定文档中的频率"""
        posting_list = self.get_posting_list(term)
        for document_id, freq in posting_list.get_documents():
            if document_id == doc_id:
                return freq
        return 0
    
    def get_document_length(self, doc_id: int) -> int:
        """获取文档长度"""
        return self.document_lengths.get(doc_id, 0)
    
    def search_term(self, term: str) -> List[Tuple[int, int]]:
        """搜索单个词汇，返回[(doc_id, term_frequency), ...]"""
        posting_list = self.get_posting_list(term)
        return posting_list.get_documents()
    
    def search_and(self, terms: List[str]) -> List[int]:
        """AND搜索：返回包含所有词汇的文档ID"""
        if not terms:
            return []
        
        # 获取每个词汇的文档列表
        doc_sets = []
        for term in terms:
            doc_ids = set(self.get_documents_containing_term(term))
            doc_sets.append(doc_ids)
        
        # 求交集
        result = doc_sets[0]
        for doc_set in doc_sets[1:]:
            result = result.intersection(doc_set)
        
        return list(result)
    
    def search_or(self, terms: List[str]) -> List[int]:
        """OR搜索：返回包含任意词汇的文档ID"""
        if not terms:
            return []
        
        result_set = set()
        for term in terms:
            doc_ids = self.get_documents_containing_term(term)
            result_set.update(doc_ids)
        
        return list(result_set)
    
    def get_index_stats(self) -> Dict[str, any]:
        """获取索引统计信息"""
        if not self.index:
            return {}
        
        posting_list_sizes = [len(posting_list.documents) for posting_list in self.index.values()]
        
        return {
            "文档总数": self.document_count,
            "词汇总数": len(self.vocabulary),
            "索引条目数": len(self.index),
            "平均倒排列表长度": sum(posting_list_sizes) / len(posting_list_sizes),
            "最长倒排列表": max(posting_list_sizes),
            "最短倒排列表": min(posting_list_sizes),
            "总文档长度": sum(self.document_lengths.values()),
            "平均文档长度": sum(self.document_lengths.values()) / len(self.document_lengths)
        }
    
    def save_index(self, filepath: str) -> None:
        """保存索引到文件"""
        index_data = {
            'index': self.index,
            'document_count': self.document_count,
            'vocabulary': self.vocabulary,
            'document_lengths': self.document_lengths
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(index_data, f)
        print(f"索引已保存到: {filepath}")
    
    def load_index(self, filepath: str) -> None:
        """从文件加载索引"""
        with open(filepath, 'rb') as f:
            index_data = pickle.load(f)
        
        self.index = index_data['index']
        self.document_count = index_data['document_count']
        self.vocabulary = index_data['vocabulary']
        self.document_lengths = index_data['document_lengths']
        print(f"索引已从文件加载: {filepath}")


# 测试代码
if __name__ == "__main__":
    # 测试倒排索引
    print("=== 倒排索引测试 ===")
    
    # 测试文档集合
    documents = [
        ["apple", "banana", "cherry", "apple"],
        ["banana", "date", "elderberry"],
        ["apple", "cherry", "fig", "apple", "apple"],
        ["banana", "apple", "grape"],
        ["date", "elderberry", "fig", "grape", "cherry"]
    ]
    
    print("测试文档集合:")
    for i, doc in enumerate(documents):
        print(f"文档{i}: {doc}")
    
    # 构建倒排索引
    inverted_index = InvertedIndex()
    inverted_index.build_index(documents)
    
    # 显示索引统计
    print(f"\n=== 索引统计 ===")
    stats = inverted_index.get_index_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    # 测试词汇搜索
    print(f"\n=== 词汇搜索测试 ===")
    test_terms = ["apple", "banana", "xyz"]
    
    for term in test_terms:
        results = inverted_index.search_term(term)
        print(f"搜索 '{term}': {results}")
        
        posting_list = inverted_index.get_posting_list(term)
        print(f"  倒排列表: {posting_list}")
    
    # 测试布尔搜索
    print(f"\n=== 布尔搜索测试 ===")
    and_terms = ["apple", "banana"]
    or_terms = ["fig", "grape"]
    
    and_results = inverted_index.search_and(and_terms)
    or_results = inverted_index.search_or(or_terms)
    
    print(f"AND搜索 {and_terms}: 文档 {and_results}")
    print(f"OR搜索 {or_terms}: 文档 {or_results}")
    
    # 测试文档信息查询
    print(f"\n=== 文档信息查询 ===")
    for doc_id in range(min(3, len(documents))):
        length = inverted_index.get_document_length(doc_id)
        apple_freq = inverted_index.get_term_frequency_in_document("apple", doc_id)
        print(f"文档{doc_id}: 长度={length}, 'apple'频率={apple_freq}")