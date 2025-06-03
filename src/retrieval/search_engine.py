import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from typing import List, Dict, Any
from preprocessing.data_loader import DataLoader
from preprocessing.document_processor import DocumentProcessor
from retrieval.query_processor import EnhancedQueryProcessor, SearchResult
import time

class EnhancedSearchEngine:
    """增强搜索引擎：整合所有优化算法，提供完整的搜索功能"""
    
    def __init__(self, data_file_path: str, config: Dict[str, Any] = None):
        """
        初始化增强搜索引擎
        
        Args:
            data_file_path: 数据文件路径
            config: 配置参数，包含算法开关和参数设置
        """
        self.data_file_path = data_file_path
        self.data_loader = DataLoader(data_file_path)
        self.document_processor = DocumentProcessor()
        
        # 配置参数
        if config is None:
            config = {
                'use_bm25': True,
                'use_temporal': True,
                'use_multi_field': True,
                'temporal_weight': 0.2,
                'title_weight': 3.0,
                'summary_weight': 2.0,
                'content_weight': 1.0
            }
        
        self.config = config
        self.query_processor = EnhancedQueryProcessor(
            use_bm25=config.get('use_bm25', True),
            use_temporal=config.get('use_temporal', True),
            use_multi_field=config.get('use_multi_field', True)
        )
        
        self.documents = []
        self.is_initialized = False
        self.index_build_time = 0
    
    def initialize(self) -> bool:
        """初始化搜索引擎：加载数据、处理文档、构建索引"""
        print("=" * 50)
        print("初始化增强搜索引擎...")
        print("=" * 50)
        
        start_time = time.time()
        
        try:
            # 1. 加载数据
            print("\n步骤1: 加载数据")
            articles = self.data_loader.load_articles()
            if not articles:
                print("❌ 错误：无法加载文章数据")
                return False
            
            # 2. 处理文档
            print("\n步骤2: 处理文档")
            self.documents = self.document_processor.process_articles(articles)
            if not self.documents:
                print("❌ 错误：文档处理失败")
                return False
            
            # 3. 初始化增强查询处理器
            print("\n步骤3: 构建增强索引和模型")
            self.query_processor.initialize(self.documents)
            
            self.index_build_time = time.time() - start_time
            self.is_initialized = True
            
            print(f"\n✅ 增强搜索引擎初始化完成！")
            print(f"⏱️ 总耗时: {self.index_build_time:.2f} 秒")
            self._print_system_stats()
            
            return True
            
        except Exception as e:
            print(f"❌ 初始化过程中出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def search(self, query: str, top_k: int = 10, algorithm: str = "enhanced") -> List[SearchResult]:
        """
        执行搜索
        
        Args:
            query: 查询字符串
            top_k: 返回结果数量
            algorithm: 搜索算法 ('tfidf', 'bm25', 'enhanced')
        """
        if not self.is_initialized:
            print("❌ 错误：搜索引擎未初始化")
            return []
        
        if not query.strip():
            print("❌ 错误：查询不能为空")
            return []
        
        print(f"\n🔍 搜索查询: '{query}' (算法: {algorithm})")
        start_time = time.time()
        
        try:
            results = self.query_processor.search(query, top_k, algorithm)
            search_time = time.time() - start_time
            
            print(f"⚡ 搜索完成，耗时: {search_time:.3f} 秒")
            print(f"📊 找到 {len(results)} 个相关结果")
            
            return results
            
        except Exception as e:
            print(f"❌ 搜索过程中出错: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def compare_algorithms(self, query: str, top_k: int = 5) -> Dict[str, List[SearchResult]]:
        """比较不同算法的搜索结果"""
        if not self.is_initialized:
            print("❌ 错误：搜索引擎未初始化")
            return {}
        
        algorithms = ["tfidf", "bm25", "enhanced"]
        results = {}
        
        print(f"\n🔬 算法比较分析: '{query}'")
        print("=" * 60)
        
        for algorithm in algorithms:
            start_time = time.time()
            search_results = self.search(query, top_k, algorithm)
            search_time = time.time() - start_time
            
            results[algorithm] = search_results
            
            print(f"\n{algorithm.upper()} 算法:")
            print(f"  耗时: {search_time:.3f} 秒")
            print(f"  结果数: {len(search_results)}")
            if search_results:
                print(f"  最高分: {search_results[0].similarity:.3f}")
                print(f"  前3结果: {[r.title[:30] + '...' for r in search_results[:3]]}")
        
        return results
    
    def display_results(self, results: List[SearchResult], show_snippet: bool = True, 
                       show_scores: bool = False) -> None:
        """显示搜索结果"""
        if not results:
            print("❌ 没有找到相关结果")
            return
        
        print("\n" + "=" * 80)
        print(f"🎯 搜索结果 (共 {len(results)} 条)")
        print("=" * 80)
        
        for i, result in enumerate(results):
            print(f"\n【结果 {i+1}】")
            print(f"📊 综合相关度: {result.similarity:.3f}")
            print(f"📰 标题: {result.title}")
            print(f"🌐 URL: {result.url}")
            print(f"📅 发布时间: {result.publish_time}")
            print(f"🔤 匹配词汇: {', '.join(result.matched_terms)}")
            
            if show_scores:
                print(f"📈 详细分数:")
                print(f"   内容相关性: {result.content_score:.3f}")
                if result.temporal_score > 0:
                    print(f"   时间新鲜度: {result.temporal_score:.3f}")
                if result.field_scores:
                    print(f"   字段分数: {result.field_scores}")
            
            if show_snippet and result.snippet:
                print(f"📝 内容摘要: {result.snippet}")
            
            print("-" * 80)
    
    def display_comparison_results(self, comparison_results: Dict[str, List[SearchResult]]) -> None:
        """显示算法比较结果"""
        print(f"\n{'='*80}")
        print("🔬 算法比较结果")
        print(f"{'='*80}")
        
        # 显示每个算法的前3个结果
        for algorithm, results in comparison_results.items():
            print(f"\n🧮 {algorithm.upper()} 算法结果:")
            if results:
                for i, result in enumerate(results[:3]):
                    print(f"  {i+1}. {result.title[:50]}... (分数: {result.similarity:.3f})")
            else:
                print("  无结果")
        
        # 分析结果差异
        print(f"\n📊 结果分析:")
        if len(comparison_results) >= 2:
            algorithms = list(comparison_results.keys())
            for i in range(len(algorithms)):
                for j in range(i+1, len(algorithms)):
                    alg1, alg2 = algorithms[i], algorithms[j]
                    results1 = comparison_results[alg1]
                    results2 = comparison_results[alg2]
                    
                    if results1 and results2:
                        # 计算排序相关性
                        top_docs1 = set(r.doc_id for r in results1[:3])
                        top_docs2 = set(r.doc_id for r in results2[:3])
                        overlap = len(top_docs1.intersection(top_docs2))
                        
                        print(f"  {alg1} vs {alg2}: 前3结果重叠 {overlap}/3")
    
    def explain_result(self, query: str, doc_id: int, algorithm: str = "enhanced") -> Dict[str, Any]:
        """解释搜索结果"""
        if not self.is_initialized:
            return {}
        
        return self.query_processor.explain_search(query, doc_id, algorithm)
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        if not self.is_initialized:
            return {"状态": "未初始化"}
        
        # 获取数据统计
        data_stats = self.data_loader.get_article_info()
        doc_stats = self.document_processor.get_document_stats()
        model_stats = self.query_processor.get_model_info()
        
        return {
            "系统状态": "已初始化",
            "配置参数": self.config,
            "索引构建时间": f"{self.index_build_time:.2f} 秒",
            "数据统计": data_stats,
            "文档统计": doc_stats,
            "模型统计": model_stats
        }
    
    def _print_system_stats(self) -> None:
        """打印系统统计信息"""
        print("\n" + "=" * 50)
        print("📊 系统统计信息")
        print("=" * 50)
        
        info = self.get_system_info()
        
        for category, stats in info.items():
            if isinstance(stats, dict):
                print(f"\n📈 {category}:")
                for key, value in stats.items():
                    if isinstance(value, dict):
                        print(f"  {key}:")
                        for k, v in value.items():
                            if isinstance(v, float):
                                print(f"    {k}: {v:.3f}")
                            else:
                                print(f"    {k}: {v}")
                    elif isinstance(value, float):
                        print(f"  {key}: {value:.3f}")
                    elif isinstance(value, list):
                        print(f"  {key}: {', '.join(map(str, value))}")
                    else:
                        print(f"  {key}: {value}")
            else:
                print(f"📋 {category}: {stats}")
    
    def interactive_search(self) -> None:
        """交互式搜索界面"""
        if not self.is_initialized:
            print("❌ 请先初始化搜索引擎")
            return
        
        print("\n" + "=" * 60)
        print("🔍 NPR文章增强搜索引擎 - 交互模式")
        print("=" * 60)
        print("💡 输入查询词汇进行搜索")
        print("🎛️ 支持命令:")
        print("   • 'help' - 查看帮助信息")
        print("   • 'stats' - 查看系统统计")
        print("   • 'compare <查询>' - 比较不同算法")
        print("   • 'config' - 查看配置信息")
        print("   • 'quit' - 退出程序")
        
        while True:
            try:
                user_input = input("\n🔍 请输入查询或命令: ").strip()
                
                if user_input.lower() == 'quit':
                    print("👋 感谢使用，再见！")
                    break
                
                elif user_input.lower() == 'help':
                    self._show_help()
                
                elif user_input.lower() == 'stats':
                    self._print_system_stats()
                
                elif user_input.lower() == 'config':
                    self._show_config()
                
                elif user_input.lower().startswith('compare '):
                    query = user_input[8:].strip()
                    if query:
                        comparison_results = self.compare_algorithms(query, top_k=5)
                        self.display_comparison_results(comparison_results)
                    else:
                        print("❌ 请提供查询词汇，例如: compare climate change")
                
                elif user_input:
                    # 执行搜索
                    results = self.search(user_input, top_k=5, algorithm="enhanced")
                    self.display_results(results, show_snippet=True, show_scores=True)
                    
                    # 显示搜索统计
                    if results:
                        stats = self.query_processor.get_search_stats(results)
                        print(f"\n📊 搜索统计:")
                        for key, value in stats.items():
                            if isinstance(value, float):
                                print(f"  {key}: {value:.3f}")
                            else:
                                print(f"  {key}: {value}")
                    
                    # 询问是否需要解释
                    if results:
                        explain_input = input(f"\n❓ 是否需要解释第一个结果？(y/n): ").strip().lower()
                        if explain_input == 'y':
                            explanation = self.explain_result(user_input, results[0].doc_id)
                            self._print_explanation(explanation)
                
                else:
                    print("❌ 请输入有效的查询或命令")
                    
            except KeyboardInterrupt:
                print("\n\n👋 程序被用户中断，再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
    
    def _show_help(self) -> None:
        """显示帮助信息"""
        print("\n" + "=" * 50)
        print("📚 帮助信息")
        print("=" * 50)
        print("🔍 搜索功能:")
        print("  • 直接输入查询词汇进行搜索")
        print("  • 支持多个关键词，用空格分隔")
        print("  • 系统会自动处理大小写和标点符号")
        print("  • 支持英文词干提取")
        print("  • 结果按综合相关度排序")
        
        print("\n🎛️ 高级功能:")
        print("  • 使用BM25算法提升检索精度")
        print("  • 多字段权重：标题 > 摘要 > 内容")
        print("  • 时间新鲜度：新文章权重更高")
        print("  • 综合评分：内容相关性 + 时间新鲜度")
        
        print("\n⚙️ 命令:")
        print("  • 'compare <查询>' - 比较TF-IDF、BM25、增强算法")
        print("  • 'stats' - 显示详细系统统计信息")
        print("  • 'config' - 显示当前配置参数")
        print("  • 'help' - 显示此帮助信息")
        print("  • 'quit' - 退出程序")
    
    def _show_config(self) -> None:
        """显示配置信息"""
        print("\n" + "=" * 50)
        print("⚙️ 当前配置")
        print("=" * 50)
        
        for key, value in self.config.items():
            if isinstance(value, bool):
                status = "✅ 启用" if value else "❌ 禁用"
                print(f"  {key}: {status}")
            else:
                print(f"  {key}: {value}")
    
    def _print_explanation(self, explanation: Dict[str, Any]) -> None:
        """打印搜索结果解释"""
        print(f"\n" + "=" * 60)
        print("🔬 搜索结果详细解释")
        print("=" * 60)
        
        for key, value in explanation.items():
            if isinstance(value, dict):
                print(f"\n📊 {key}:")
                self._print_dict_recursive(value, indent=2)
            elif isinstance(value, list):
                print(f"{key}: {', '.join(map(str, value))}")
            elif isinstance(value, float):
                print(f"{key}: {value:.3f}")
            else:
                print(f"{key}: {value}")
    
    def _print_dict_recursive(self, d: Dict[str, Any], indent: int = 0) -> None:
        """递归打印字典"""
        prefix = " " * indent
        for key, value in d.items():
            if isinstance(value, dict):
                print(f"{prefix}{key}:")
                self._print_dict_recursive(value, indent + 2)
            elif isinstance(value, float):
                print(f"{prefix}{key}: {value:.3f}")
            elif isinstance(value, list):
                if len(value) <= 5:
                    print(f"{prefix}{key}: {value}")
                else:
                    print(f"{prefix}{key}: {value[:5]}... (共{len(value)}项)")
            else:
                print(f"{prefix}{key}: {value}")


# 测试代码
if __name__ == "__main__":
    print("=== 增强搜索引擎测试 ===")
    
    # 配置参数
    config = {
        'use_bm25': True,
        'use_temporal': True,
        'use_multi_field': True,
        'temporal_weight': 0.2,
        'title_weight': 3.0,
        'summary_weight': 2.0,
        'content_weight': 1.0
    }
    
    # 数据文件路径
    data_file = "../../data/npr_articles.json"
    
    # 检查文件是否存在
    if not os.path.exists(data_file):
        print(f"❌ 数据文件不存在: {data_file}")
        print("请确保NPR文章数据文件在正确的位置")
        exit(1)
    
    # 创建增强搜索引擎
    search_engine = EnhancedSearchEngine(data_file, config)
    
    # 初始化
    if search_engine.initialize():
        print("\n🎯 开始测试搜索功能...")
        
        # 测试搜索
        test_queries = [
            "climate change global warming",
            "health care medical treatment", 
            "education school students"
        ]
        
        for query in test_queries:
            print(f"\n{'='*80}")
            print(f"测试查询: '{query}'")
            print(f"{'='*80}")
            
            # 比较不同算法
            comparison_results = search_engine.compare_algorithms(query, top_k=3)
            search_engine.display_comparison_results(comparison_results)
            
            # 显示增强算法的详细结果
            print(f"\n🔍 增强算法详细结果:")
            enhanced_results = comparison_results.get('enhanced', [])
            search_engine.display_results(enhanced_results, show_snippet=True, show_scores=True)
        
        # 启动交互模式（可选）
        # search_engine.interactive_search()
    
    else:
        print("❌ 搜索引擎初始化失败")