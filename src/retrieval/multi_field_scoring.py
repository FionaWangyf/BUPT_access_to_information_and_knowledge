from typing import List, Dict, Any, Tuple
import math
from collections import defaultdict, Counter

class MultiFieldScoring:
    """多字段权重评分：为不同字段（标题、摘要、内容）分配不同权重"""
    
    def __init__(self, title_weight: float = 3.0, summary_weight: float = 2.0, content_weight: float = 1.0):
        """
        初始化多字段评分器
        
        Args:
            title_weight: 标题字段权重
            summary_weight: 摘要字段权重  
            content_weight: 内容字段权重
        """
        self.title_weight = title_weight
        self.summary_weight = summary_weight
        self.content_weight = content_weight
        
        # 归一化权重
        total_weight = title_weight + summary_weight + content_weight
        self.normalized_title_weight = title_weight / total_weight
        self.normalized_summary_weight = summary_weight / total_weight
        self.normalized_content_weight = content_weight / total_weight
        
        print(f"多字段权重设置:")
        print(f"  标题权重: {self.title_weight} (归一化: {self.normalized_title_weight:.3f})")
        print(f"  摘要权重: {self.summary_weight} (归一化: {self.normalized_summary_weight:.3f})")
        print(f"  内容权重: {self.content_weight} (归一化: {self.normalized_content_weight:.3f})")
    
    def calculate_field_scores_tfidf(self, query_tokens: List[str], documents: List[Any], 
                                   vector_space_model: Any) -> List[float]:
        """
        使用TF-IDF为多字段计算分数
        
        Args:
            query_tokens: 查询词汇列表
            documents: 文档对象列表
            vector_space_model: 向量空间模型
            
        Returns:
            多字段加权分数列表
        """
        multi_field_scores = []
        
        for doc_id, doc in enumerate(documents):
            # 为每个字段计算TF-IDF分数
            title_score = self._calculate_field_tfidf_score(
                query_tokens, doc.processed_title, vector_space_model
            )
            
            summary_score = self._calculate_field_tfidf_score(
                query_tokens, doc.processed_summary, vector_space_model
            )
            
            content_score = self._calculate_field_tfidf_score(
                query_tokens, doc.processed_content, vector_space_model
            )
            
            # 加权组合
            weighted_score = (
                self.normalized_title_weight * title_score +
                self.normalized_summary_weight * summary_score +
                self.normalized_content_weight * content_score
            )
            
            multi_field_scores.append(weighted_score)
        
        return multi_field_scores
    
    def calculate_field_scores_bm25(self, query_tokens: List[str], documents: List[Any], 
                                  bm25_models: Dict[str, Any]) -> List[float]:
        """
        使用BM25为多字段计算分数
        
        Args:
            query_tokens: 查询词汇列表
            documents: 文档对象列表
            bm25_models: 包含不同字段BM25模型的字典
                        {'title': BM25Model, 'summary': BM25Model, 'content': BM25Model}
            
        Returns:
            多字段加权BM25分数列表
        """
        multi_field_scores = []
        
        # 获取各字段的BM25分数
        title_scores = bm25_models['title'].get_query_document_scores(query_tokens) if 'title' in bm25_models else []
        summary_scores = bm25_models['summary'].get_query_document_scores(query_tokens) if 'summary' in bm25_models else []
        content_scores = bm25_models['content'].get_query_document_scores(query_tokens) if 'content' in bm25_models else []
        
        # 确保所有字段都有分数
        doc_count = len(documents)
        if not title_scores:
            title_scores = [0.0] * doc_count
        if not summary_scores:
            summary_scores = [0.0] * doc_count
        if not content_scores:
            content_scores = [0.0] * doc_count
        
        # 组合分数
        for i in range(doc_count):
            title_score = title_scores[i] if i < len(title_scores) else 0.0
            summary_score = summary_scores[i] if i < len(summary_scores) else 0.0
            content_score = content_scores[i] if i < len(content_scores) else 0.0
            
            # 加权组合
            weighted_score = (
                self.normalized_title_weight * title_score +
                self.normalized_summary_weight * summary_score +
                self.normalized_content_weight * content_score
            )
            
            multi_field_scores.append(weighted_score)
        
        return multi_field_scores
    
    def _calculate_field_tfidf_score(self, query_tokens: List[str], field_tokens: List[str], 
                                   vector_space_model: Any) -> float:
        """计算单个字段的TF-IDF分数"""
        if not query_tokens or not field_tokens:
            return 0.0
        
        # 计算字段的TF权重
        field_tf = self._calculate_tf_weights(field_tokens)
        
        # 计算查询的TF权重
        query_tf = self._calculate_tf_weights(query_tokens)
        
        score = 0.0
        
        # 计算查询词汇在字段中的TF-IDF分数
        for term in query_tokens:
            if term in vector_space_model.vocabulary:
                tf_field = field_tf.get(term, 0)
                tf_query = query_tf.get(term, 0)
                idf = vector_space_model.idf_weights.get(term, 0)
                
                # TF-IDF分数
                term_score = tf_field * tf_query * idf
                score += term_score
        
        return score
    
    def _calculate_tf_weights(self, tokens: List[str]) -> Dict[str, float]:
        """计算TF权重（对数TF）"""
        tf_dict = {}
        term_freq = Counter(tokens)
        
        for term, freq in term_freq.items():
            if freq > 0:
                tf_dict[term] = 1 + math.log(freq)
            else:
                tf_dict[term] = 0
        
        return tf_dict
    
    def calculate_field_coverage_bonus(self, query_tokens: List[str], documents: List[Any]) -> List[float]:
        """
        计算字段覆盖度奖励：查询词汇在多个字段中出现会得到奖励
        
        Args:
            query_tokens: 查询词汇列表
            documents: 文档对象列表
            
        Returns:
            字段覆盖度奖励分数列表
        """
        coverage_bonuses = []
        
        for doc in documents:
            bonus = 0.0
            
            for term in set(query_tokens):
                fields_containing_term = 0
                
                # 检查词汇在哪些字段中出现
                if term in doc.processed_title:
                    fields_containing_term += 1
                if term in doc.processed_summary:
                    fields_containing_term += 1
                if term in doc.processed_content:
                    fields_containing_term += 1
                
                # 多字段覆盖奖励
                if fields_containing_term >= 2:
                    bonus += 0.2 * fields_containing_term
                elif fields_containing_term == 1:
                    bonus += 0.1
            
            coverage_bonuses.append(bonus)
        
        return coverage_bonuses
    
    def analyze_field_importance(self, query_tokens: List[str], documents: List[Any]) -> Dict[str, Any]:
        """分析不同字段对查询的重要性"""
        field_stats = {
            'title': {'matches': 0, 'total_terms': 0},
            'summary': {'matches': 0, 'total_terms': 0},
            'content': {'matches': 0, 'total_terms': 0}
        }
        
        query_set = set(query_tokens)
        
        for doc in documents:
            # 标题统计
            title_matches = len(query_set.intersection(set(doc.processed_title)))
            field_stats['title']['matches'] += title_matches
            field_stats['title']['total_terms'] += len(doc.processed_title)
            
            # 摘要统计
            summary_matches = len(query_set.intersection(set(doc.processed_summary)))
            field_stats['summary']['matches'] += summary_matches
            field_stats['summary']['total_terms'] += len(doc.processed_summary)
            
            # 内容统计
            content_matches = len(query_set.intersection(set(doc.processed_content)))
            field_stats['content']['matches'] += content_matches
            field_stats['content']['total_terms'] += len(doc.processed_content)
        
        # 计算重要性指标
        analysis = {}
        for field, stats in field_stats.items():
            if stats['total_terms'] > 0:
                match_rate = stats['matches'] / len(documents)
                density = stats['matches'] / stats['total_terms'] if stats['total_terms'] > 0 else 0
                
                analysis[field] = {
                    'total_matches': stats['matches'],
                    'total_terms': stats['total_terms'],
                    'avg_matches_per_doc': match_rate,
                    'match_density': density,
                    'relative_importance': match_rate * density
                }
            else:
                analysis[field] = {
                    'total_matches': 0,
                    'total_terms': 0,
                    'avg_matches_per_doc': 0,
                    'match_density': 0,
                    'relative_importance': 0
                }
        
        return analysis
    
    def get_field_score_explanation(self, query_tokens: List[str], doc_index: int, 
                                  documents: List[Any], vector_space_model: Any) -> Dict[str, Any]:
        """解释多字段分数计算过程"""
        if doc_index >= len(documents):
            return {"错误": "文档索引超出范围"}
        
        doc = documents[doc_index]
        
        # 计算各字段分数
        title_score = self._calculate_field_tfidf_score(
            query_tokens, doc.processed_title, vector_space_model
        )
        summary_score = self._calculate_field_tfidf_score(
            query_tokens, doc.processed_summary, vector_space_model
        )
        content_score = self._calculate_field_tfidf_score(
            query_tokens, doc.processed_content, vector_space_model
        )
        
        # 计算加权分数
        weighted_score = (
            self.normalized_title_weight * title_score +
            self.normalized_summary_weight * summary_score +
            self.normalized_content_weight * content_score
        )
        
        # 计算字段覆盖度
        coverage_bonus = self.calculate_field_coverage_bonus(query_tokens, [doc])[0]
        
        return {
            "文档索引": doc_index,
            "文档标题": doc.title,
            "查询词汇": query_tokens,
            "字段分数": {
                "标题": {"原始分数": title_score, "权重": self.normalized_title_weight, "加权分数": self.normalized_title_weight * title_score},
                "摘要": {"原始分数": summary_score, "权重": self.normalized_summary_weight, "加权分数": self.normalized_summary_weight * summary_score},
                "内容": {"原始分数": content_score, "权重": self.normalized_content_weight, "加权分数": self.normalized_content_weight * content_score}
            },
            "总加权分数": weighted_score,
            "字段覆盖度奖励": coverage_bonus,
            "最终分数": weighted_score + coverage_bonus,
            "字段匹配情况": {
                "标题匹配词": list(set(query_tokens).intersection(set(doc.processed_title))),
                "摘要匹配词": list(set(query_tokens).intersection(set(doc.processed_summary))),
                "内容匹配词": list(set(query_tokens).intersection(set(doc.processed_content)))
            }
        }
    
    def optimize_field_weights(self, query_tokens: List[str], documents: List[Any]) -> Dict[str, float]:
        """根据查询和文档集合优化字段权重"""
        field_analysis = self.analyze_field_importance(query_tokens, documents)
        
        # 基于相对重要性调整权重
        title_importance = field_analysis['title']['relative_importance']
        summary_importance = field_analysis['summary']['relative_importance']
        content_importance = field_analysis['content']['relative_importance']
        
        total_importance = title_importance + summary_importance + content_importance
        
        if total_importance > 0:
            optimized_weights = {
                'title_weight': (title_importance / total_importance) * 5 + 1,  # 保证最小权重为1
                'summary_weight': (summary_importance / total_importance) * 3 + 0.5,
                'content_weight': (content_importance / total_importance) * 2 + 0.5
            }
        else:
            # 如果无法计算重要性，使用默认权重
            optimized_weights = {
                'title_weight': self.title_weight,
                'summary_weight': self.summary_weight,
                'content_weight': self.content_weight
            }
        
        return optimized_weights


