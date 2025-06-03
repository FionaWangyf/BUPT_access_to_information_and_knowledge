import math
from collections import Counter
from typing import List, Dict

class TermFrequencyCalculator:
    """词频计算器：计算TF（Term Frequency）值"""
    
    def __init__(self):
        pass
    
    def calculate_raw_tf(self, tokens: List[str]) -> Dict[str, int]:
        """计算原始词频（词汇在文档中出现的次数）"""
        return dict(Counter(tokens))
    
    def calculate_normalized_tf(self, tokens: List[str]) -> Dict[str, float]:
        """计算归一化词频（词频/文档总词数）"""
        if not tokens:
            return {}
        
        raw_tf = self.calculate_raw_tf(tokens)
        total_words = len(tokens)
        
        normalized_tf = {}
        for term, freq in raw_tf.items():
            normalized_tf[term] = freq / total_words
        
        return normalized_tf
    
    def calculate_log_tf(self, tokens: List[str]) -> Dict[str, float]:
        """计算对数词频（1 + log(词频)）"""
        raw_tf = self.calculate_raw_tf(tokens)
        
        log_tf = {}
        for term, freq in raw_tf.items():
            if freq > 0:
                log_tf[term] = 1 + math.log(freq)
            else:
                log_tf[term] = 0
        
        return log_tf
    
    def calculate_boolean_tf(self, tokens: List[str]) -> Dict[str, int]:
        """计算布尔词频（词汇存在为1，不存在为0）"""
        unique_tokens = set(tokens)
        return {term: 1 for term in unique_tokens}
    
    def get_tf_vector(self, tokens: List[str], vocabulary: List[str], 
                      tf_type: str = "log") -> List[float]:
        """
        获取文档的TF向量
        tf_type: "raw", "normalized", "log", "boolean"
        """
        if tf_type == "raw":
            tf_dict = self.calculate_raw_tf(tokens)
        elif tf_type == "normalized":
            tf_dict = self.calculate_normalized_tf(tokens)
        elif tf_type == "log":
            tf_dict = self.calculate_log_tf(tokens)
        elif tf_type == "boolean":
            tf_dict = self.calculate_boolean_tf(tokens)
        else:
            raise ValueError(f"不支持的TF类型: {tf_type}")
        
        # 构建向量
        tf_vector = []
        for term in vocabulary:
            tf_vector.append(tf_dict.get(term, 0))
        
        return tf_vector


# 测试代码
if __name__ == "__main__":
    # 测试词频计算器
    print("=== 词频计算测试 ===")
    
    tf_calculator = TermFrequencyCalculator()
    
    # 测试文档
    doc1_tokens = ["apple", "banana", "apple", "cherry", "apple"]
    doc2_tokens = ["banana", "cherry", "date", "banana"]
    
    print(f"文档1词汇: {doc1_tokens}")
    print(f"文档2词汇: {doc2_tokens}")
    
    # 测试不同类型的TF计算
    print(f"\n=== 文档1的TF计算 ===")
    raw_tf = tf_calculator.calculate_raw_tf(doc1_tokens)
    print(f"原始词频: {raw_tf}")
    
    norm_tf = tf_calculator.calculate_normalized_tf(doc1_tokens)
    print(f"归一化词频: {norm_tf}")
    
    log_tf = tf_calculator.calculate_log_tf(doc1_tokens)
    print(f"对数词频: {log_tf}")
    
    bool_tf = tf_calculator.calculate_boolean_tf(doc1_tokens)
    print(f"布尔词频: {bool_tf}")
    
    # 测试TF向量
    vocabulary = ["apple", "banana", "cherry", "date"]
    print(f"\n=== TF向量测试 ===")
    print(f"词汇表: {vocabulary}")
    
    tf_vector1 = tf_calculator.get_tf_vector(doc1_tokens, vocabulary, "log")
    tf_vector2 = tf_calculator.get_tf_vector(doc2_tokens, vocabulary, "log")
    
    print(f"文档1的TF向量: {tf_vector1}")
    print(f"文档2的TF向量: {tf_vector2}")