import math
import numpy as np
from typing import List, Tuple

class SimilarityCalculator:
    """相似度计算器：计算查询与文档之间的相似度"""
    
    def __init__(self):
        pass
    
    def cosine_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """计算余弦相似度"""
        if len(vector1) != len(vector2):
            raise ValueError("向量维度不匹配")
        
        # 计算点积
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        
        # 计算向量模长
        norm1 = math.sqrt(sum(a * a for a in vector1))
        norm2 = math.sqrt(sum(b * b for b in vector2))
        
        # 避免除零
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def cosine_similarity_with_norms(self, vector1: List[float], vector2: List[float], 
                                   norm1: float, norm2: float) -> float:
        """使用预计算的模长计算余弦相似度（更高效）"""
        if len(vector1) != len(vector2):
            raise ValueError("向量维度不匹配")
        
        # 计算点积
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        
        # 避免除零
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def euclidean_distance(self, vector1: List[float], vector2: List[float]) -> float:
        """计算欧几里得距离"""
        if len(vector1) != len(vector2):
            raise ValueError("向量维度不匹配")
        
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(vector1, vector2)))
        return distance
    
    def manhattan_distance(self, vector1: List[float], vector2: List[float]) -> float:
        """计算曼哈顿距离"""
        if len(vector1) != len(vector2):
            raise ValueError("向量维度不匹配")
        
        distance = sum(abs(a - b) for a, b in zip(vector1, vector2))
        return distance
    
    def jaccard_similarity(self, tokens1: List[str], tokens2: List[str]) -> float:
        """计算Jaccard相似度（基于词汇集合）"""
        set1 = set(tokens1)
        set2 = set(tokens2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def dice_coefficient(self, tokens1: List[str], tokens2: List[str]) -> float:
        """计算Dice系数"""
        set1 = set(tokens1)
        set2 = set(tokens2)
        
        intersection = len(set1.intersection(set2))
        
        if len(set1) + len(set2) == 0:
            return 0.0
        
        return 2 * intersection / (len(set1) + len(set2))
    
    def calculate_similarities(self, query_vector: List[float], 
                             document_vectors: List[List[float]],
                             method: str = "cosine") -> List[float]:
        """批量计算查询与所有文档的相似度"""
        similarities = []
        
        if method == "cosine":
            # 预计算查询向量的模长
            query_norm = math.sqrt(sum(x * x for x in query_vector))
            
            for doc_vector in document_vectors:
                similarity = self.cosine_similarity(query_vector, doc_vector)
                similarities.append(similarity)
        
        elif method == "euclidean":
            for doc_vector in document_vectors:
                distance = self.euclidean_distance(query_vector, doc_vector)
                # 转换为相似度（距离越小，相似度越大）
                similarity = 1 / (1 + distance)
                similarities.append(similarity)
        
        elif method == "manhattan":
            for doc_vector in document_vectors:
                distance = self.manhattan_distance(query_vector, doc_vector)
                # 转换为相似度
                similarity = 1 / (1 + distance)
                similarities.append(similarity)
        
        else:
            raise ValueError(f"不支持的相似度计算方法: {method}")
        
        return similarities
    
    def rank_documents(self, similarities: List[float]) -> List[Tuple[int, float]]:
        """根据相似度对文档进行排序"""
        # 创建(文档ID, 相似度)的列表
        doc_similarity_pairs = [(i, sim) for i, sim in enumerate(similarities)]
        
        # 按相似度降序排序
        doc_similarity_pairs.sort(key=lambda x: x[1], reverse=True)
        
        return doc_similarity_pairs
    
    def get_top_k_documents(self, similarities: List[float], k: int = 10) -> List[Tuple[int, float]]:
        """获取相似度最高的前k个文档"""
        ranked_docs = self.rank_documents(similarities)
        return ranked_docs[:k]
    
    def calculate_similarity_stats(self, similarities: List[float]) -> dict:
        """计算相似度统计信息"""
        if not similarities:
            return {}
        
        non_zero_sims = [sim for sim in similarities if sim > 0]
        
        return {
            "总文档数": len(similarities),
            "非零相似度文档数": len(non_zero_sims),
            "最大相似度": max(similarities),
            "最小相似度": min(similarities),
            "平均相似度": sum(similarities) / len(similarities),
            "非零平均相似度": sum(non_zero_sims) / len(non_zero_sims) if non_zero_sims else 0,
            "相似度标准差": self._calculate_std(similarities)
        }
    
    def _calculate_std(self, values: List[float]) -> float:
        """计算标准差"""
        if len(values) <= 1:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)


