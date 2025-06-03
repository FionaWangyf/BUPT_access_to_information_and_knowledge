
"""
NPR文章信息检索系统
集成BM25、多字段权重、时间新鲜度等优化算法
"""

import sys
import os
sys.path.append('src')

from src.retrieval.search_engine import EnhancedSearchEngine
import argparse
import json

def load_config(config_file: str = None) -> dict:
    """加载配置文件"""
    default_config = {
        'use_bm25': True,
        'use_temporal': True,
        'use_multi_field': True,
        'temporal_weight': 0.2,
        'temporal_decay_factor': 0.2,
        'temporal_max_days': 365,
        'title_weight': 3.0,
        'summary_weight': 2.0,
        'content_weight': 1.0,
        'bm25_k1': 1.5,
        'bm25_b': 0.75
    }
    
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            default_config.update(user_config)
            print(f"✅ 已加载配置文件: {config_file}")
        except Exception as e:
            print(f"⚠️ 配置文件加载失败，使用默认配置: {e}")
    
    return default_config

def print_welcome():
    """打印欢迎信息"""
    print("🚀" + "=" * 78 + "🚀")
    print("🔍" + " " * 20 + "NPR文章信息检索系统" + " " * 20 + "🔍")
    print("🚀" + "=" * 78 + "🚀")
    print("🎯 集成先进检索算法:")
    print("   • BM25算法 - 业界标准的概率检索模型")
    print("   • 多字段权重 - 标题、摘要、内容差异化评分")  
    print("   • 时间新鲜度 - 新文章优先推荐")
    print("   • 智能融合 - 多维度综合评分")
    print("🚀" + "=" * 78 + "🚀")

def main():
    """主函数"""
    print_welcome()
    
    # 设置数据文件路径
    data_file = "data/npr_articles.json"
    
    # 检查数据文件是否存在
    if not os.path.exists(data_file):
        print(f"❌ 错误：数据文件不存在 - {data_file}")
        print("请确保文章数据文件在data目录下")
        return
    
    # 加载配置
    config = load_config()
    
    # 创建增强搜索引擎
    search_engine = EnhancedSearchEngine(data_file, config)
    
    # 初始化搜索引擎
    print("\n🔧 正在初始化增强搜索引擎，请稍候...")
    if not search_engine.initialize():
        print("❌ 搜索引擎初始化失败")
        return
    
    print("\n✅ 增强搜索引擎初始化成功！")
    
    # 启动交互式搜索
    search_engine.interactive_search()

def demo_search():
    """演示搜索功能"""
    print_welcome()
    print("\n🎯 演示模式：预设查询测试")
    print("=" * 50)
    
    data_file = "data/npr_articles.json"
    
    if not os.path.exists(data_file):
        print(f"❌ 错误：数据文件不存在 - {data_file}")
        return
    
    # 加载配置
    config = load_config()
    
    # 创建和初始化搜索引擎
    search_engine = EnhancedSearchEngine(data_file, config)
    
    if not search_engine.initialize():
        print("❌ 搜索引擎初始化失败")
        return
    
    # 预设的演示查询
    demo_queries = [
        {
            "query": "climate change global warming",
            "description": "气候变化和全球变暖相关新闻"
        },
        {
            "query": "health care medical treatment", 
            "description": "医疗保健和治疗相关报道"
        },
        {
            "query": "education school students",
            "description": "教育和学校相关文章"
        },
        {
            "query": "politics government election",
            "description": "政治和政府选举新闻"
        },
        {
            "query": "technology artificial intelligence AI",
            "description": "科技和人工智能相关内容"
        },
        {
            "query": "economy financial market business",
            "description": "经济金融和商业报道"
        }
    ]
    
    print("\n🔍 开始演示搜索...")
    
    for i, demo in enumerate(demo_queries):
        query = demo["query"]
        description = demo["description"]
        
        print(f"\n{'='*90}")
        print(f"🎯 演示查询 {i+1}: '{query}'")
        print(f"📝 描述: {description}")
        print(f"{'='*90}")
        
        # 比较不同算法
        print(f"\n🔬 算法性能比较:")
        comparison_results = search_engine.compare_algorithms(query, top_k=3)
        search_engine.display_comparison_results(comparison_results)
        
        # 显示增强算法的详细结果
        print(f"\n🎯 增强算法详细结果:")
        enhanced_results = comparison_results.get('enhanced', [])
        search_engine.display_results(enhanced_results, show_snippet=True, show_scores=True)
        
        # 显示搜索统计
        if enhanced_results:
            stats = search_engine.query_processor.get_search_stats(enhanced_results)
            print(f"\n📊 搜索统计:")
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.3f}")
                else:
                    print(f"  {key}: {value}")
        
        # 询问是否继续
        if i < len(demo_queries) - 1:
            response = input(f"\n⏭️ 按回车继续下一个演示查询，输入'q'退出: ").strip()
            if response.lower() == 'q':
                break
    
    print("\n🎯 演示完成！")

