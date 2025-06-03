import math
from typing import List, Dict, Tuple
from collections import defaultdict, Counter

class BM25Model:
    """BM25检索模型：更适合短查询和实际检索场景的算法"""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        初始化BM25模型
        
        Args:
            k1: 控制词频饱和度的参数 (1.2-2.0)
            b: 控制文档长度归一化的参数 (0.75)
        """
        self.k1 = k1
        self.b = b
        
        # 模型数据
        self.vocabulary = []
        self.document_frequencies = {}  # {term: df}
        self.document_lengths = []  # 每个文档的长度
        self.average_doc_length = 0
        self.document_count = 0
        self.document_term_frequencies = []  # 每个文档的词频字典
        
        # 预计算的IDF值
        self.idf_values = {}
    
    def build_model(self, documents_tokens: List[List[str]]) -> None:
        """构建BM25模型"""
        self.document_count = len(documents_tokens)
        print(f"开始构建BM25模型，共{self.document_count}个文档...")
        
        # 1. 构建词汇表和统计文档频率
        self._build_vocabulary_and_df(documents_tokens)
        
        # 2. 计算文档长度统计
        self._calculate_document_lengths(documents_tokens)
        
        # 3. 构建每个文档的词频统计
        self._build_document_term_frequencies(documents_tokens)
        
        # 4. 预计算IDF值
        self._calculate_idf_values()
        
        print(f"BM25模型构建完成！")
        print(f"词汇表大小: {len(self.vocabulary)}")
        print(f"平均文档长度: {self.average_doc_length:.1f}")
    
    def _build_vocabulary_and_df(self, documents_tokens: List[List[str]]) -> None:
        """构建词汇表并计算文档频率"""
        vocab_set = set()
        self.document_frequencies = defaultdict(int)
        
        for tokens in documents_tokens:
            unique_tokens = set(tokens)
            vocab_set.update(unique_tokens)
            
            # 统计文档频率
            for token in unique_tokens:
                self.document_frequencies[token] += 1
        
        self.vocabulary = sorted(list(vocab_set))
        print(f"词汇表构建完成，包含{len(self.vocabulary)}个唯一词汇")
    
    def _calculate_document_lengths(self, documents_tokens: List[List[str]]) -> None:
        """计算文档长度统计"""
        self.document_lengths = [len(tokens) for tokens in documents_tokens]
        self.average_doc_length = sum(self.document_lengths) / len(self.document_lengths)
        print(f"文档长度统计完成，平均长度: {self.average_doc_length:.1f}")
    
    def _build_document_term_frequencies(self, documents_tokens: List[List[str]]) -> None:
        """构建每个文档的词频统计"""
        self.document_term_frequencies = []
        
        for tokens in documents_tokens:
            tf_dict = dict(Counter(tokens))
            self.document_term_frequencies.append(tf_dict)
        
        print(f"文档词频统计完成")
    
    def _calculate_idf_values(self) -> None:
        """预计算所有词汇的IDF值"""
        self.idf_values = {}
        
        for term in self.vocabulary:
            df = self.document_frequencies[term]
            # BM25的IDF公式：log((N - df + 0.5) / (df + 0.5))
            idf = math.log((self.document_count - df + 0.5) / (df + 0.5))
            self.idf_values[term] = idf
        
        print(f"IDF值计算完成")
    
    def get_query_document_scores(self, query_tokens: List[str]) -> List[float]:
        """计算查询与所有文档的BM25分数"""
        scores = []
        
        for doc_id in range(self.document_count):
            score = self._calculate_bm25_score(query_tokens, doc_id)
            scores.append(score)
        
        return scores
    
    def _calculate_bm25_score(self, query_tokens: List[str], doc_id: int) -> float:
        """计算查询与特定文档的BM25分数"""
        score = 0.0
        doc_tf = self.document_term_frequencies[doc_id]
        doc_length = self.document_lengths[doc_id]
        
        # 对查询中的每个词汇计算BM25得分
        query_term_counts = Counter(query_tokens)
        
        for term, query_tf in query_term_counts.items():
            if term not in self.vocabulary:
                continue
            
            # 获取词汇在文档中的频率
            term_freq = doc_tf.get(term, 0)
            
            if term_freq == 0:
                continue
            
            # 获取IDF值
            idf = self.idf_values[term]
            
            # 计算BM25公式的TF部分
            tf_component = (term_freq * (self.k1 + 1)) / (
                term_freq + self.k1 * (
                    1 - self.b + self.b * (doc_length / self.average_doc_length)
                )
            )
            
            # BM25得分 = IDF * TF_component * query_term_frequency
            term_score = idf * tf_component * query_tf
            score += term_score
        
        return score
    
    def search(self, query_tokens: List[str], top_k: int = 10) -> List[Tuple[int, float]]:
        """执行BM25搜索"""
        if not query_tokens:
            return []
        
        # 计算所有文档的BM25分数
        scores = self.get_query_document_scores(query_tokens)
        
        # 创建(文档ID, 分数)对并排序
        doc_score_pairs = [(doc_id, score) for doc_id, score in enumerate(scores)]
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前top_k个结果
        return doc_score_pairs[:top_k]
    
    def explain_score(self, query_tokens: List[str], doc_id: int) -> Dict[str, any]:
        """解释BM25分数计算过程"""
        if doc_id >= self.document_count:
            return {}
        
        doc_tf = self.document_term_frequencies[doc_id]
        doc_length = self.document_lengths[doc_id]
        query_term_counts = Counter(query_tokens)
        
        explanation = {
            'document_id': doc_id,
            'document_length': doc_length,
            'average_doc_length': self.average_doc_length,
            'bm25_parameters': {'k1': self.k1, 'b': self.b},
            'term_scores': [],
            'total_score': 0.0
        }
        
        total_score = 0.0
        
        for term, query_tf in query_term_counts.items():
            if term not in self.vocabulary:
                continue
            
            term_freq = doc_tf.get(term, 0)
            if term_freq == 0:
                continue
            
            idf = self.idf_values[term]
            df = self.document_frequencies[term]
            
            # 计算TF组件
            tf_component = (term_freq * (self.k1 + 1)) / (
                term_freq + self.k1 * (
                    1 - self.b + self.b * (doc_length / self.average_doc_length)
                )
            )
            
            term_score = idf * tf_component * query_tf
            total_score += term_score
            
            explanation['term_scores'].append({
                'term': term,
                'query_tf': query_tf,
                'doc_tf': term_freq,
                'df': df,
                'idf': idf,
                'tf_component': tf_component,
                'term_score': term_score
            })
        
        explanation['total_score'] = total_score
        return explanation
    
    def get_model_stats(self) -> Dict[str, any]:
        """获取模型统计信息"""
        if not self.vocabulary:
            return {}
        
        idf_values = list(self.idf_values.values())
        doc_lengths = self.document_lengths
        
        return {
            'document_count': self.document_count,
            'vocabulary_size': len(self.vocabulary),
            'average_document_length': self.average_doc_length,
            'min_document_length': min(doc_lengths),
            'max_document_length': max(doc_lengths),
            'average_idf': sum(idf_values) / len(idf_values),
            'min_idf': min(idf_values),
            'max_idf': max(idf_values),
            'bm25_parameters': {
                'k1': self.k1,
                'b': self.b
            }
        }


# 测试代码
if __name__ == "__main__":
    # 测试BM25模型
    print("=== BM25模型测试 ===")
    
    # 测试数据
    documents = [
        ["apple", "banana", "cherry", "apple", "apple"],
        ["banana", "date", "elderberry"],
        ["apple", "cherry", "fig", "apple"],
        ["banana", "apple", "grape", "grape"],
        ["date", "elderberry", "fig", "grape", "cherry"],
        ["apple", "fruit", "healthy", "apple"],
        ["banana", "fruit", "yellow", "potassium"],
        ["cherry", "red", "fruit", "sweet"]
    ]
    
    print("测试文档集合:")
    for i, doc in enumerate(documents):
        print(f"文档{i}: {doc}")
    
    # 构建BM25模型
    bm25 = BM25Model(k1=1.5, b=0.75)
    bm25.build_model(documents)
    
    # 显示模型统计
    print(f"\n=== 模型统计 ===")
    stats = bm25.get_model_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        elif isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")
    
    # 测试搜索
    print(f"\n=== 搜索测试 ===")
    test_queries = [
        ["apple", "fruit"],
        ["banana"],
        ["cherry", "red"]
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        results = bm25.search(query, top_k=5)
        
        print(f"搜索结果:")
        for doc_id, score in results:
            if score > 0:
                print(f"  文档{doc_id}: BM25分数 = {score:.3f}")
        
        # 解释最佳结果
        if results and results[0][1] > 0:
            best_doc_id = results[0][0]
            explanation = bm25.explain_score(query, best_doc_id)
            
            print(f"\n最佳匹配文档{best_doc_id}的分数解释:")
            print(f"  文档长度: {explanation['document_length']}")
            print(f"  平均文档长度: {explanation['average_doc_length']:.1f}")
            print(f"  词汇得分详情:")
            for term_info in explanation['term_scores']:
                print(f"    {term_info['term']}: "
                     f"TF={term_info['doc_tf']}, "
                     f"IDF={term_info['idf']:.3f}, "
                     f"得分={term_info['term_score']:.3f}")
            print(f"  总分: {explanation['total_score']:.3f}")