# 测试代码
if __name__ == "__main__":
    # 测试相似度计算器
    print("=== 相似度计算测试 ===")
    
    sim_calc = SimilarityCalculator()
    
    # 测试向量
    vector1 = [1.0, 2.0, 3.0, 0.0, 1.0]
    vector2 = [2.0, 1.0, 0.0, 1.0, 2.0]
    vector3 = [1.0, 2.0, 3.0, 0.0, 1.0]  # 与vector1相同
    
    print(f"向量1: {vector1}")
    print(f"向量2: {vector2}")
    print(f"向量3: {vector3}")
    
    # 测试余弦相似度
    print(f"\n=== 余弦相似度测试 ===")
    cos_sim_12 = sim_calc.cosine_similarity(vector1, vector2)
    cos_sim_13 = sim_calc.cosine_similarity(vector1, vector3)
    cos_sim_23 = sim_calc.cosine_similarity(vector2, vector3)
    
    print(f"向量1与向量2: {cos_sim_12:.3f}")
    print(f"向量1与向量3: {cos_sim_13:.3f}")
    print(f"向量2与向量3: {cos_sim_23:.3f}")
    
    # 测试欧几里得距离
    print(f"\n=== 欧几里得距离测试 ===")
    eucl_dist_12 = sim_calc.euclidean_distance(vector1, vector2)
    eucl_dist_13 = sim_calc.euclidean_distance(vector1, vector3)
    
    print(f"向量1与向量2: {eucl_dist_12:.3f}")
    print(f"向量1与向量3: {eucl_dist_13:.3f}")
    
    # 测试曼哈顿距离
    print(f"\n=== 曼哈顿距离测试 ===")
    manh_dist_12 = sim_calc.manhattan_distance(vector1, vector2)
    manh_dist_13 = sim_calc.manhattan_distance(vector1, vector3)
    
    print(f"向量1与向量2: {manh_dist_12:.3f}")
    print(f"向量1与向量3: {manh_dist_13:.3f}")
    
    # 测试Jaccard相似度
    print(f"\n=== Jaccard相似度测试 ===")
    tokens1 = ["apple", "banana", "cherry"]
    tokens2 = ["banana", "cherry", "date"]
    tokens3 = ["apple", "banana", "cherry"]
    
    jaccard_12 = sim_calc.jaccard_similarity(tokens1, tokens2)
    jaccard_13 = sim_calc.jaccard_similarity(tokens1, tokens3)
    
    print(f"词汇集合1: {tokens1}")
    print(f"词汇集合2: {tokens2}")
    print(f"词汇集合3: {tokens3}")
    print(f"集合1与集合2: {jaccard_12:.3f}")
    print(f"集合1与集合3: {jaccard_13:.3f}")
    
    # 测试批量相似度计算
    print(f"\n=== 批量相似度计算测试 ===")
    query_vector = [1.0, 1.0, 1.0, 0.0, 0.0]
    document_vectors = [
        [2.0, 2.0, 2.0, 0.0, 0.0],  # 与查询向量方向相同
        [0.0, 0.0, 0.0, 1.0, 1.0],  # 与查询向量正交
        [1.0, 0.0, 0.0, 0.0, 0.0],  # 部分重叠
        [0.0, 0.0, 0.0, 0.0, 0.0],  # 零向量
    ]
    
    similarities = sim_calc.calculate_similarities(query_vector, document_vectors, "cosine")
    
    print(f"查询向量: {query_vector}")
    for i, (doc_vec, sim) in enumerate(zip(document_vectors, similarities)):
        print(f"文档{i} {doc_vec}: 相似度 {sim:.3f}")
    
    # 测试文档排序
    print(f"\n=== 文档排序测试 ===")
    ranked_docs = sim_calc.rank_documents(similarities)
    print("排序结果 (文档ID, 相似度):")
    for doc_id, sim in ranked_docs:
        print(f"  文档{doc_id}: {sim:.3f}")
    
    # 测试统计信息
    print(f"\n=== 相似度统计 ===")
    stats = sim_calc.calculate_similarity_stats(similarities)
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")