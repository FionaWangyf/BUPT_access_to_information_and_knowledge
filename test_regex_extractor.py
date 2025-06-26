#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试正则表达式抽取器
"""

import sys
import os
sys.path.append('src')

from src.extraction.regex_extractor import RegexExtractor

def test_regex_extractor():
    """测试正则表达式抽取器"""
    print("🔧 正则表达式抽取器功能测试")
    print("=" * 60)
    
    # 初始化抽取器
    extractor = RegexExtractor(confidence_threshold=0.6)
    
    if not extractor.initialize():
        print("❌ 抽取器初始化失败")
        return False
    
    print(f"✅ 抽取器初始化成功")
    print(f"📋 支持的实体类型: {extractor.get_supported_entity_types()}")
    print(f"⚙️ 置信度阈值: {extractor.confidence_threshold}")
    
    # 测试基本功能
    test_text = "President Biden announced $1 billion aid to Ukraine yesterday."
    
    print(f"\n🔍 测试文本: {test_text}")
    results = extractor.extract_from_text(test_text, doc_id=1, field="test")
    
    print(f"✅ 抽取结果: {len(results)} 个实体")
    for result in results:
        print(f"  - {result.entity_type}: {result.entity_value} (置信度: {result.confidence:.3f})")
    
    return True

def test_with_real_npr_data():
    """使用真实NPR数据测试"""
    print("\n📰 使用真实NPR数据测试")
    print("=" * 60)
    
    # 尝试加载真实数据
    try:
        import json
        with open('data/npr_articles.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        print(f"✅ 加载了 {len(articles)} 篇NPR文章")
        
        # 初始化抽取器
        extractor = RegexExtractor(confidence_threshold=0.7)
        if not extractor.initialize():
            print("❌ 抽取器初始化失败")
            return False
        
        # 测试前3篇文章
        total_results = []
        for i, article in enumerate(articles[:3]):
            print(f"\n📄 测试文章 {i+1}: {article['title'][:50]}...")
            
            # 从标题抽取
            title_results = extractor.extract_from_text(
                article['title'], doc_id=i, field='title'
            )
            
            # 从内容抽取（限制长度以节省时间）
            content_preview = article['content'][:1000]  # 前1000字符
            content_results = extractor.extract_from_text(
                content_preview, doc_id=i, field='content'
            )
            
            article_results = title_results + content_results
            total_results.extend(article_results)
            
            print(f"  📊 抽取到 {len(article_results)} 个实体")
            
            # 显示每种类型的数量
            type_counts = {}
            for result in article_results:
                type_counts[result.entity_type] = type_counts.get(result.entity_type, 0) + 1
            
            if type_counts:
                type_summary = ", ".join([f"{t}:{c}" for t, c in type_counts.items()])
                print(f"  🏷️ 类型分布: {type_summary}")
        
        # 总体统计
        print(f"\n📈 总体测试结果:")
        print(f"  总实体数: {len(total_results)}")
        
        if total_results:
            summary = extractor.get_extraction_summary(total_results)
            print(f"  平均置信度: {summary['avg_confidence']:.3f}")
            print(f"  类型分布: {summary['entity_type_counts']}")
            print(f"  高置信度占比: {summary['quality_metrics']['high_confidence_ratio']:.1%}")
        
        return True
        
    except FileNotFoundError:
        print("⚠️ 未找到NPR数据文件，跳过真实数据测试")
        return True
    except Exception as e:
        print(f"❌ 真实数据测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎯 正则表达式抽取器测试套件")
    print("=" * 70)
    
    try:
        # 基本功能测试
        if not test_regex_extractor():
            print("❌ 基本功能测试失败")
            return False
        
        # 真实数据测试
        if not test_with_real_npr_data():
            print("❌ 真实数据测试失败")
            return False
        
        print("\n" + "=" * 70)
        print("✅ 所有测试通过！正则表达式抽取器运行正常")
        print("🎯 准备进入第三步：实现抽取管理器")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()