def benchmark_algorithms():
    """算法性能基准测试"""
    print_welcome()
    print("\n🏁 算法性能基准测试")
    print("=" * 50)
    
    data_file = "data/npr_articles.json"
    
    if not os.path.exists(data_file):
        print(f"❌ 错误：数据文件不存在 - {data_file}")
        return
    
    # 加载配置
    config = load_config()
    
    # 创建搜索引擎
    search_engine = EnhancedSearchEngine(data_file, config)
    
    if not search_engine.initialize():
        print("❌ 搜索引擎初始化失败")
        return
    
    # 基准测试查询
    benchmark_queries = [
        "climate change",
        "health care",
        "education policy",
        "economic growth",
        "technology innovation",
        "political election",
        "scientific research",
        "social justice",
        "environmental protection",
        "public health"
    ]
    
    algorithms = ["tfidf", "bm25", "enhanced"]
    algorithm_stats = {alg: {"total_time": 0, "avg_scores": []} for alg in algorithms}
    
    print(f"\n🔬 开始基准测试 ({len(benchmark_queries)} 个查询)")
    
    for i, query in enumerate(benchmark_queries):
        print(f"\n测试查询 {i+1}/{len(benchmark_queries)}: '{query}'")
        
        for algorithm in algorithms:
            import time
            start_time = time.time()
            
            results = search_engine.search(query, top_k=10, algorithm=algorithm)
            
            end_time = time.time()
            search_time = end_time - start_time
            
            algorithm_stats[algorithm]["total_time"] += search_time
            
            if results:
                avg_score = sum(r.similarity for r in results) / len(results)
                algorithm_stats[algorithm]["avg_scores"].append(avg_score)
            
            print(f"  {algorithm:>8}: {search_time:.3f}s, {len(results)} 结果")
    
    # 显示基准测试结果
    print(f"\n{'='*60}")
    print("🏆 基准测试结果")
    print(f"{'='*60}")
    
    for algorithm, stats in algorithm_stats.items():
        avg_time = stats["total_time"] / len(benchmark_queries)
        avg_score = sum(stats["avg_scores"]) / len(stats["avg_scores"]) if stats["avg_scores"] else 0
        
        print(f"\n📊 {algorithm.upper()} 算法:")
        print(f"  平均响应时间: {avg_time:.3f} 秒")
        print(f"  平均相关度分数: {avg_score:.3f}")
        print(f"  总耗时: {stats['total_time']:.3f} 秒")

def create_sample_config():
    """创建示例配置文件"""
    config = {
        "use_bm25": True,
        "use_temporal": True,
        "use_multi_field": True,
        "temporal_weight": 0.2,
        "temporal_decay_factor": 0.2,
        "temporal_max_days": 365,
        "title_weight": 3.0,
        "summary_weight": 2.0,
        "content_weight": 1.0,
        "bm25_k1": 1.5,
        "bm25_b": 0.75
    }
    
    config_file = "config_sample.json"
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ 示例配置文件已创建: {config_file}")
        print("📝 你可以修改此文件来自定义搜索引擎参数")
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="NPR文章信息检索系统 - 增强版", 
                                   formatter_class=argparse.RawDescriptionHelpFormatter,
                                   epilog="""
示例用法:
  python main.py                           # 启动交互模式
  python main.py --demo                    # 运行演示模式
  python main.py --benchmark               # 运行性能基准测试
  python main.py --query "climate change" # 单次查询
  python main.py --config config.json     # 使用自定义配置
  python main.py --create-config          # 创建示例配置文件
                                   """)
    
    parser.add_argument("--demo", action="store_true", help="运行演示模式")
    parser.add_argument("--benchmark", action="store_true", help="运行算法性能基准测试")
    parser.add_argument("--query", type=str, help="直接执行单次查询")
    parser.add_argument("--algorithm", type=str, choices=["tfidf", "bm25", "enhanced"], 
                       default="enhanced", help="指定搜索算法")
    parser.add_argument("--config", type=str, help="指定配置文件路径")
    parser.add_argument("--top-k", type=int, default=10, help="返回结果数量")
    parser.add_argument("--create-config", action="store_true", help="创建示例配置文件")
    
    args = parser.parse_args()
    
    try:
        if args.create_config:
            create_sample_config()
            
        elif args.benchmark:
            benchmark_algorithms()
            
        elif args.demo:
            demo_search()
            
        elif args.query:
            # 单次查询模式
            data_file = "data/npr_articles.json"
            if not os.path.exists(data_file):
                print(f"❌ 错误：数据文件不存在 - {data_file}")
                sys.exit(1)
            
            config = load_config(args.config)
            search_engine = EnhancedSearchEngine(data_file, config)
            
            if search_engine.initialize():
                print(f"\n🔍 执行查询: '{args.query}' (算法: {args.algorithm})")
                results = search_engine.search(args.query, top_k=args.top_k, algorithm=args.algorithm)
                search_engine.display_results(results, show_snippet=True, show_scores=True)
                
                # 显示搜索统计
                if results:
                    stats = search_engine.query_processor.get_search_stats(results)
                    print(f"\n📊 搜索统计:")
                    for key, value in stats.items():
                        if isinstance(value, float):
                            print(f"  {key}: {value:.3f}")
                        else:
                            print(f"  {key}: {value}")
            else:
                print("❌ 搜索引擎初始化失败")
        else:
            # 默认交互模式
            main()
    
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断，再见！")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()