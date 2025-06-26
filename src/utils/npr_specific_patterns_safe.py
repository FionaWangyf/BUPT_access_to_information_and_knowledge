"""
安全的正则表达式模式 - 彻底修复版
替换 src/utils/npr_specific_patterns.py 的完整内容
"""

import re
from typing import Dict, List, Pattern

class NPRSpecificPatterns:
    """安全的正则表达式模式 - 简化版"""
    
    # 简化的人名模式 - 避免复杂的分组
    PERSON_NAME_PATTERNS = [
        # 1. 带称谓的人名
        r'\b(?:President|Senator|Representative|Governor|Dr|Prof)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b',
        
        # 2. NPR记者归属
        r'\bNPR's\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b',
        
        # 3. 发言上下文
        r'\b([A-Z][a-z]+)\s+(?:said|told|announced)\b',
        
        # 4. according to 格式
        r'\baccording to\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b',
        
        # 5. 标准人名格式
        r'\b([A-Z][a-z]{2,}\s+[A-Z][a-z]{2,})\b',
        
        # 6. 带中间名
        r'\b([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+)\b',
    ]
    
    # 地名模式
    LOCATION_PATTERNS = [
        r'\b(Washington|White House|Capitol Hill|Pentagon)\b',
        r'\b(Ukraine|Russia|China|Iran|Israel|Gaza|Palestine|Afghanistan|Iraq|Syria)\b',
        r'\b(California|Texas|Florida|New York|Pennsylvania|Illinois|Ohio|Georgia)\b',
        r'\b([A-Z][a-z]+),\s*([A-Z][a-z]+)\b',
        r'\b(Los Angeles|Chicago|Houston|Philadelphia|Phoenix|San Diego|Dallas)\b',
        r'\b(United States|America|Canada|Mexico|Brazil|United Kingdom|Britain|France|Germany|Italy|Spain|Japan|Australia)\b',
        r'\b(Europe|Middle East|Africa|Asia|Latin America)\b',
    ]
    
    # 组织机构模式
    ORGANIZATION_PATTERNS = [
        r'\b(White House|Congress|Senate|House of Representatives|Supreme Court)\b',
        r'\b(Department of (?:State|Defense|Justice|Treasury|Education|Veterans Affairs))\b',
        r'\b(FBI|CIA|NSA|CDC|FDA|EPA|FCC|SEC|Federal Reserve|IRS)\b',
        r'\b(NPR|PBS|CNN|BBC|NBC|ABC|CBS|Fox News|Reuters|Associated Press)\b',
        r'\b(Harvard University|Yale University|Stanford University|MIT)\b',
        r'\b(United Nations|UN|NATO|European Union|EU|WHO|IMF|World Bank)\b',
    ]
    
    # 时间模式
    TIME_PATTERNS = [
        r'\b(today|yesterday|tomorrow|this week|last week|next week)\b',
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b',
        r'\b(\d{1,2}/\d{1,2}/\d{4})\b',
        r'\b(\d{4}-\d{1,2}-\d{1,2})\b',
        r'\b(\d+\s+(?:days?|weeks?|months?|years?)\s+ago)\b',
        r'\b(\d{1,2}:\d{2}\s*(?:AM|PM|EST|PST|CST|MST)?)\b',
        r'\b(during the (?:campaign|election|presidency))\b',
        r'\b(election day|inauguration)\b',
    ]
    
    # 金额模式
    MONEY_PATTERNS = [
        r'(\$\d+(?:\.\d+)?\s*(?:billion|trillion|million))\b',
        r'\b(\d+(?:\.\d+)?\s*(?:billion|trillion|million)\s*dollars?)\b',
        r'(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b',
        r'\b(\d+(?:\.\d+)?%)\b',
        r'\b(?:budget|funding|spending)\s+(?:of\s+)?(\$?\d+(?:\.\d+)?\s*(?:billion|trillion|million)?)\b',
    ]
    
    # 联系方式模式
    CONTACT_PATTERNS = [
        r'\b(\d{3}-\d{3}-\d{4})\b',
        r'\b(\(\d{3}\)\s*\d{3}-\d{4})\b',
        r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
        r'\b(https?://[^\s]+)\b',
        r'\b(www\.[^\s]+)\b',
    ]
    
    # 引用模式
    QUOTE_PATTERNS = [
        r'"([^"]{15,300})"',
        r"'([^']{15,300})'",
        r'\b(?:said|stated|declared):\s*"([^"]{15,200})"',
    ]

    @classmethod
    def get_compiled_patterns(cls) -> Dict[str, List[Pattern]]:
        """获取编译后的正则表达式模式"""
        patterns = {}
        
        pattern_lists = [
            ('person', cls.PERSON_NAME_PATTERNS),
            ('location', cls.LOCATION_PATTERNS),
            ('organization', cls.ORGANIZATION_PATTERNS),
            ('time', cls.TIME_PATTERNS),
            ('money', cls.MONEY_PATTERNS),
            ('contact', cls.CONTACT_PATTERNS),
            ('quote', cls.QUOTE_PATTERNS),
        ]
        
        for name, pattern_list in pattern_lists:
            patterns[name] = []
            for i, pattern in enumerate(pattern_list):
                try:
                    if name == 'quote':
                        compiled_pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
                    else:
                        compiled_pattern = re.compile(pattern, re.IGNORECASE)
                    patterns[name].append(compiled_pattern)
                except re.error as e:
                    print(f"模式编译失败 {name}[{i}]: {e}")
                    continue
        
        return patterns
    
    @classmethod
    def get_pattern_descriptions(cls) -> Dict[str, str]:
        """获取模式描述"""
        return {
            'person': '人名（政治人物、记者、专家、官员等）',
            'location': '地名（美国地名、国际热点地区、政治中心等）',
            'organization': '组织机构（政府部门、媒体、大学、公司、国际组织等）',
            'time': '时间信息（新闻时间、政治事件时间、相对时间等）',
            'money': '金额信息（政府预算、贸易数据、罚款赔偿、百分比等）',
            'contact': '联系方式（官方联系方式、新闻相关联系信息）',
            'quote': '引用内容（政治发言、新闻声明、专家观点等）'
        }


# 测试所有模式
if __name__ == "__main__":
    print("=== 测试安全正则表达式模式 ===")
    
    try:
        patterns = NPRSpecificPatterns.get_compiled_patterns()
        
        total_patterns = sum(len(pattern_list) for pattern_list in patterns.values())
        print(f"✅ 成功编译 {total_patterns} 个模式")
        
        for entity_type, pattern_list in patterns.items():
            print(f"  {entity_type}: {len(pattern_list)} 个模式")
        
        # 简单测试
        test_text = "President Biden announced $1 billion aid to Ukraine yesterday."
        print(f"\n测试文本: {test_text}")
        
        for entity_type, pattern_list in patterns.items():
            matches = []
            for pattern in pattern_list:
                for match in pattern.finditer(test_text):
                    if match.groups():
                        for group in match.groups():
                            if group:
                                matches.append(group.strip())
                                break
                    else:
                        matches.append(match.group().strip())
            
            if matches:
                unique_matches = list(set(matches))
                print(f"  {entity_type}: {unique_matches}")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
