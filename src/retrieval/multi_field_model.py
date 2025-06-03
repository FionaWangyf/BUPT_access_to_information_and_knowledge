from typing import List, Dict, Tuple, Any
from .bm25_model import BM25Model

class MultiFieldBM25Model:
    """多字段BM25模型：对标题、摘要、内容进行加权检索"""
    
    def __init__(self, field_weights: Dict[str, float] = None):
        """
        初始化多字段模型
        
        Args:
            field_weights: 字段权重配置
        """
        # 默认字段权重
        if field_weights is None:
            field_weights = {
                'title': 2.0,      # 标题权重最高
                'summary': 1.5,    # 摘要权重中等
                'content': 1.0     # 内容基准权重
            }
        
        self.field_weights = field_weights
        self.field_models = {}  # {field_name: BM25Model}
        self.documents = []  # 原始文档数据
        
        print(f"多字段BM25模型初始化")
        print(f"字段权重配置: {self.field_weights}")
    
    def build_model(self, documents: List[Any]) -> None:
        """
        构建多字段模型
        
        Args:
            documents: Document对象列表，包含processed_title, processed_summary, processed_content
        """
        self.documents = documents
        print(f"开始构建多字段BM25模型，共{len(documents)}个文档...")
        
        # 为每个字段构建独立的BM25模型
        field_documents = {
            'title': [],
            'summary': [],
            'content': []
        }
        
        # 提取各字段的词汇
        for doc in documents:
            field_documents['title'].append(doc.processed_title)
            field_documents['summary'].append(doc.processed_summary)
            field_documents['content'].append(doc.processed_content)
        
        # 为每个字段构建BM25模型
        for field_name, field_tokens_list in field_documents.items():
            if field_name in self.field_weights:
                print(f"\n构建 {field_name} 字段的BM25模型...")
                
                # 过滤空文档
                non_empty_docs = []
                for tokens in field_tokens_list:
                    if tokens:  # 非空
                        non_empty_docs.append(tokens)
                    else:  # 空文档，添加占位符
                        non_empty_docs.append([''])
                
                bm25_model = BM25Model(k1=1.5, b=0.75)
                bm25_model.build_model(non_empty_docs)
                self.field_models[field_name] = bm25_model
        
        print(f"\n多字段BM25模型构建完成！")
        self._print_model_summary()
    
    def _print_model_summary(self):
        """打印模型摘要信息"""
        print(f"\n=== 多字段模型摘要 ===")
        for field_name, model in self.field_models.items():
            stats = model.get_model_stats()
            print(f"{field_name} 字段:")
            print(f"  权重: {self.field_weights[field_name]}")
            print(f"  词汇表大小: {stats['vocabulary_size']}")
            print(f"  平均文档长度: {stats['average_document_length']:.1f}")
    
    def search(self, query_tokens: List[str], top_k: int = 10) -> List[Tuple[int, float, Dict[str, float]]]:
        """
        执行多字段搜索
        
        Returns:
            List of (doc_id, combined_score, field_scores)
        """
        if not query_tokens:
            return []
        
        print(f"执行多字段搜索，查询词汇: {query_tokens}")
        
        # 计算每个字段的分数
        field_scores = {}
        for field_name, model in self.field_models.items():
            scores = model.get_query_document_scores(query_tokens)
            field_scores[field_name] = scores
        
        # 合并分数
        combined_results = []
        doc_count = len(self.documents)
        
        for doc_id in range(doc_count):
            # 计算加权总分
            total_score = 0.0
            doc_field_scores = {}
            
            for field_name, scores in field_scores.items():
                field_score = scores[doc_id] if doc_id < len(scores) else 0.0
                weighted_score = field_score * self.field_weights[field_name]
                total_score += weighted_score
                doc_field_scores[field_name] = field_score
            
            combined_results.append((doc_id, total_score, doc_field_scores))
        
        # 按总分排序
        combined_results.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前top_k个结果
        return combined_results[:top_k]
    
    def explain_score(self, query_tokens: List[str], doc_id: int) -> Dict[str, Any]:
        """解释多字段分数计算"""
        if doc_id >= len(self.documents):
            return {}
        
        explanation = {
            'document_id': doc_id,
            'query_tokens': query_tokens,
            'field_weights': self.field_weights,
            'field_explanations': {},
            'field_scores': {},
            'weighted_scores': {},
            'total_score': 0.0
        }
        
        total_score = 0.0
        
        # 获取每个字段的详细解释
        for field_name, model in self.field_models.items():
            field_explanation = model.explain_score(query_tokens, doc_id)
            field_score = field_explanation.get('total_score', 0.0)
            weighted_score = field_score * self.field_weights[field_name]
            
            explanation['field_explanations'][field_name] = field_explanation
            explanation['field_scores'][field_name] = field_score
            explanation['weighted_scores'][field_name] = weighted_score
            
            total_score += weighted_score
        
        explanation['total_score'] = total_score
        return explanation
    
    def get_field_contributions(self, query_tokens: List[str], doc_id: int) -> Dict[str, float]:
        """获取各字段对总分的贡献比例"""
        explanation = self.explain_score(query_tokens, doc_id)
        
        total_score = explanation['total_score']
        if total_score == 0:
            return {field: 0.0 for field in self.field_weights}
        
        contributions = {}
        for field_name in self.field_weights:
            weighted_score = explanation['weighted_scores'].get(field_name, 0.0)
            contribution = weighted_score / total_score
            contributions[field_name] = contribution
        
        return contributions
    
    def compare_with_single_field(self, query_tokens: List[str], 
                                doc_id: int) -> Dict[str, Any]:
        """比较多字段和单字段的效果"""
        multi_explanation = self.explain_score(query_tokens, doc_id)
        
        comparison = {
            'multi_field_score': multi_explanation['total_score'],
            'field_contributions': self.get_field_contributions(query_tokens, doc_id),
            'single_field_scores': {}
        }
        
        # 计算单独使用每个字段的分数
        for field_name, model in self.field_models.items():
            field_explanation = model.explain_score(query_tokens, doc_id)
            comparison['single_field_scores'][field_name] = field_explanation.get('total_score', 0.0)
        
        return comparison
    
    def optimize_field_weights(self, validation_queries: List[Tuple[List[str], List[int]]]) -> Dict[str, float]:
        """
        基于验证查询优化字段权重（简单版本）
        
        Args:
            validation_queries: List of (query_tokens, relevant_doc_ids)
        """
        print("开始字段权重优化...")
        
        # 测试不同的权重组合
        weight_combinations = [
            {'title': 1.0, 'summary': 1.0, 'content': 1.0},  # 基准
            {'title': 2.0, 'summary': 1.0, 'content': 1.0},  # 标题权重高
            {'title': 1.5, 'summary': 1.5, 'content': 1.0},  # 标题摘要权重高
            {'title': 3.0, 'summary': 2.0, 'content': 1.0},  # 更高权重
            {'title': 1.0, 'summary': 2.0, 'content': 1.0},  # 摘要权重高
        ]
        
        best_weights = self.field_weights
        best_score = 0.0
        
        for weights in weight_combinations:
            # 临时更新权重
            old_weights = self.field_weights.copy()
            self.field_weights = weights
            
            # 计算这组权重的性能
            total_precision = 0.0
            
            for query_tokens, relevant_docs in validation_queries:
                results = self.search(query_tokens, top_k=10)
                
                # 计算precision@5
                top_5_docs = [doc_id for doc_id, score, _ in results[:5]]
                relevant_in_top_5 = len(set(top_5_docs) & set(relevant_docs))
                precision = relevant_in_top_5 / min(5, len(top_5_docs))
                total_precision += precision
            
            avg_precision = total_precision / len(validation_queries)
            print(f"权重 {weights}: 平均Precision@5 = {avg_precision:.3f}")
            
            if avg_precision > best_score:
                best_score = avg_precision
                best_weights = weights.copy()
            
            # 恢复原权重
            self.field_weights = old_weights
        
        # 设置最佳权重
        self.field_weights = best_weights
        print(f"最佳权重: {best_weights}, 得分: {best_score:.3f}")
        
        return best_weights


