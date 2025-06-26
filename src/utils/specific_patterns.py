"""
最终修复的正则表达式模式
完全替换 src/utils/npr_specific_patterns.py
"""

import re
from typing import Dict, List, Pattern

class NPRSpecificPatterns:
    """针对NPR新闻数据优化的正则表达式模式 - 最终修复版"""
    
    # 简化且稳定的人名模式
    PERSON_NAME_PATTERNS = [
        # 1. 带职位/称谓的人名
        r'\b(?:President|Vice President|Senator|Representative|Rep\.|Governor|Mayor|Chief|Director|Secretary|Attorney General|Justice)\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*[A-Z][a-z]+)?)\b',
        
        # 2. 学术/专业称谓
        r'\b(?:Dr|Prof|Professor)\.?\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b',
        
        # 3. NPR记者归属
        r'\bNPR\'s\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b',
        
        # 4. 引用上下文中的人名 - 简化版
        r'\b([A-Z][a-z]+)\s+(?:said|told|testified|announced|declared|stated)\b',
        
        # 5. according to 格式
        r'(?:according to|as)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b',
        
        # 6. 标准人名格式 - 移除负向前瞻以避免错误
        r'\b([A-Z][a-z]{2,}\s+[A-Z][a-z]{2,})\b',
        
        # 7. 带中间名的人名
        r'\b([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+)\b',
    ]
    
    # 地名模式
    LOCATION_PATTERNS = [
        # 1. 政治中心
        r'\b(Washington(?:,\s*D\.?C\.?)?|White House|Capitol Hill|Pentagon)\b',
        
        # 2. 国际热点地区
        r'\b(Ukraine|Russia|China|Iran|Israel|Gaza|Palestine|Afghanistan|Iraq|Syria|North Korea|South Korea|Taiwan|Hong Kong)\b',
        
        # 3. 美国州名
        r'\b(California|Texas|Florida|New York|Pennsylvania|Illinois|Ohio|Georgia|Michigan|North Carolina|Virginia|Washington|Arizona|Massachusetts|Tennessee|Colorado|Minnesota|Alabama|Louisiana|Oregon|Connecticut|Maryland|Wisconsin|Missouri|Indiana|Kentucky|Oklahoma|Nevada|Utah|Iowa|Arkansas|Mississippi|Kansas|New Mexico|Nebraska|West Virginia|Idaho|Hawaii|New Hampshire|Maine|Rhode Island|Montana|Delaware|South Dakota|North Dakota|Alaska|Vermont|Wyoming)\b',
        
        # 4. 城市,州格式
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+)\b',
        
        # 5. 主要城市
        r'\b(New York|Los Angeles|Chicago|Houston|Philadelphia|Phoenix|San Diego|Dallas|San Antonio|San Jose|Austin|Jacksonville|San Francisco|Indianapolis|Seattle|Denver|Boston|Nashville|Detroit|Portland|Las Vegas|Memphis|Baltimore|Milwaukee|Atlanta|Miami|Cleveland|New Orleans|Tampa|Pittsburgh|Cincinnati|Minneapolis|Kansas City|St\. Louis|Orlando|Buffalo|Newark|Richmond|Birmingham|Salt Lake City|Providence)\b',
        
        # 6. 国家名称
        r'\b(United States|America|Canada|Mexico|Brazil|United Kingdom|Britain|England|France|Germany|Italy|Spain|Netherlands|Belgium|Switzerland|Austria|Sweden|Norway|Denmark|Finland|Poland|Romania|Greece|Turkey|Egypt|India|Pakistan|Thailand|Vietnam|Indonesia|Malaysia|Philippines|Singapore|Japan|Australia|New Zealand)\b',
        
        # 7. 地区名称
        r'\b(Europe|Middle East|Africa|Asia|Latin America|European Union|EU)\b',
    ]
    
    # 组织机构模式
    ORGANIZATION_PATTERNS = [
        # 1. 美国政府核心机构
        r'\b(White House|Congress|Senate|House of Representatives|Supreme Court)\b',
        
        # 2. 政府部门
        r'\b(Department of (?:State|Defense|Justice|Treasury|Interior|Agriculture|Commerce|Labor|Health and Human Services|Housing and Urban Development|Transportation|Energy|Education|Veterans Affairs|Homeland Security))\b',
        
        # 3. 联邦机构
        r'\b(Federal Bureau of Investigation|FBI|Central Intelligence Agency|CIA|National Security Agency|NSA|Centers for Disease Control|CDC|Food and Drug Administration|FDA|Environmental Protection Agency|EPA|Federal Communications Commission|FCC|Securities and Exchange Commission|SEC|Federal Reserve|Internal Revenue Service|IRS)\b',
        
        # 4. 媒体机构
        r'\b(NPR|National Public Radio|PBS|Public Broadcasting Service|Corporation for Public Broadcasting|CPB|CNN|BBC|NBC|ABC|CBS|Fox News|MSNBC|Reuters|Associated Press|AP|New York Times|Washington Post|Wall Street Journal|USA Today|Bloomberg|CNBC)\b',
        
        # 5. 著名大学
        r'\b(Harvard University|Yale University|Princeton University|Stanford University|MIT|University of California|University of Michigan|University of Texas)\b',
        
        # 6. 国际组织
        r'\b(United Nations|UN|NATO|European Union|EU|World Health Organization|WHO|International Monetary Fund|IMF|World Bank)\b',
    ]
    
    # 时间模式
    TIME_PATTERNS = [
        # 1. 相对时间
        r'\b(today|yesterday|tomorrow|this week|last week|next week|this month|last month|next month|this year|last year|next year|recently|earlier|later)\b',
        
        # 2. 完整日期
        r'\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b',
        
        # 3. 数字日期格式
        r'\b(\d{1,2}/\d{1,2}/\d{4})\b',
        r'\b(\d{4}-\d{1,2}-\d{1,2})\b',
        
        # 4. 时间段
        r'\b(\d+\s+(?:days?|weeks?|months?|years?)\s+ago)\b',
        
        # 5. 时间点
        r'\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm|EST|PST|CST|MST|EDT|PDT|CDT|MDT)?)\b',
        
        # 6. 政治时间
        r'\b(during the (?:campaign|election|presidency|administration)|election day|inauguration)\b',
        
        # 7. 月份年份
        r'\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b',
        
        # 8. 季节
        r'\b((?:spring|summer|fall|autumn|winter)\s+\d{4})\b',
        
        # 9. 年份
        r'\b(\d{4})\b',
    ]
    
    # 金额模式
    MONEY_PATTERNS = [
        # 1. 大额资金
        r'(\$\d+(?:\.\d+)?\s*(?:billion|trillion|million))\b',
        
        # 2. 数字+货币单位
        r'\b(\d+(?:\.\d+)?\s*(?:billion|trillion|million)\s*dollars?)\b',
        
        # 3. 普通金额
        r'(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b',
        
        # 4. 百分比
        r'\b(\d+(?:\.\d+)?%)\b',
        
        # 5. 预算相关
        r'\b(?:budget|funding|spending|cost|price|worth|value)\s+(?:of\s+)?(\$?\d+(?:\.\d+)?\s*(?:billion|trillion|million|thousand)?\s*(?:dollars?)?)\b',
        
        # 6. 其他货币
        r'\b(\d+(?:,\d{3})*\s+(?:dollars?|euros?|pounds?|yen))\b',
    ]
    
    # 联系方式模式
    CONTACT_PATTERNS = [
        # 1. 美国电话号码格式
        r'\b(\d{3}-\d{3}-\d{4})\b',
        r'\b(\(\d{3}\)\s*\d{3}-\d{4})\b',
        r'\b(1-\d{3}-\d{3}-\d{4})\b',
        
        # 2. 邮箱地址
        r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
        
        # 3. 网址
        r'\b(https?://[^\s]+)\b',
        r'\b(www\.[^\s]+)\b',
        
        # 4. 域名
        r'\b([a-zA-Z0-9.-]+\.(?:gov|edu|org|com|net))\b',
        
        # 5. 电话号码其他格式
        r'\b(\d{3}\.\d{3}\.\d{4})\b',
        r'\b(\d{3}\s+\d{3}\s+\d{4})\b',
        
        # 6. 免费电话
        r'\b(1-800-\d{3}-\d{4})\b',
    ]
    
    # 引用模式
    QUOTE_PATTERNS = [
        # 1. 双引号引用
        r'"([^"]{15,300})"',
        
        # 2. 单引号引用
        r"'([^']{15,300})'",
        
        # 3. 声明格式
        r'\b(?:said|stated|declared|announced|testified):\s*"([^"]{15,200})"',
        
        # 4. 简单间接引用
        r'\b(?:according to)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s*,?\s*"([^"]{15,150})"',
    ]

    @classmethod
    def get_compiled_patterns(cls) -> Dict[str, List[Pattern]]:
        """获取编译后的正则表达式模式"""
        patterns = {}
        
        try:
            patterns['person'] = []
            for i, p in enumerate(cls.PERSON_NAME_PATTERNS):
                try:
                    compiled_pattern = re.compile(p, re.IGNORECASE)
                    patterns['person'].append(compiled_pattern)
                except re.error as e:
                    print(f"人名模式 {i} 编译失败: {e}")
                    continue
            
            patterns['location'] = []
            for i, p in enumerate(cls.LOCATION_PATTERNS):
                try:
                    compiled_pattern = re.compile(p, re.IGNORECASE)
                    patterns['location'].append(compiled_pattern)
                except re.error as e:
                    print(f"地名模式 {i} 编译失败: {e}")
                    continue
            
            patterns['organization'] = []
            for i, p in enumerate(cls.ORGANIZATION_PATTERNS):
                try:
                    compiled_pattern = re.compile(p, re.IGNORECASE)
                    patterns['organization'].append(compiled_pattern)
                except re.error as e:
                    print(f"组织模式 {i} 编译失败: {e}")
                    continue
            
            patterns['time'] = []
            for i, p in enumerate(cls.TIME_PATTERNS):
                try:
                    compiled_pattern = re.compile(p, re.IGNORECASE)
                    patterns['time'].append(compiled_pattern)
                except re.error as e:
                    print(f"时间模式 {i} 编译失败: {e}")
                    continue
            
            patterns['money'] = []
            for i, p in enumerate(cls.MONEY_PATTERNS):
                try:
                    compiled_pattern = re.compile(p, re.IGNORECASE)
                    patterns['money'].append(compiled_pattern)
                except re.error as e:
                    print(f"金额模式 {i} 编译失败: {e}")
                    continue
            
            patterns['contact'] = []
            for i, p in enumerate(cls.CONTACT_PATTERNS):
                try:
                    compiled_pattern = re.compile(p, re.IGNORECASE)
                    patterns['contact'].append(compiled_pattern)
                except re.error as e:
                    print(f"联系方式模式 {i} 编译失败: {e}")
                    continue
            
            patterns['quote'] = []
            for i, p in enumerate(cls.QUOTE_PATTERNS):
                try:
                    compiled_pattern = re.compile(p, re.IGNORECASE | re.DOTALL)
                    patterns['quote'].append(compiled_pattern)
                except re.error as e:
                    print(f"引用模式 {i} 编译失败: {e}")
                    continue
                    
        except Exception as e:
            print(f"模式编译总体错误: {e}")
            return {}
        
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


# 测试正则表达式语法
if __name__ == "__main__":
    print("=== 测试正则表达式语法 ===")
    
    try:
        patterns = NPRSpecificPatterns.get_compiled_patterns()
        if patterns:
            print("✅ 所有正则表达式编译成功！")
            
            total_patterns = sum(len(pattern_list) for pattern_list in patterns.values())
            print(f"总计: {total_patterns} 个有效模式")
            
            for entity_type, pattern_list in patterns.items():
                print(f"  {entity_type}: {len(pattern_list)} 个模式")
                
            # 简单测试
            test_text = "President Biden announced aid to Ukraine yesterday."
            print(f"\n测试文本: {test_text}")
            
            for entity_type, pattern_list in patterns.items():
                matches = []
                for pattern in pattern_list:
                    for match in pattern.finditer(test_text):
                        if match.groups():
                            # 获取第一个非空分组
                            for group in match.groups():
                                if group:
                                    matches.append(group.strip())
                                    break
                        else:
                            matches.append(match.group().strip())
                
                if matches:
                    unique_matches = list(set(matches))  # 去重
                    print(f"  {entity_type}: {unique_matches}")
        else:
            print("❌ 正则表达式编译失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()