import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from typing import List, Dict, Tuple, Any
from preprocessing.text_processor import TextProcessor
from retrieval.vector_space_model import VectorSpaceModel
from retrieval.similarity_calculator import SimilarityCalculator
from retrieval.bm25_model import BM25Model
from retrieval.temporal_scoring import TemporalScoring
from retrieval.multi_field_scoring import MultiFieldScoring

class SearchResult:
    """搜索结果类：存储单个搜索结果的信息"""
    
    def __init__(self, doc_id: int, similarity: float, title: str = "", 
                 content: str = "", url: str = "", publish_time: str = ""):
        self.doc_id = doc_id
        self.similarity = similarity
        self.title = title
        self.content = content
        self.url = url
        self.publish_time = publish_time
        self.matched_terms = []  # 匹配的查询词汇
        self.snippet = ""  # 内容摘要片段
        
        # 新增的详细分数信息
        self.content_score = 0.0  # 内容相关性分数
        self.temporal_score = 0.0  # 时间新鲜度分数
        self.field_scores = {}  # 各字段分数
        self.score_explanation = {}  # 分数解释
    
    def __str__(self):
        return f"SearchResult(doc_id={self.doc_id}, similarity={self.similarity:.3f}, title='{self.title[:50]}...')"


class EnhancedQueryProcessor:
    """增强的查询处理器：整合BM25、多字段权重、时间新鲜度等优化算法"""
    
    def __init__(self, use_bm25: bool = True, use_temporal: bool = True, 
                 use_multi_field: bool = True):
        """
        初始化增强查询处理器
        
        Args:
            use_bm25: 是否使用BM25算法
            use_temporal: 是否使用时间新鲜度
            use_multi_field: 是否使用多字段权重
        """
        self.text_processor = TextProcessor()
        self.similarity_calculator = SimilarityCalculator()
        
        # 配置使用的算法
        self.use_bm25 = use_bm25
        self.use_temporal = use_temporal
        self.use_multi_field = use_multi_field
        
        # 模型组件
        self.vector_space_model = VectorSpaceModel()
        self.bm25_model = None
        self.bm25_field_models = {}  # 多字段BM25模型
        self.temporal_scorer = None
        self.multi_field_scorer = None
        
        # 数据
        self.documents = []
        self.is_ready = False
        
        print(f"增强查询处理器配置:")
        print(f"  BM25算法: {'✓' if use_bm25 else '✗'}")
        print(f"  时间新鲜度: {'✓' if use_temporal else '✗'}")
        print(f"  多字段权重: {'✓' if use_multi_field else '✗'}")
    
    def initialize(self, documents: List[Any]) -> None:
        """初始化查询处理器"""
        print("初始化增强查询处理器...")
        self.documents = documents
        
        # 提取文档的所有词汇
        documents_tokens = [doc.all_tokens for doc in documents]
        
        # 1. 构建向量空间模型
        print("构建向量空间模型...")
        self.vector_space_model.build_model(documents_tokens)
        
        # 2. 构建BM25模型
        if self.use_bm25:
            print("构建BM25模型...")
            self.bm25_model = BM25Model(k1=1.5, b=0.75)
            self.bm25_model.build_model(documents_tokens)
            
            # 构建多字段BM25模型
            if self.use_multi_field:
                print("构建多字段BM25模型...")
                self._build_multi_field_bm25_models()
        
        # 3. 初始化时间评分器
        if self.use_temporal:
            print("初始化时间评分器...")
            self.temporal_scorer = TemporalScoring(decay_factor=0.2, max_days=365)
            publish_times = [doc.publish_time for doc in documents]
            self.temporal_scorer.analyze_document_dates(publish_times)
        
        # 4. 初始化多字段评分器
        if self.use_multi_field:
            print("初始化多字段评分器...")
            self.multi_field_scorer = MultiFieldScoring(
                title_weight=3.0, summary_weight=2.0, content_weight=1.0
            )
        
        self.is_ready = True
        print("增强查询处理器初始化完成！")
    
    def _build_multi_field_bm25_models(self) -> None:
        """构建多字段BM25模型"""
        # 提取各字段的词汇
        title_tokens = [doc.processed_title for doc in self.documents]
        summary_tokens = [doc.processed_summary for doc in self.documents]
        content_tokens = [doc.processed_content for doc in self.documents]
        
        # 构建各字段的BM25模型
        if any(tokens for tokens in title_tokens):
            self.bm25_field_models['title'] = BM25Model(k1=1.2, b=0.75)
            self.bm25_field_models['title'].build_model(title_tokens)
        
        if any(tokens for tokens in summary_tokens):
            self.bm25_field_models['summary'] = BM25Model(k1=1.5, b=0.75)
            self.bm25_field_models['summary'].build_model(summary_tokens)
        
        if any(tokens for tokens in content_tokens):
            self.bm25_field_models['content'] = BM25Model(k1=1.8, b=0.75)
            self.bm25_field_models['content'].build_model(content_tokens)
        
        print(f"多字段BM25模型构建完成，包含字段: {list(self.bm25_field_models.keys())}")
    
    def process_query(self, query: str) -> List[str]:
        """处理查询字符串，返回处理后的词汇列表"""
        if not query.strip():
            return []
        
        query_tokens = self.text_processor.process_text(query)
        return query_tokens
    
    def search(self, query: str, top_k: int = 10, algorithm: str = "enhanced") -> List[SearchResult]:
        """
        执行搜索
        
        Args:
            query: 查询字符串
            top_k: 返回结果数量
            algorithm: 搜索算法 ('tfidf', 'bm25', 'enhanced')
            
        Returns:
            搜索结果列表
        """
        if not self.is_ready:
            raise Exception("查询处理器未初始化，请先调用initialize()方法")
        
        # 处理查询
        query_tokens = self.process_query(query)
        if not query_tokens:
            return []
        
        print(f"处理后的查询词汇: {query_tokens}")
        
        # 根据算法选择计算相似度
        if algorithm == "tfidf":
            similarities = self._calculate_tfidf_similarities(query_tokens)
        elif algorithm == "bm25":
            similarities = self._calculate_bm25_similarities(query_tokens)
        elif algorithm == "enhanced":
            similarities = self._calculate_enhanced_similarities(query_tokens)
        else:
            raise ValueError(f"不支持的算法: {algorithm}")
        
        # 获取Top-K结果
        top_docs = self.similarity_calculator.get_top_k_documents(similarities, top_k)
        
        # 创建搜索结果对象
        search_results = []
        for doc_id, similarity in top_docs:
            if similarity > 0:  # 只返回有相似度的结果
                result = self._create_search_result(query_tokens, doc_id, similarity)
                search_results.append(result)
        
        return search_results
    
    def _calculate_tfidf_similarities(self, query_tokens: List[str]) -> List[float]:
        """计算TF-IDF相似度"""
        query_vector = self.vector_space_model.get_query_vector(query_tokens)
        similarities = self.similarity_calculator.calculate_similarities(
            query_vector, self.vector_space_model.document_vectors, "cosine"
        )
        return similarities
    
    def _calculate_bm25_similarities(self, query_tokens: List[str]) -> List[float]:
        """计算BM25相似度"""
        if not self.bm25_model:
            return self._calculate_tfidf_similarities(query_tokens)
        
        bm25_scores = self.bm25_model.get_query_document_scores(query_tokens)
        
        # 归一化BM25分数到[0,1]范围
        if bm25_scores and max(bm25_scores) > 0:
            max_score = max(bm25_scores)
            similarities = [score / max_score for score in bm25_scores]
        else:
            similarities = bm25_scores
        
        return similarities
    
    def _calculate_enhanced_similarities(self, query_tokens: List[str]) -> List[float]:
        """计算增强的综合相似度"""
        # 1. 基础内容相关性分数
        if self.use_bm25 and self.bm25_model:
            content_scores = self._calculate_bm25_similarities(query_tokens)
        else:
            content_scores = self._calculate_tfidf_similarities(query_tokens)
        
        # 2. 多字段权重分数
        if self.use_multi_field and self.multi_field_scorer:
            if self.bm25_field_models:
                # 使用多字段BM25
                multi_field_scores = self.multi_field_scorer.calculate_field_scores_bm25(
                    query_tokens, self.documents, self.bm25_field_models
                )
            else:
                # 使用多字段TF-IDF
                multi_field_scores = self.multi_field_scorer.calculate_field_scores_tfidf(
                    query_tokens, self.documents, self.vector_space_model
                )
            
            # 归一化多字段分数
            if multi_field_scores and max(multi_field_scores) > 0:
                max_score = max(multi_field_scores)
                multi_field_scores = [score / max_score for score in multi_field_scores]
            
            # 结合基础分数和多字段分数
            content_scores = [
                0.6 * content + 0.4 * multi_field
                for content, multi_field in zip(content_scores, multi_field_scores)
            ]
        
        # 3. 时间新鲜度加权
        if self.use_temporal and self.temporal_scorer:
            document_indices = list(range(len(content_scores)))
            enhanced_scores = self.temporal_scorer.combine_content_and_temporal_scores(
                content_scores, document_indices, temporal_weight=0.2
            )
        else:
            enhanced_scores = content_scores
        
        return enhanced_scores
    
    def _create_search_result(self, query_tokens: List[str], doc_id: int, similarity: float) -> SearchResult:
        """创建搜索结果对象"""
        doc = self.documents[doc_id]
        
        result = SearchResult(
            doc_id=doc_id,
            similarity=similarity,
            title=doc.title,
            content=doc.content,
            url=doc.url,
            publish_time=doc.publish_time
        )
        
        # 添加匹配词汇信息
        result.matched_terms = self._find_matched_terms(query_tokens, doc.all_tokens)
        
        # 生成内容摘要片段
        result.snippet = self._generate_snippet(doc.content, query_tokens)
        
        # 计算详细分数信息
        self._calculate_detailed_scores(result, query_tokens)
        
        return result
    
    def _calculate_detailed_scores(self, result: SearchResult, query_tokens: List[str]) -> None:
        """计算详细的分数信息"""
        doc_id = result.doc_id
        
        # 内容相关性分数
        if self.use_bm25 and self.bm25_model:
            bm25_scores = self.bm25_model.get_query_document_scores(query_tokens)
            result.content_score = bm25_scores[doc_id] if doc_id < len(bm25_scores) else 0.0
        else:
            tfidf_similarities = self._calculate_tfidf_similarities(query_tokens)
            result.content_score = tfidf_similarities[doc_id] if doc_id < len(tfidf_similarities) else 0.0
        
        # 时间新鲜度分数
        if self.use_temporal and self.temporal_scorer:
            temporal_scores = self.temporal_scorer.calculate_temporal_scores([doc_id])
            result.temporal_score = temporal_scores[0] if temporal_scores else 0.0
        
        # 多字段分数
        if self.use_multi_field and self.multi_field_scorer:
            explanation = self.multi_field_scorer.get_field_score_explanation(
                query_tokens, doc_id, self.documents, self.vector_space_model
            )
            result.field_scores = explanation.get("字段分数", {})
    
    def _find_matched_terms(self, query_tokens: List[str], doc_tokens: List[str]) -> List[str]:
        """找到查询与文档中的匹配词汇"""
        query_set = set(query_tokens)
        doc_set = set(doc_tokens)
        matched = list(query_set.intersection(doc_set))
        return matched
    
    def _generate_snippet(self, content: str, query_tokens: List[str], max_length: int = 200) -> str:
        """生成包含查询词汇的内容摘要片段"""
        if not content or not query_tokens:
            return content[:max_length] + "..." if len(content) > max_length else content
        
        # 简单的摘要生成：寻找包含查询词汇的句子
        sentences = content.split('.')
        best_sentence = ""
        max_matches = 0
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            matches = sum(1 for token in query_tokens if token.lower() in sentence_lower)
            if matches > max_matches:
                max_matches = matches
                best_sentence = sentence.strip()
        
        # 如果找到包含查询词的句子，使用它；否则使用开头
        if best_sentence and max_matches > 0:
            snippet = best_sentence
        else:
            snippet = content[:max_length]
        
        # 确保摘要不超过最大长度
        if len(snippet) > max_length:
            snippet = snippet[:max_length] + "..."
        
        return snippet
    
    def get_search_stats(self, search_results: List[SearchResult]) -> Dict[str, Any]:
        """获取搜索结果统计信息"""
        if not search_results:
            return {"结果数量": 0}
        
        similarities = [result.similarity for result in search_results]
        content_scores = [result.content_score for result in search_results]
        temporal_scores = [result.temporal_score for result in search_results if result.temporal_score > 0]
        matched_terms_counts = [len(result.matched_terms) for result in search_results]
        
        stats = {
            "结果数量": len(search_results),
            "最高相似度": max(similarities),
            "最低相似度": min(similarities),
            "平均相似度": sum(similarities) / len(similarities),
            "平均内容分数": sum(content_scores) / len(content_scores) if content_scores else 0,
            "平均匹配词汇数": sum(matched_terms_counts) / len(matched_terms_counts),
            "有匹配词汇的结果数": sum(1 for count in matched_terms_counts if count > 0)
        }
        
        if temporal_scores:
            stats["平均时间分数"] = sum(temporal_scores) / len(temporal_scores)
            stats["最高时间分数"] = max(temporal_scores)
        
        return stats
    
    def explain_search(self, query: str, doc_id: int, algorithm: str = "enhanced") -> Dict[str, Any]:
        """解释搜索结果：显示查询与特定文档的匹配详情"""
        if not self.is_ready:
            return {}
        
        query_tokens = self.process_query(query)
        if not query_tokens or doc_id >= len(self.documents):
            return {}
        
        doc = self.documents[doc_id]
        explanation = {
            "查询": query,
            "处理后查询": query_tokens,
            "文档ID": doc_id,
            "文档标题": doc.title,
            "算法": algorithm
        }
        
        # 基础TF-IDF解释
        if self.vector_space_model:
            query_vector = self.vector_space_model.get_query_vector(query_tokens)
            doc_vector = self.vector_space_model.get_document_vector(doc_id)
            tfidf_similarity = self.similarity_calculator.cosine_similarity(query_vector, doc_vector)
            
            explanation["TF-IDF相似度"] = tfidf_similarity
        
        # BM25解释
        if self.use_bm25 and self.bm25_model:
            bm25_explanation = self.bm25_model.explain_score(query_tokens, doc_id)
            explanation["BM25详情"] = bm25_explanation
        
        # 多字段解释
        if self.use_multi_field and self.multi_field_scorer:
            multi_field_explanation = self.multi_field_scorer.get_field_score_explanation(
                query_tokens, doc_id, self.documents, self.vector_space_model
            )
            explanation["多字段详情"] = multi_field_explanation
        
        # 时间新鲜度解释
        if self.use_temporal and self.temporal_scorer:
            temporal_explanation = self.temporal_scorer.get_temporal_explanation(doc_id)
            explanation["时间新鲜度详情"] = temporal_explanation
        
        return explanation
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        if not self.is_ready:
            return {"状态": "未初始化"}
        
        info = {
            "状态": "已初始化",
            "使用的算法": [],
            "文档数量": len(self.documents)
        }
        
        if self.use_bm25:
            info["使用的算法"].append("BM25")
            if self.bm25_model:
                info["BM25统计"] = self.bm25_model.get_model_stats()
        
        if self.use_temporal:
            info["使用的算法"].append("时间新鲜度")
            if self.temporal_scorer:
                info["时间统计"] = self.temporal_scorer.get_temporal_stats()
        
        if self.use_multi_field:
            info["使用的算法"].append("多字段权重")
            if self.multi_field_scorer:
                info["多字段权重"] = {
                    "标题": self.multi_field_scorer.title_weight,
                    "摘要": self.multi_field_scorer.summary_weight,
                    "内容": self.multi_field_scorer.content_weight
                }
        
        if not info["使用的算法"]:
            info["使用的算法"].append("TF-IDF")
        
        return info


