#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索诊断工具：分析查询处理和相似度计算
"""

import sys
import os
sys.path.append('src')

from src.retrieval.search_engine import SearchEngine
import json

class SearchDiagnostics:
    """搜索诊断工具：深入分析查询处理过程"""
    
    def __init__(self, search_engine: SearchEngine):
        self.search_engine = search_engine
    
    def diagnose_query(self, query: str):
        """诊断查询处理过程"""
        print(f"🔍 诊断查询: '{query}'")
        print("=" * 80)
        
        # 1. 查询预处理分析
        self._analyze_query_processing(query)
        
        # 2. 词汇分析
        self._analyze_vocabulary(query)
        
        # 3. 向量分析
        self._analyze_vectors(query)
        
        # 4. 相似度分析
        self._analyze_similarities(query)
    
    def _analyze_query_processing(self, query: str):
        """分析查询预处理"""
        print("\n📝 1. 查询预处理分析")
        print("-" * 40)
        
        processor = self.search_engine.query_processor.text_processor
        
        # 逐步处理
        print(f"原始查询: '{query}'")
        
        cleaned = processor.clean_text(query)
        print(f"清洗后: '{cleaned}'")
        
        tokens = processor.tokenize(cleaned)
        print(f"分词结果: {tokens}")
        
        no_stops = processor.remove_stopwords(tokens)
        print(f"去停用词: {no_stops}")
        
        stemmed = processor.stem_words(no_stops)
        print(f"词干提取: {stemmed}")
        
        final_tokens = processor.process_text(query)
        print(f"最终结果: {final_tokens}")
    
    def _analyze_vocabulary(self, query: str):
        """分析词汇表信息"""
        print("\n📚 2. 词汇表分析")
        print("-" * 40)
        
        query_tokens = self.search_engine.query_processor.process_query(query)
        vsm = self.search_engine.query_processor.vector_space_model
        
        print(f"查询词汇: {query_tokens}")
        print(f"词汇表大小: {len(vsm.vocabulary)}")
        
        for token in query_tokens:
            if token in vsm.vocabulary:
                vocab_index = vsm.vocabulary.index(token)
                idf_weight = vsm.idf_weights.get(token, 0)
                
                # 统计包含该词的文档数
                doc_count = 0
                for doc_vector in vsm.document_vectors:
                    if doc_vector[vocab_index] > 0:
                        doc_count += 1
                
                print(f"  词汇 '{token}':")
                print(f"    词汇表索引: {vocab_index}")
                print(f"    IDF权重: {idf_weight:.3f}")
                print(f"    出现在 {doc_count}/{len(vsm.document_vectors)} 个文档中")
            else:
                print(f"  词汇 '{token}': 不在词汇表中")
    
    def _analyze_vectors(self, query: str):
        """分析向量信息"""
        print("\n🔢 3. 向量分析")
        print("-" * 40)
        
        query_tokens = self.search_engine.query_processor.process_query(query)
        vsm = self.search_engine.query_processor.vector_space_model
        
        # 获取查询向量
        query_vector = vsm.get_query_vector(query_tokens)
        
        # 分析查询向量
        non_zero_count = sum(1 for x in query_vector if x > 0)
        query_norm = sum(x * x for x in query_vector) ** 0.5
        max_weight = max(query_vector) if query_vector else 0
        
        print(f"查询向量统计:")
        print(f"  向量维度: {len(query_vector)}")
        print(f"  非零元素: {non_zero_count}")
        print(f"  向量模长: {query_norm:.3f}")
        print(f"  最大权重: {max_weight:.3f}")
        
        # 显示非零元素
        print(f"  非零元素详情:")
        for i, weight in enumerate(query_vector):
            if weight > 0:
                term = vsm.vocabulary[i]
                print(f"    {term}: {weight:.3f}")
        
        # 分析几个文档向量
        print(f"\n前3个文档向量统计:")
        for doc_id in range(min(3, len(vsm.document_vectors))):
            doc_vector = vsm.document_vectors[doc_id]
            doc_norm = vsm.document_norms[doc_id]
            doc_nonzero = sum(1 for x in doc_vector if x > 0)
            
            print(f"  文档{doc_id}: 模长={doc_norm:.3f}, 非零={doc_nonzero}")
    
    def _analyze_similarities(self, query: str):
        """分析相似度计算"""
        print("\n📊 4. 相似度分析")
        print("-" * 40)
        
        # 执行搜索获取相似度
        results = self.search_engine.search(query, top_k=10)
        
        if not results:
            print("没有搜索结果")
            return
        
        similarities = [r.similarity for r in results]
        
        print(f"相似度统计:")
        print(f"  最高相似度: {max(similarities):.3f}")
        print(f"  最低相似度: {min(similarities):.3f}")
        print(f"  平均相似度: {sum(similarities)/len(similarities):.3f}")
        
        # 分析相似度分布
        ranges = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
        distribution = {f"{ranges[i]:.1f}-{ranges[i+1]:.1f}": 0 for i in range(len(ranges)-1)}
        
        for sim in similarities:
            for i in range(len(ranges)-1):
                if ranges[i] <= sim < ranges[i+1]:
                    range_key = f"{ranges[i]:.1f}-{ranges[i+1]:.1f}"
                    distribution[range_key] += 1
                    break
        
        print(f"  相似度分布:")
        for range_key, count in distribution.items():
            if count > 0:
                print(f"    {range_key}: {count} 个")
        
        # 详细分析最高相似度的文档
        best_result = results[0]
        print(f"\n最佳匹配文档分析:")
        print(f"  文档ID: {best_result.doc_id}")
        print(f"  相似度: {best_result.similarity:.3f}")
        print(f"  匹配词汇: {best_result.matched_terms}")
        print(f"  标题: {best_result.title[:100]}")
        
        # 计算点积分解
        query_tokens = self.search_engine.query_processor.process_query(query)
        vsm = self.search_engine.query_processor.vector_space_model
        query_vector = vsm.get_query_vector(query_tokens)
        doc_vector = vsm.get_document_vector(best_result.doc_id)
        
        # 计算点积贡献
        dot_product = sum(q * d for q, d in zip(query_vector, doc_vector))
        query_norm = sum(x * x for x in query_vector) ** 0.5
        doc_norm = vsm.document_norms[best_result.doc_id]
        
        print(f"  相似度计算详情:")
        print(f"    点积: {dot_product:.3f}")
        print(f"    查询向量模长: {query_norm:.3f}")
        print(f"    文档向量模长: {doc_norm:.3f}")
        print(f"    余弦相似度: {dot_product/(query_norm*doc_norm):.3f}")
    
    def suggest_improvements(self, query: str):
        """建议改进方案"""
        print("\n🚀 5. 改进建议")
        print("-" * 40)
        
        query_tokens = self.search_engine.query_processor.process_query(query)
        vsm = self.search_engine.query_processor.vector_space_model
        
        suggestions = []
        
        # 检查词汇覆盖
        missing_tokens = [token for token in query_tokens if token not in vsm.vocabulary]
        if missing_tokens:
            suggestions.append(f"词汇表缺失: {missing_tokens}")
        
        # 检查IDF权重
        low_idf_tokens = []
        for token in query_tokens:
            if token in vsm.idf_weights:
                if vsm.idf_weights[token] < 2.0:  # 较低的IDF
                    low_idf_tokens.append(token)
        
        if low_idf_tokens:
            suggestions.append(f"高频词汇(低IDF): {low_idf_tokens}")
        
        # 检查查询长度
        if len(query_tokens) < 3:
            suggestions.append("查询词汇较少，可考虑查询扩展")
        
        # 具体建议
        print("针对性改进建议:")
        print("1. 算法优化:")
        print("   - 使用BM25代替TF-IDF")
        print("   - 增加标题字段权重")
        print("   - 实现查询扩展")
        
        print("2. 预处理优化:")
        print("   - 调整词干提取策略")
        print("   - 优化停用词列表")
        print("   - 保留部分词形变化")
        
        print("3. 向量空间优化:")
        print("   - 降维技术(如LSA)")
        print("   - 词汇过滤(去除极高/低频词)")
        print("   - 归一化策略调整")
        
        if suggestions:
            print("4. 当前查询特定问题:")
            for suggestion in suggestions:
                print(f"   - {suggestion}")


def main():
    """主函数"""
    data_file = "data/npr_articles.json"
    
    if not os.path.exists(data_file):
        print(f"❌ 数据文件不存在: {data_file}")
        return
    
    # 初始化搜索引擎
    print("初始化搜索引擎...")
    search_engine = SearchEngine(data_file)
    if not search_engine.initialize():
        print("❌ 搜索引擎初始化失败")
        return
    
    # 创建诊断工具
    diagnostics = SearchDiagnostics(search_engine)
    
    # 诊断示例查询
    test_queries = [
        "climate change",
        "health care",
        "education policy",
        "technology innovation"
    ]
    
    for query in test_queries:
        diagnostics.diagnose_query(query)
        diagnostics.suggest_improvements(query)
        
        response = input(f"\n按回车继续下一个查询，输入'q'退出: ").strip()
        if response.lower() == 'q':
            break
        print("\n" + "="*100 + "\n")


if __name__ == "__main__":
    main()