# 测试代码
if __name__ == "__main__":
    print("=== 多字段BM25模型测试 ===")
    
    # 创建模拟Document类
    class MockDocument:
        def __init__(self, title_tokens, summary_tokens, content_tokens):
            self.processed_title = title_tokens
            self.processed_summary = summary_tokens
            self.processed_content = content_tokens
    
    # 测试数据
    test_documents = [
        MockDocument(
            ["climat", "chang", "global"],
            ["climat", "chang", "environment", "impact"],
            ["global", "warm", "climat", "chang", "carbon", "emiss", "environment"]
        ),
        MockDocument(
            ["health", "care", "medic"],
            ["health", "care", "hospit", "treatment"],
            ["medic", "treatment", "health", "care", "doctor", "patient", "hospit"]
        ),
        MockDocument(
            ["educ", "school", "student"],
            ["educ", "school", "teacher", "learn"],
            ["school", "student", "teacher", "educ", "learn", "classroom", "univers"]
        )
    ]
    
    # 构建多字段模型
    multi_field_model = MultiFieldBM25Model()
    multi_field_model.build_model(test_documents)
    
    # 测试搜索
    print(f"\n=== 搜索测试 ===")
    test_query = ["climat", "chang"]
    
    results = multi_field_model.search(test_query, top_k=3)
    
    print(f"查询: {test_query}")
    print(f"搜索结果:")
    for doc_id, total_score, field_scores in results:
        print(f"\n文档{doc_id}: 总分={total_score:.3f}")
        for field, score in field_scores.items():
            weight = multi_field_model.field_weights[field]
            weighted = score * weight
            print(f"  {field}: {score:.3f} × {weight} = {weighted:.3f}")
    
    # 详细解释最佳结果
    if results:
        best_doc_id = results[0][0]
        print(f"\n=== 最佳匹配文档{best_doc_id}的详细解释 ===")
        
        explanation = multi_field_model.explain_score(test_query, best_doc_id)
        print(f"总分: {explanation['total_score']:.3f}")
        
        for field_name, field_exp in explanation['field_explanations'].items():
            print(f"\n{field_name} 字段:")
            print(f"  原始分数: {field_exp.get('total_score', 0):.3f}")
            print(f"  权重: {multi_field_model.field_weights[field_name]}")
            print(f"  加权分数: {explanation['weighted_scores'][field_name]:.3f}")
        
        # 字段贡献分析
        contributions = multi_field_model.get_field_contributions(test_query, best_doc_id)
        print(f"\n字段贡献分析:")
        for field, contrib in contributions.items():
            print(f"  {field}: {contrib:.1%}")