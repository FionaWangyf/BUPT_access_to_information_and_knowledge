#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试信息抽取基础架构
"""

import sys
import os
sys.path.append('src')

from src.extraction.extractor_base import ExtractionResult, BaseExtractor
from src.utils.patterns import RegexPatterns

def test_extraction_result():
    """测试ExtractionResult类"""
    print("=== 测试ExtractionResult ===")
    
    # 创建测试结果
    result = ExtractionResult(
        entity_type="person",
        entity_value="John Smith",
        confidence=0.85,
        start_position=10,
        end_position=20,
        context="President John Smith announced",
        doc_id=1,
        field="title",
        metadata={"pattern_type": "with_title"}
    )
    
    print(f"✓ 创建结果: {result}")
    
    # 测试转换
    result_dict = result.to_dict()
    print(f"✓ 转为字典: {len(result_dict)} 个字段")
    
    # 测试恢复
    restored = ExtractionResult.from_dict(result_dict)
    print(f"✓ 从字典恢复: {restored.entity_value == result.entity_value}")
    
    return True

def test_regex_patterns():
    """测试正则表达式模式"""
    print("\n=== 测试正则表达式模式 ===")
    
    # 获取模式
    patterns = RegexPatterns.get_compiled_patterns()
    descriptions = RegexPatterns.get_pattern_descriptions()
    
    print(f"✓ 加载了 {len(patterns)} 种实体类型")
    
    for entity_type, pattern_list in patterns.items():
        print(f"  {entity_type}: {len(pattern_list)} 个模式")
    
    # 简单匹配测试
    test_text = "President Biden announced $1 billion aid."
    total_matches = 0
    
    for entity_type, pattern_list in patterns.items():
        matches = 0
        for pattern in pattern_list:
            matches += len(pattern.findall(test_text))
        if matches > 0:
            print(f"✓ {entity_type}: {matches} 个匹配")
            total_matches += matches
    
    print(f"✓ 总计找到 {total_matches} 个匹配")
    return True

def main():
    """主测试函数"""
    print("🔍 信息抽取基础架构测试")
    print("=" * 50)
    
    try:
        # 测试基础类
        if not test_extraction_result():
            print("❌ ExtractionResult测试失败")
            return False
        
        # 测试正则模式
        if not test_regex_patterns():
            print("❌ RegexPatterns测试失败")
            return False
        
        print("\n✅ 所有基础架构测试通过！")
        print("\n📋 下一步：开始实现正则表达式抽取器")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()