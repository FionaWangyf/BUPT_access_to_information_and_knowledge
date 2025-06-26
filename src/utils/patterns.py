"""
正则表达式模式库 - 优化版本
修复误识别问题，提高抽取准确性
"""

# 导入优化的NPR专用模式
from .specific_patterns import NPRSpecificPatterns

# 为了向后兼容，保持原来的接口
class RegexPatterns(NPRSpecificPatterns):
    """正则表达式模式集合（优化版）"""
    pass


# 测试代码
if __name__ == "__main__":
    print("=== 优化正则表达式模式测试 ===")
    
    # 使用问题案例进行测试
    test_cases = [
        # 问题案例1: "This support" 不应该被识别为人名
        'President Biden announced today. "This support is crucial," Biden said.',
        
        # 问题案例2: "to Ukraine" 不应该被识别为人名
        'The United States will provide aid to Ukraine.',
        
        # 问题案例3: "Ukrainian President" 应该只识别具体人名
        'meeting with Ukrainian President Volodymyr Zelenskyy',
        
        # 正确案例：应该被正确识别的
        'NPR\'s David Folkenflik reported from Washington. Dr. Sarah Johnson testified.',
    ]
    
    patterns = RegexPatterns.get_compiled_patterns()
    descriptions = RegexPatterns.get_pattern_descriptions()
    
    print("测试优化后的模式匹配:")
    print("=" * 70)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n📝 测试案例 {i}: {test_text}")
        print("-" * 50)
        
        for entity_type, pattern_list in patterns.items():
            matches = set()
            
            for pattern in pattern_list:
                for match in pattern.finditer(test_text):
                    if match.groups():
                        matched_text = match.group(1).strip()
                    else:
                        matched_text = match.group().strip()
                    
                    if matched_text and len(matched_text) > 1:
                        matches.add(matched_text)
            
            if matches:
                print(f"  🏷️ {entity_type}: {', '.join(sorted(matches))}")
    
    print("\n✅ 优化模式测试完成")