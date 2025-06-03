import math
import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict

class VectorSpaceModel:
    """向量空间模型：将文档和查询表示为向量，计算TF-IDF权重"""
    
    def __init__(self):
        self.vocabulary = []  # 词汇表
        self.document_vectors = []  # 文档向量列表
        self.idf_weights = {}  # IDF权重
        self.document_count = 0
        self.document_norms = []  # 文档向量的模长
    
    def build_model(self, documents_tokens: List[List[str]]) -> None:
        """构建向量空间模型"""
        self.document_count = len(documents_tokens)
        print(f"开始构建向量空间模型，共{self.document_count}个文档...")
        
        # 1. 构建词汇表
        self._build_vocabulary(documents_tokens)
        
        # 2. 计算IDF权重
        self._calculate_idf_weights(documents_tokens)
        
        # 3. 构建文档向量
        self._build_document_vectors(documents_tokens)
        
        print(f"向量空间模型构建完成！")
        print(f"词汇表大小: {len(self.vocabulary)}")
        print(f"文档向量维度: {len(self.vocabulary)}")
    
    def _build_vocabulary(self, documents_tokens: List[List[str]]) -> None:
        """构建词汇表"""
        vocab_set = set()
        for tokens in documents_tokens:
            vocab_set.update(tokens)
        
        # 按字母顺序排序，保证一致性
        self.vocabulary = sorted(list(vocab_set))
        print(f"词汇表构建完成，包含{len(self.vocabulary)}个唯一词汇")
    
    def _calculate_idf_weights(self, documents_tokens: List[List[str]]) -> None:
        """计算IDF权重"""
        # 计算每个词汇的文档频率
        document_frequency = defaultdict(int)
        
        for tokens in documents_tokens:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                document_frequency[token] += 1
        
        # 计算IDF权重
        self.idf_weights = {}
        for term in self.vocabulary:
            df = document_frequency[term]
            if df > 0:
                self.idf_weights[term] = math.log(self.document_count / df)
            else:
                self.idf_weights[term] = 0
        
        print(f"IDF权重计算完成")
    
    def _calculate_tf(self, tokens: List[str]) -> Dict[str, float]:
        """计算TF权重（使用对数TF）"""
        tf_dict = {}
        term_freq = defaultdict(int)
        
        # 计算原始词频
        for token in tokens:
            term_freq[token] += 1
        
        # 计算对数TF
        for term, freq in term_freq.items():
            if freq > 0:
                tf_dict[term] = 1 + math.log(freq)
            else:
                tf_dict[term] = 0
        
        return tf_dict
    
    def _build_document_vectors(self, documents_tokens: List[List[str]]) -> None:
        """构建文档TF-IDF向量"""
        self.document_vectors = []
        self.document_norms = []
        
        for doc_id, tokens in enumerate(documents_tokens):
            # 计算TF权重
            tf_weights = self._calculate_tf(tokens)
            
            # 构建TF-IDF向量
            tfidf_vector = []
            for term in self.vocabulary:
                tf = tf_weights.get(term, 0)
                idf = self.idf_weights[term]
                tfidf = tf * idf
                tfidf_vector.append(tfidf)
            
            self.document_vectors.append(tfidf_vector)
            
            # 计算向量模长（用于余弦相似度）
            norm = math.sqrt(sum(x * x for x in tfidf_vector))
            self.document_norms.append(norm)
            
            if (doc_id + 1) % 100 == 0:
                print(f"已构建 {doc_id + 1}/{self.document_count} 个文档向量")
    
    def get_query_vector(self, query_tokens: List[str]) -> List[float]:
        """将查询转换为TF-IDF向量"""
        # 计算查询的TF权重
        tf_weights = self._calculate_tf(query_tokens)
        
        # 构建查询TF-IDF向量
        query_vector = []
        for term in self.vocabulary:
            tf = tf_weights.get(term, 0)
            idf = self.idf_weights.get(term, 0)
            tfidf = tf * idf
            query_vector.append(tfidf)
        
        return query_vector
    
    def get_document_vector(self, doc_id: int) -> List[float]:
        """获取指定文档的TF-IDF向量"""
        if 0 <= doc_id < len(self.document_vectors):
            return self.document_vectors[doc_id]
        return []
    
    def get_vector_info(self, vector: List[float]) -> Dict[str, any]:
        """获取向量的信息"""
        non_zero_count = sum(1 for x in vector if x > 0)
        vector_norm = math.sqrt(sum(x * x for x in vector))
        max_weight = max(vector) if vector else 0
        
        return {
            "向量维度": len(vector),
            "非零元素数": non_zero_count,
            "稀疏度": (len(vector) - non_zero_count) / len(vector) if vector else 0,
            "向量模长": vector_norm,
            "最大权重": max_weight
        }
    
    def get_top_terms_in_vector(self, vector: List[float], top_k: int = 10) -> List[Tuple[str, float]]:
        """获取向量中权重最高的前k个词汇"""
        term_weights = [(self.vocabulary[i], vector[i]) for i in range(len(vector)) if vector[i] > 0]
        term_weights.sort(key=lambda x: x[1], reverse=True)
        return term_weights[:top_k]
    
    def get_model_stats(self) -> Dict[str, any]:
        """获取模型统计信息"""
        if not self.document_vectors:
            return {}
        
        # 计算文档向量的统计信息
        all_weights = []
        for vector in self.document_vectors:
            all_weights.extend([w for w in vector if w > 0])
        
        avg_doc_norm = sum(self.document_norms) / len(self.document_norms)
        
        return {
            "文档数量": self.document_count,
            "词汇表大小": len(self.vocabulary),
            "向量维度": len(self.vocabulary),
            "平均文档向量模长": avg_doc_norm,
            "非零权重总数": len(all_weights),
            "平均权重": sum(all_weights) / len(all_weights) if all_weights else 0,
            "最大权重": max(all_weights) if all_weights else 0,
            "IDF权重范围": f"{min(self.idf_weights.values()):.3f} - {max(self.idf_weights.values()):.3f}"
        }


