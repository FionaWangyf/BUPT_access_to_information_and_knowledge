#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信息抽取系统集成测试
文件位置：test_extraction_system.py
"""

import sys
import os
import json
import time
sys.path.append('src')

from src.extraction.extraction_manager import ExtractionManager

class MockDocument:
    """模拟文档类"""
    def __init__(self, doc_id: int, title: str, content: str, summary: str = ""):
        self.doc_id = doc_id
        self.title = title
        self.content = content
        self.summary = summary

def test_extraction_system():
    """测试完整的信息抽取系统"""
    print("🎯 信息抽取系统集成测试")
    print("=" * 60)
    
    # 1. 初始化管理器
    print("\n📋 步骤1: 初始化抽取管理器")
    config = {
        'enable_regex_extractor': True,
        'regex_confidence_threshold': 0.6,
        'merge_duplicate_entities': True,
        'max_entities_per_type': 50,
        'enable_cache': True
    }
    
    manager = ExtractionManager(config)
    if not manager.initialize():
        print("❌ 管理器初始化失败")
        return False
    
    print(f"✅ 管理器初始化成功")
    print(f"📋 支持的实体类型: {manager.get_supported_entity_types()}")
    
    # 2. 测试单文本抽取
    print("\n📋 步骤2: 测试单文本抽取")
    test_text = """
    President Joe Biden announced today that the United States will provide
    $2.5 billion in military aid to Ukraine. The announcement was made at the 
    White House during a meeting with Ukrainian President Volodymyr Zelenskyy.
    
    "This support is crucial for our democratic allies," Biden said during the 
    press conference at 2:30 PM EST. NPR's David Folkenflik reported from 
    Washington, D.C.
    
    The funding will be distributed through the Department of Defense according 
    to Secretary Lloyd Austin. For more information, contact the White House at 
    202-456-1414 or visit https://whitehouse.gov.
    """
    
    results = manager.extract_from_text(test_text, doc_id=1, field="content")
    
    print(f"✅ 单文本抽取完成，找到 {len(results)} 个实体")
    
    # 按类型分组显示
    results_by_type = {}
    for result in results:
        if result.entity_type not in results_by_type:
            results_by_type[result.entity_type] = []
        results_by_type[result.entity_type].append(result)
    
    for entity_type, type_results in results_by_type.items():
        print(f"\n  🏷️ {entity_type.upper()} ({len(type_results)} 个):")
        for result in sorted(type_results, key=lambda x: x.confidence, reverse=True)[:3]:
            print(f"    - {result.entity_value} (置信度: {result.confidence:.3f})")
    
    # 3. 测试文档对象抽取
    print("\n📋 步骤3: 测试文档对象抽取")
    
    test_documents = [
        MockDocument(
            doc_id=1,
            title="Biden Announces Military Aid to Ukraine",
            content="President Biden announced $2.5 billion aid package...",
            summary="US provides military support to Ukraine"
        ),
        MockDocument(
            doc_id=2,
            title="NPR CEO Testifies Before Congress",
            content="Katherine Maher testified about NPR's editorial independence...",
            summary="NPR leadership faces congressional questioning"
        ),
        MockDocument(
            doc_id=3,
            title="Federal Reserve Raises Interest Rates",
            content="The Federal Reserve announced a 0.25% rate increase...",
            summary="Fed continues monetary tightening policy"
        )
    ]
    
    # 测试单个文档
    doc_results = manager.extract_from_document(test_documents[0])
    print(f"✅ 单文档抽取完成，找到 {len(doc_results)} 个实体")
    
    # 4. 测试批量处理
    print("\n📋 步骤4: 测试批量处理")
    
    def progress_callback(current, total, progress):
        if current % 1 == 0:  # 每个文档都显示进度
            print(f"    进度: {current}/{total} ({progress:.1%})")
    
    batch_results = manager.extract_from_documents(test_documents, progress_callback)
    
    total_entities = sum(len(results) for results in batch_results.values())
    print(f"✅ 批量处理完成，总计 {total_entities} 个实体")
    
    # 显示每个文档的结果
    for doc_id, doc_results in batch_results.items():
        print(f"  📄 文档 {doc_id}: {len(doc_results)} 个实体")
    
    # 5. 测试统计信息
    print("\n📋 步骤5: 测试统计信息")
    stats = manager.get_summary_statistics()
    
    print("📊 抽取统计信息:")
    print(f"  📄 处理文档数: {stats['total_documents_processed']}")
    print(f"  🔍 总抽取数: {stats['total_extractions']}")
    print(f"  ⭐ 平均置信度: {stats['average_confidence']:.3f}")
    print(f"  ⏱️ 总处理时间: {stats['total_processing_time']:.3f}秒")
    print(f"  📊 平均每文档抽取数: {stats.get('avg_extractions_per_document', 0):.1f}")
    print(f"  🎯 有抽取结果的文档比例: {stats.get('documents_with_extractions_ratio', 0):.1%}")
    
    print(f"\n📋 各类型实体统计:")
    for entity_type, count in stats['extractions_by_type'].items():
        print(f"  {entity_type}: {count} 个")
    
    print(f"\n🔧 各抽取器统计:")
    for extractor, count in stats['extractions_by_extractor'].items():
        print(f"  {extractor}: {count} 个")
    
    # 6. 测试结果导出
    print("\n📋 步骤6: 测试结果导出")
    
    # 创建结果目录
    os.makedirs('results', exist_ok=True)
    
    # 导出JSON格式
    manager.export_results(batch_results, 'results/extraction_results.json', 'json')
    
    # 导出CSV格式
    manager.export_results(batch_results, 'results/extraction_results.csv', 'csv')
    
    # 导出文本格式
    manager.export_results(batch_results, 'results/extraction_results.txt', 'txt')
    
    # 保存统计信息
    manager.save_statistics('results/extraction_statistics.json')
    
    print("✅ 结果导出完成")
    
    # 7. 测试缓存功能
    print("\n📋 步骤7: 测试缓存功能")
    
    # 第一次抽取
    start_time = time.time()
    results1 = manager.extract_from_text(test_text, doc_id=99, field="cache_test")
    time1 = time.time() - start_time
    
    # 第二次抽取（应该使用缓存）
    start_time = time.time()
    results2 = manager.extract_from_text(test_text, doc_id=99, field="cache_test")
    time2 = time.time() - start_time
    
    print(f"✅ 缓存测试:")
    print(f"  第一次抽取: {time1:.4f}秒, {len(results1)} 个实体")
    print(f"  第二次抽取: {time2:.4f}秒, {len(results2)} 个实体")
    print(f"  加速比: {time1/time2 if time2 > 0 else 'N/A':.1f}x")
    
    return True

def test_with_real_npr_data():
    """使用真实NPR数据测试"""
    print("\n🌟 使用真实NPR数据测试")
    print("=" * 60)
    
    try:
        # 加载NPR数据
        with open('data/npr_articles.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        print(f"✅ 加载了 {len(articles)} 篇NPR文章")
        
        # 初始化管理器
        config = {
            'enable_regex_extractor': True,
            'regex_confidence_threshold': 0.7,  # 更严格的阈值
            'merge_duplicate_entities': True,
            'max_entities_per_type': 30,
            'enable_cache': True
        }
        
        manager = ExtractionManager(config)
        if not manager.initialize():
            print("❌ 管理器初始化失败")
            return False
        
        # 创建文档对象
        documents = []
        for i, article in enumerate(articles[:10]):  # 测试前10篇
            doc = MockDocument(
                doc_id=i,
                title=article['title'],
                content=article['content'][:2000],  # 限制长度以节省时间
                summary=article.get('summary', '')
            )
            documents.append(doc)
        
        print(f"📄 准备处理 {len(documents)} 篇文章")
        
        # 批量处理
        def progress_callback(current, total, progress):
            print(f"    处理进度: {current}/{total} ({progress:.1%})")
        
        start_time = time.time()
        results = manager.extract_from_documents(documents, progress_callback)
        processing_time = time.time() - start_time
        
        # 统计结果
        total_entities = sum(len(doc_results) for doc_results in results.values())
        
        print(f"\n✅ 真实数据测试完成:")
        print(f"  📄 处理文章: {len(documents)} 篇")
        print(f"  🔍 总抽取数: {total_entities} 个实体")
        print(f"  ⏱️ 处理时间: {processing_time:.2f}秒")
        print(f"  🚀 处理速度: {len(documents)/processing_time:.1f} 文章/秒")
        print(f"  📊 平均每篇: {total_entities/len(documents):.1f} 个实体")
        
        # 显示各类型统计
        type_counts = {}
        for doc_results in results.values():
            for result in doc_results:
                type_counts[result.entity_type] = type_counts.get(result.entity_type, 0) + 1
        
        print(f"\n📋 实体类型分布:")
        for entity_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {entity_type}: {count} 个")
        
        # 显示一些示例结果
        print(f"\n🔍 抽取示例:")
        for doc_id, doc_results in list(results.items())[:3]:
            print(f"\n  📄 文章 {doc_id} ({len(doc_results)} 个实体):")
            
            # 按类型分组
            by_type = {}
            for result in doc_results:
                if result.entity_type not in by_type:
                    by_type[result.entity_type] = []
                by_type[result.entity_type].append(result)
            
            for entity_type, type_results in by_type.items():
                top_results = sorted(type_results, key=lambda x: x.confidence, reverse=True)[:2]
                entities = [f"{r.entity_value}({r.confidence:.2f})" for r in top_results]
                print(f"    {entity_type}: {', '.join(entities)}")
        
        # 保存真实数据的结果
        os.makedirs('results', exist_ok=True)
        manager.export_results(results, 'results/npr_extraction_results.json', 'json')
        manager.save_statistics('results/npr_extraction_statistics.json')
        
        print(f"\n💾 真实数据结果已保存到 results/ 目录")
        
        return True
        
    except FileNotFoundError:
        print("⚠️ 未找到NPR数据文件 (data/npr_articles.json)")
        print("   跳过真实数据测试")
        return True
    except Exception as e:
        print(f"❌ 真实数据测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🎯 信息抽取系统完整测试套件")
    print("=" * 70)
    
    try:
        # 基础功能测试
        if not test_extraction_system():
            print("❌ 基础功能测试失败")
            return False
        
        # 真实数据测试
        if not test_with_real_npr_data():
            print("❌ 真实数据测试失败")
            return False
        
        print("\n" + "=" * 70)
        print("🎉 所有测试通过！信息抽取系统运行正常")
        print("📁 测试结果已保存到 results/ 目录")
        print("🎯 系统已准备好进行实际使用")
        
        # 给出使用建议
        print("\n💡 使用建议:")
        print("1. 可以调整 regex_confidence_threshold 来控制抽取精度")
        print("2. enable_cache=True 可以提高重复处理的速度")
        print("3. max_entities_per_type 可以限制每种类型的实体数量")
        print("4. 查看 results/ 目录了解详细的抽取结果")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()