# 测试代码
if __name__ == "__main__":
    print("=== 多字段权重评分测试 ===")
    
    # 创建模拟的Document类用于测试
    class MockDocument:
        def __init__(self, doc_id, title, summary, content):
            self.doc_id = doc_id
            self.title = title
            self.summary = summary
            self.content = content
            
            # 模拟处理后的词汇
            self.processed_title = title.lower().split()
            self.processed_summary = summary.lower().split()
            self.processed_content = content.lower().split()
    
    # 创建模拟的向量空间模型
    class MockVectorSpaceModel:
        def __init__(self):
            self.vocabulary = ["health", "apple", "fruit", "nutrition", "vitamin", "diet", "food", "benefit"]
            self.idf_weights = {term: 2.0 for term in self.vocabulary}  # 简化的IDF权重
    
    # 测试文档
    test_documents = [
        MockDocument(0, 
                    "Apple Health Benefits", 
                    "Apples are nutritious fruits with many health benefits",
                    "Apples contain vitamins and fiber. They are great for your diet and overall health. Eating apples daily can improve nutrition."),
        
        MockDocument(1,
                    "Nutrition Guide", 
                    "Complete guide to healthy nutrition and diet",
                    "A healthy diet includes fruits, vegetables, and balanced nutrition. Food choices affect your health significantly."),
        
        MockDocument(2,
                    "Fruit Comparison", 
                    "Comparing different fruits and their benefits",
                    "Different fruits offer various health benefits. Apples, oranges, and bananas all contribute to good nutrition.")
    ]
    
    # 初始化多字段评分器
    multi_field_scorer = MultiFieldScoring(title_weight=3.0, summary_weight=2.0, content_weight=1.0)
    
    # 测试查询
    test_query = ["apple", "health", "nutrition"]
    
    print(f"\n测试查询: {test_query}")
    
    # 模拟向量空间模型
    mock_vsm = MockVectorSpaceModel()
    
    # 计算多字段TF-IDF分数
    print(f"\n=== TF-IDF多字段分数 ===")
    tfidf_scores = multi_field_scorer.calculate_field_scores_tfidf(test_query, test_documents, mock_vsm)
    
    for i, (doc, score) in enumerate(zip(test_documents, tfidf_scores)):
        print(f"文档{i} '{doc.title}': {score:.3f}")
    
    # 计算字段覆盖度奖励
    print(f"\n=== 字段覆盖度奖励 ===")
    coverage_bonuses = multi_field_scorer.calculate_field_coverage_bonus(test_query, test_documents)
    
    for i, (doc, bonus) in enumerate(zip(test_documents, coverage_bonuses)):
        print(f"文档{i} '{doc.title}': {bonus:.3f}")
    
    # 分析字段重要性
    print(f"\n=== 字段重要性分析 ===")
    field_analysis = multi_field_scorer.analyze_field_importance(test_query, test_documents)
    
    for field, stats in field_analysis.items():
        print(f"{field}字段:")
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")
    
    # 获取详细解释
    print(f"\n=== 分数解释 (文档0) ===")
    explanation = multi_field_scorer.get_field_score_explanation(test_query, 0, test_documents, mock_vsm)
    
    for key, value in explanation.items():
        if key == "字段分数":
            print(f"{key}:")
            for field, scores in value.items():
                print(f"  {field}: {scores}")
        elif key == "字段匹配情况":
            print(f"{key}:")
            for field, matches in value.items():
                print(f"  {field}: {matches}")
        elif isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")
    
    # 测试权重优化
    print(f"\n=== 权重优化建议 ===")
    optimized_weights = multi_field_scorer.optimize_field_weights(test_query, test_documents)
    
    print("当前权重:")
    print(f"  标题: {multi_field_scorer.title_weight}")
    print(f"  摘要: {multi_field_scorer.summary_weight}")
    print(f"  内容: {multi_field_scorer.content_weight}")
    
    print("优化建议权重:")
    for field, weight in optimized_weights.items():
        print(f"  {field}: {weight:.3f}")