# 测试代码
if __name__ == "__main__":
    # 测试向量空间模型
    print("=== 向量空间模型测试 ===")
    
    # 测试文档集合
    documents = [
        ["apple", "banana", "cherry", "apple"],
        ["banana", "date", "elderberry"],
        ["apple", "cherry", "fig", "apple", "apple"],
        ["banana", "apple", "grape"],
        ["date", "elderberry", "fig", "grape", "cherry"],
        ["apple", "fruit", "healthy"],
        ["banana", "fruit", "yellow"],
        ["cherry", "red", "fruit"]
    ]
    
    print("测试文档集合:")
    for i, doc in enumerate(documents):
        print(f"文档{i}: {doc}")
    
    # 构建向量空间模型
    vsm = VectorSpaceModel()
    vsm.build_model(documents)
    
    # 显示模型统计
    print(f"\n=== 模型统计 ===")
    stats = vsm.get_model_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")
    
    # 显示前几个词汇的IDF权重
    print(f"\n=== IDF权重示例 ===")
    for i, term in enumerate(vsm.vocabulary[:10]):
        idf = vsm.idf_weights[term]
        print(f"{term}: {idf:.3f}")
    
    # 测试文档向量
    print(f"\n=== 文档向量测试 ===")
    test_doc_id = 0
    doc_vector = vsm.get_document_vector(test_doc_id)
    vector_info = vsm.get_vector_info(doc_vector)
    
    print(f"文档{test_doc_id}向量信息:")
    for key, value in vector_info.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")
    
    print(f"文档{test_doc_id}的前5个重要词汇:")
    top_terms = vsm.get_top_terms_in_vector(doc_vector, 5)
    for term, weight in top_terms:
        print(f"  {term}: {weight:.3f}")
    
    # 测试查询向量
    print(f"\n=== 查询向量测试 ===")
    test_query = ["apple", "fruit"]
    query_vector = vsm.get_query_vector(test_query)
    query_info = vsm.get_vector_info(query_vector)
    
    print(f"查询 '{test_query}' 向量信息:")
    for key, value in query_info.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")
    
    print(f"查询的重要词汇:")
    query_top_terms = vsm.get_top_terms_in_vector(query_vector, 5)
    for term, weight in query_top_terms:
        print(f"  {term}: {weight:.3f}")