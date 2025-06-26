#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进后的抽取器效果
"""

import sys
import os
sys.path.append('src')

from src.extraction.regex_extractor import RegexExtractor

def test_problematic_cases():
    """测试之前有问题的案例"""
    print("🔍 测试改进效果")
    print("=" * 50)
    
    # 初始化抽取器
    extractor = RegexExtractor(confidence_threshold=0.7)
    if not extractor.initialize():
        print("❌ 初始化失败")
        return
    
    # 测试之前有问题的文本
    test_cases = [
        'President Biden announced $1 billion aid to Ukraine yesterday.',
        '"This support is crucial for democracy," Biden said.',
        'Ukrainian President Volodymyr Zelenskyy met with officials.',
        'NPR\'s David Folkenflik reported from Washington.',
        'According to Secretary Austin, the funding will help.',
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n📝 测试案例 {i}: {text}")
        results = extractor.extract_from_text(text, doc_id=i, field="test")
        
        if results:
            for result in results:
                print(f"  ✓ {result.entity_type}: '{result.entity_value}' (置信度: {result.confidence:.3f})")
        else:
            print("  (无抽取结果)")
    

if __name__ == "__main__":
    test_problematic_cases()