# 测试代码
if __name__ == "__main__":
    print("=== 增强查询处理器测试 ===")
    
    # 创建模拟的Document类用于测试
    class MockDocument:
        def __init__(self, doc_id, title, content, summary, publish_time):
            self.doc_id = doc_id
            self.title = title
            self.content = content
            self.summary = summary
            self.publish_time = publish_time
            self.url = f"http://example.com/doc{doc_id}"
            
            # 简化的文本处理
            self.processed_title = title.lower().split()
            self.processed_content = content.lower().split()
            self.processed_summary = summary.lower().split()
            self.all_tokens = self.processed_title + self.processed_content + self.processed_summary
    
    # 创建测试文档
    test_documents = [
        MockDocument(0, "Climate Change Effects", 
                    "Climate change is affecting global weather patterns and causing environmental challenges.",
                    "Global warming leads to climate change impacts",
                    "2025-05-30"),
        
        MockDocument(1, "Health Care Reform", 
                    "Health care systems need reform to provide better medical treatment for patients.",
                    "Medical care improvements and health system reforms",
                    "2025-05-15"),
        
        MockDocument(2, "Climate Science Research", 
                    "Scientists study climate change through research and data analysis of weather patterns.",
                    "Climate research and scientific weather analysis",
                    "2024-12-01"),
        
        MockDocument(3, "Healthcare Technology", 
                    "Technology improves healthcare delivery and medical treatment outcomes for patients.",
                    "Medical technology and healthcare innovation",
                    "2025-01-15")
    ]
    
    # 初始化增强查询处理器
    enhanced_processor = EnhancedQueryProcessor(use_bm25=True, use_temporal=True, use_multi_field=True)
    enhanced_processor.initialize(test_documents)
    
    # 测试搜索
    test_queries = ["climate change", "health care medical"]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"测试查询: '{query}'")
        print(f"{'='*80}")
        
        # 测试不同算法
        for algorithm in ["tfidf", "bm25", "enhanced"]:
            print(f"\n--- {algorithm.upper()} 算法 ---")
            results = enhanced_processor.search(query, top_k=3, algorithm=algorithm)
            
            for i, result in enumerate(results):
                print(f"结果{i+1}: {result.title}")
                print(f"  相似度: {result.similarity:.3f}")
                print(f"  内容分数: {result.content_score:.3f}")
                print(f"  时间分数: {result.temporal_score:.3f}")
                print(f"  匹配词汇: {result.matched_terms}")
        
        # 显示详细解释
        print(f"\n--- 详细解释 (第一个结果) ---")
        if results:
            explanation = enhanced_processor.explain_search(query, results[0].doc_id, "enhanced")
            print(f"文档: {explanation.get('文档标题', 'N/A')}")
            print(f"TF-IDF相似度: {explanation.get('TF-IDF相似度', 0):.3f}")
            
            if "BM25详情" in explanation:
                bm25_info = explanation["BM25详情"]
                print(f"BM25总分: {bm25_info.get('total_score', 0):.3f}")
            
            if "时间新鲜度详情" in explanation:
                temporal_info = explanation["时间新鲜度详情"]
                print(f"时间分数: {temporal_info.get('时间新鲜度分数', 0):.3f}")
                print(f"发布日期: {temporal_info.get('发布日期', 'N/A')}")
    
    # 显示模型信息
    print(f"\n{'='*80}")
    print("模型信息")
    print(f"{'='*80}")
    model_info = enhanced_processor.get_model_info()
    
    for key, value in model_info.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                if isinstance(v, float):
                    print(f"  {k}: {v:.3f}")
                else:
                    print(f"  {k}: {v}")
        elif isinstance(value, list):
            print(f"{key}: {', '.join(value)}")
        else:
            print(f"{key}: {value}")