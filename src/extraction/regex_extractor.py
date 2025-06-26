"""
基于正则表达式的信息抽取器
实现人名、地名、组织、时间、金额等信息的抽取
针对NPR新闻数据优化
"""

import re
import time
from typing import List, Dict, Any, Pattern, Set, Tuple
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.extraction.extractor_base import BaseExtractor, ExtractionResult
from src.utils.patterns import RegexPatterns

class RegexExtractor(BaseExtractor):
    """基于正则表达式的信息抽取器"""
    
    def __init__(self, confidence_threshold: float = 0.6):
        super().__init__("RegexExtractor")
        self.confidence_threshold = confidence_threshold
        self.patterns = {}
        self.pattern_descriptions = {}
        
        # 置信度权重配置（针对NPR数据优化）
        self.confidence_weights = {
            'person': {
                'with_title': 0.95,     # President Biden, Dr. Smith
                'quoted_speech': 0.9,   # Biden said, according to Smith
                'npr_attribution': 0.9, # NPR's John Doe
                'standard_format': 0.8, # John Smith
                'middle_initial': 0.85, # John D. Smith
                'default': 0.7
            },
            'location': {
                'political_center': 0.95, # White House, Capitol Hill
                'country': 0.9,          # United States, China
                'state': 0.85,           # California, Texas
                'city_state': 0.9,       # Los Angeles, California
                'major_city': 0.8,       # New York, Chicago
                'international': 0.85,   # Ukraine, Gaza
                'default': 0.7
            },
            'organization': {
                'government': 0.95,      # Department of Defense, FBI
                'media': 0.9,           # NPR, CNN, New York Times
                'university': 0.85,      # Harvard University
                'corporation': 0.8,      # Microsoft Corp
                'international': 0.9,    # United Nations, NATO
                'default': 0.75
            },
            'time': {
                'full_date': 0.95,      # March 15, 2024
                'relative_time': 0.85,  # yesterday, last week
                'time_point': 0.8,      # 2:30 PM EST
                'political_time': 0.9,  # during the campaign
                'default': 0.7
            },
            'money': {
                'large_amount': 0.95,   # $2.5 billion
                'government_budget': 0.9, # budget of $100 million
                'currency_symbol': 0.85, # $1,000
                'percentage': 0.8,      # 8-10%
                'default': 0.75
            },
            'contact': {
                'official_email': 0.95, # @whitehouse.gov, @npr.org
                'government_phone': 0.9, # official numbers
                'url': 0.85,           # official websites
                'regular_email': 0.8,   # regular email addresses
                'default': 0.75
            },
            'quote': {
                'direct_quote': 0.9,    # "exact quote"
                'political_statement': 0.95, # official statements
                'expert_opinion': 0.85, # academic/expert quotes
                'indirect_quote': 0.75, # according to sources
                'default': 0.8
            }
        }
        
        # 无效匹配过滤器
        self.invalid_patterns = {
            'person': [
                r'^\d+$',  # 纯数字
                r'^[A-Z]$',  # 单个大写字母
                r'^(?:the|and|or|in|on|at|to|for|of|with|by|from|said|according|told)$',  # 常见词
                r'^(?:President|Senator|Representative|Governor|Dr|Mr|Mrs|Ms)$',  # 只有称谓
                r'^(?:NPR|CNN|BBC)$',  # 媒体名称（应该是组织）
            ],
            'location': [
                r'^\d+$',
                r'^[A-Z]$',
                r'^(?:the|and|or|in|on|at)$',
            ],
            'organization': [
                r'^\d+$',
                r'^[A-Z]$',
                r'^(?:the|and|or)$',
            ],
            'time': [
                r'^[A-Z]$',
                r'^(?:the|and|or)$',
            ],
            'money': [
                r'^[\$,\.]$',
                r'^(?:the|and|or)$',
            ],
            'contact': [
                r'^[@\.]$',
                r'^(?:www|http|https)$',
            ],
            'quote': [
                r'^["\']$',
                r'^[\.\,\!\?]$',
                r'^(?:said|the|and|or)$',
            ]
        }
        
    
    def initialize(self) -> bool:
        """初始化抽取器"""
        try:
            print("🔧 初始化正则表达式抽取器...")
            
            # 获取编译后的模式
            self.patterns = RegexPatterns.get_compiled_patterns()
            self.pattern_descriptions = RegexPatterns.get_pattern_descriptions()
            
            print(f"✅ 加载了 {len(self.patterns)} 种实体类型的抽取模式")
            for entity_type, description in self.pattern_descriptions.items():
                pattern_count = len(self.patterns[entity_type])
                print(f"  📋 {entity_type}: {description} ({pattern_count} 个模式)")
            
            print(f"⚙️ 置信度阈值: {self.confidence_threshold}")
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"❌ 初始化正则抽取器失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def extract_from_text(self, text: str, doc_id: int, field: str) -> List[ExtractionResult]:
        """从文本中抽取信息"""
        if not self.is_initialized:
            print("❌ 错误：抽取器未初始化")
            return []
        
        if not text or not text.strip():
            return []
        
        start_time = time.time()
        results = []
        
        # 对每种实体类型进行抽取
        for entity_type, pattern_list in self.patterns.items():
            entity_results = self._extract_entity_type(
                text, entity_type, pattern_list, doc_id, field
            )
            results.extend(entity_results)
        
        # 后处理：去重、排序、过滤
        results = self._post_process_results(results, text)
        
        # 更新处理时间统计
        processing_time = time.time() - start_time
        self.statistics['processing_time'] += processing_time
        
        return results
    
    def _extract_entity_type(self, text: str, entity_type: str, 
                       pattern_list: List[Pattern], doc_id: int, 
                       field: str) -> List[ExtractionResult]:
        """抽取特定类型的实体"""
        results = []
        matched_spans = set()  # 避免重复匹配同一位置
        
        for pattern_idx, pattern in enumerate(pattern_list):
            try:
                for match in pattern.finditer(text):
                    # 处理分组匹配 - 修复版
                    if match.groups():
                        # 如果有分组，找到第一个非空分组
                        matched_text = None
                        start_pos = None
                        end_pos = None
                        
                        for i, group in enumerate(match.groups(), 1):
                            if group:  # 找到第一个非空分组
                                matched_text = group.strip()
                                start_pos = match.start(i)
                                end_pos = match.end(i)
                                break
                        
                        if not matched_text:  # 如果所有分组都为空，使用整个匹配
                            matched_text = match.group().strip()
                            start_pos = match.start()
                            end_pos = match.end()
                    else:
                        # 没有分组，使用整个匹配
                        matched_text = match.group().strip()
                        start_pos = match.start()
                        end_pos = match.end()
                    
                    # 检查基本有效性
                    if not matched_text or len(matched_text) < 2:
                        continue
                    
                    # 检查是否与已有匹配重叠
                    span = (start_pos, end_pos)
                    if self._has_overlap(span, matched_spans):
                        continue
                    
                    # 过滤无效匹配
                    if not self._is_valid_match(matched_text, entity_type):
                        continue
                    
                    # 计算置信度
                    confidence = self._calculate_confidence(
                        matched_text, entity_type, pattern_idx, text, start_pos
                    )
                    
                    # 只保留高置信度的结果
                    if confidence >= self.confidence_threshold:
                        # 获取上下文
                        context = self._extract_context(text, start_pos, end_pos)
                        
                        # 创建抽取结果
                        result = ExtractionResult(
                            entity_type=entity_type,
                            entity_value=matched_text,
                            confidence=confidence,
                            start_position=start_pos,
                            end_position=end_pos,
                            context=context,
                            doc_id=doc_id,
                            field=field,
                            metadata={
                                'pattern_index': pattern_idx,
                                'pattern_description': self._get_pattern_description(entity_type, pattern_idx),
                                'match_type': self._classify_match_type(matched_text, entity_type),
                                'has_groups': bool(match.groups())
                            }
                        )
                        
                        results.append(result)
                        matched_spans.add(span)
                        
            except Exception as e:
                print(f"⚠️ 模式匹配出错 {entity_type}[{pattern_idx}]: {e}")
                continue
        
        return results


    def _calculate_confidence(self, matched_text: str, entity_type: str, 
                            pattern_idx: int, full_text: str, position: int) -> float:
        """计算置信度分数"""
        # 获取匹配类型
        match_type = self._classify_match_type(matched_text, entity_type)
        
        # 根据匹配类型获取基础置信度
        if match_type in self.confidence_weights[entity_type]:
            base_confidence = self.confidence_weights[entity_type][match_type]
        else:
            base_confidence = self.confidence_weights[entity_type]['default']
        
        # 根据上下文调整置信度
        context_boost = self._get_context_boost(matched_text, entity_type, full_text, position)
        
        # 根据长度调整置信度
        length_boost = self._get_length_boost(matched_text, entity_type)
        
        # 最终置信度
        final_confidence = min(1.0, base_confidence + context_boost + length_boost)
        
        return final_confidence
    
    def _classify_match_type(self, matched_text: str, entity_type: str) -> str:
        """分类匹配类型以确定置信度权重 - 改进版"""
        if entity_type == 'person':
            # 检查是否有职位称谓
            if re.search(r'\b(?:President|Vice President|Senator|Representative|Governor|Dr|Prof|Secretary|Director|Chief|Justice)\b', matched_text, re.IGNORECASE):
                return 'with_title'
            
            # 检查NPR归属
            if 'NPR' in matched_text:
                return 'npr_attribution'
            
            # 检查中间名格式
            if re.search(r'\b[A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+\b', matched_text):
                return 'middle_initial'
            
            # 标准两个词的人名
            words = matched_text.strip().split()
            if len(words) == 2 and all(word[0].isupper() and word[1:].islower() for word in words):
                return 'standard_format'
                
        elif entity_type == 'location':
            # 政治中心
            political_centers = ['White House', 'Capitol Hill', 'Pentagon', 'Washington']
            if any(center.lower() in matched_text.lower() for center in political_centers):
                return 'political_center'
            
            # 国际热点
            international_hotspots = ['Ukraine', 'Russia', 'China', 'Iran', 'Israel', 'Gaza', 'Syria', 'Afghanistan', 'Iraq']
            if matched_text in international_hotspots:
                return 'international'
            
            # 城市,州格式
            if ',' in matched_text:
                return 'city_state'
            
            # 国家名
            countries = ['United States', 'America', 'Canada', 'Mexico', 'United Kingdom', 'Britain', 'France', 'Germany', 'Italy', 'Spain', 'Japan', 'Australia']
            if matched_text in countries:
                return 'country'
        
        elif entity_type == 'organization':
            # 政府机构
            if re.search(r'\b(?:Department|FBI|CIA|NASA|Congress|Senate|White House|Supreme Court)\b', matched_text, re.IGNORECASE):
                return 'government'
            
            # 媒体机构
            if re.search(r'\b(?:NPR|CNN|BBC|New York Times|Washington Post|CBS|NBC|ABC)\b', matched_text, re.IGNORECASE):
                return 'media'
            
            # 大学
            if re.search(r'\b(?:University|College)\b', matched_text, re.IGNORECASE):
                return 'university'
            
            # 国际组织
            if re.search(r'\b(?:United Nations|NATO|EU|WHO|IMF)\b', matched_text, re.IGNORECASE):
                return 'international'
        
        elif entity_type == 'money':
            # 大额资金
            if re.search(r'\b(?:billion|trillion)\b', matched_text, re.IGNORECASE):
                return 'large_amount'
            
            # 百分比
            if '%' in matched_text:
                return 'percentage'
            
            # 货币符号
            if matched_text.startswith('$'):
                return 'currency_symbol'
        
        elif entity_type == 'time':
            # 完整日期
            if re.search(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d+,?\s+\d{4}\b', matched_text):
                return 'full_date'
            
            # 政治时间
            if re.search(r'\b(?:campaign|election|inauguration|presidency|administration)\b', matched_text, re.IGNORECASE):
                return 'political_time'
            
            # 相对时间
            if re.search(r'\b(?:today|yesterday|tomorrow|this week|last week)\b', matched_text, re.IGNORECASE):
                return 'relative_time'
        
        elif entity_type == 'contact':
            # 官方邮箱
            if re.search(r'@(?:whitehouse\.gov|npr\.org|.*\.gov)$', matched_text, re.IGNORECASE):
                return 'official_email'
            
            # URL
            if matched_text.startswith(('http', 'www')):
                return 'url'
            
            # 电话
            if re.search(r'\d{3}[-.\s]\d{3}[-.\s]\d{4}', matched_text):
                return 'phone'
        
        elif entity_type == 'quote':
            # 长引用（可能是重要声明）
            if len(matched_text) > 100:
                return 'political_statement'
            
            # 直接引用
            if matched_text.startswith('"') and matched_text.endswith('"'):
                return 'direct_quote'
        
        return 'default'

    
    def _get_context_boost(self, matched_text: str, entity_type: str, 
                      full_text: str, position: int) -> float:
        """根据上下文获取置信度提升"""
        context_size = 100
        start = max(0, position - context_size)
        end = min(len(full_text), position + len(matched_text) + context_size)
        context = full_text[start:end].lower()
        
        boost = 0.0
        
        if entity_type == 'person':
            # 强烈的人名上下文指标 - 修复正则表达式
            strong_person_indicators = [
                r'\b(?:president|senator|representative|governor|dr|prof|secretary|director|chief)\s*$',  # 职位在前
                r'^\s*(?:said|told|announced|declared|testified|stated|explained|noted)',  # 发言动词在后
                r'\bnpr\'s\s*$',  # NPR归属
                r'\b(?:according to|as)\s*$',  # 引用介绍
            ]
            
            for indicator in strong_person_indicators:
                before_match = full_text[max(0, position-50):position].lower()
                after_match = full_text[position+len(matched_text):position+len(matched_text)+50].lower()
                
                if re.search(indicator, before_match) or re.search(r'^\s*(?:said|told|announced)', after_match):
                    boost += 0.15
                    break
            
            # 减分指标 - 不太可能是人名的上下文
            negative_indicators = [
                r'\b(?:this|that|these|those|it|its|he|she|his|her|him|they|them|their)\s*$',  # 代词在前
                r'^\s*(?:is|was|are|were|will|would|can|could|should|may|might)',  # 动词在后
            ]
            
            for indicator in negative_indicators:
                before_match = full_text[max(0, position-30):position].lower()
                after_match = full_text[position+len(matched_text):position+len(matched_text)+30].lower()
                
                if re.search(indicator, before_match) or re.search(indicator, after_match):
                    boost -= 0.2  # 大幅减分
                    break
                    
        elif entity_type == 'organization':
            # 官方上下文
            if re.search(r'\b(?:official|government|federal|administration|agency|bureau|department)\b', context):
                boost += 0.1
                
        elif entity_type == 'money':
            # 政府/预算上下文
            if re.search(r'\b(?:budget|funding|appropriation|spending|allocation|investment|aid|grant)\b', context):
                boost += 0.15
            
            # 经济/金融上下文
            if re.search(r'\b(?:revenue|profit|loss|cost|price|worth|value|tax|fee)\b', context):
                boost += 0.1
                
        elif entity_type == 'quote':
            # 重要发言人上下文
            if re.search(r'\b(?:president|senator|secretary|director|spokesperson|official)\b', context):
                boost += 0.15
            
            # 正式场合上下文
            if re.search(r'\b(?:conference|hearing|testimony|statement|announcement|speech)\b', context):
                boost += 0.1
        
        return min(0.3, max(-0.3, boost))  # 限制在-0.3到+0.3之间

    def _get_length_boost(self, matched_text: str, entity_type: str) -> float:
        """根据长度获取置信度调整 - 改进版"""
        length = len(matched_text.strip())
        
        if entity_type == 'person':
            if 5 <= length <= 25:  # 合理的人名长度
                return 0.05
            elif length < 3:  # 太短，很可能不是完整人名
                return -0.3
            elif length > 40:  # 太长，可能包含其他内容
                return -0.2
                
        elif entity_type == 'quote':
            if 20 <= length <= 200:  # 合理的引用长度
                return 0.1
            elif length < 10:  # 太短的引用不可信
                return -0.4
            elif length > 300:  # 太长可能包含多个句子
                return -0.1
                
        elif entity_type == 'organization':
            if length < 3:  # 组织名太短
                return -0.3
            elif 3 <= length <= 50:  # 合理长度
                return 0.05
                
        elif entity_type == 'location':
            if length < 2:  # 地名太短
                return -0.3
            elif 2 <= length <= 30:  # 合理长度
                return 0.05
        
        return 0.0



    def _has_overlap(self, span: Tuple[int, int], existing_spans: Set[Tuple[int, int]]) -> bool:
        """检查是否与现有span重叠"""
        start, end = span
        for existing_start, existing_end in existing_spans:
            # 检查是否有重叠
            if not (end <= existing_start or start >= existing_end):
                # 计算重叠程度
                overlap_start = max(start, existing_start)
                overlap_end = min(end, existing_end)
                overlap_length = overlap_end - overlap_start
                
                # 如果重叠超过50%，认为是重复
                min_length = min(end - start, existing_end - existing_start)
                if overlap_length / min_length > 0.5:
                    return True
        return False
    
    """
    改进的验证逻辑
    修改位置：src/extraction/regex_extractor.py 中的 _is_valid_match 方法
    """

    def _is_valid_match(self, matched_text: str, entity_type: str) -> bool:
        """验证匹配是否有效 - 改进版"""
        # 基本长度检查
        text = matched_text.strip()
        if len(text) < 2:
            return False
        
        # 通用无效词汇
        common_invalid = {
            'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
            'is', 'was', 'are', 'were', 'will', 'would', 'can', 'could', 'should', 'may', 'might',
            'this', 'that', 'these', 'those', 'it', 'its', 'he', 'she', 'his', 'her', 'him',
            'they', 'them', 'their', 'we', 'us', 'our', 'i', 'me', 'my', 'you', 'your'
        }
        
        if text.lower() in common_invalid:
            return False
        
        # 特定类型的验证
        if entity_type == 'person':
            return self._validate_person_name(text)
        elif entity_type == 'location':
            return self._validate_location(text)
        elif entity_type == 'organization':
            return self._validate_organization(text)
        elif entity_type == 'money':
            return self._validate_money(text)
        elif entity_type == 'contact':
            return self._validate_contact(text)
        elif entity_type == 'quote':
            return self._validate_quote(text)
        elif entity_type == 'time':
            return self._validate_time(text)
        
        return True

    def _validate_person_name(self, text: str) -> bool:
        """验证人名的有效性"""
        # 无效的人名模式
        invalid_person_patterns = [
            r'^\d+$',  # 纯数字
            r'^[A-Z]$',  # 单个字母
            r'^(?:said|told|announced|declared|stated|explained|noted|added|continued)$',  # 动词
            r'^(?:support|democracy|crucial|important|necessary|significant)$',  # 形容词/名词
            r'^(?:this|that|these|those|it|its)(?:\s+\w+)*$',  # 代词开头
            r'^(?:the|and|or|in|on|at|to|for|of|with|by|from)(?:\s+\w+)*$',  # 介词/连词开头
            r'^\w+(?:\s+said|\s+told|\s+announced)$',  # 以动词结尾
        ]
        
        for pattern in invalid_person_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return False
        
        # 人名应该以大写字母开头
        if not text[0].isupper():
            return False
        
        # 人名长度合理性检查
        if len(text) > 50:  # 太长
            return False
        
        # 人名不应该包含特殊字符（除了点和撇号）
        if re.search(r'[^\w\s\.\'-]', text):
            return False
        
        # 检查是否包含常见的非人名词汇
        non_name_words = {
            'support', 'democracy', 'crucial', 'important', 'necessary', 'significant',
            'government', 'administration', 'policy', 'program', 'system', 'process',
            'development', 'research', 'study', 'report', 'analysis', 'data',
            'information', 'details', 'facts', 'evidence', 'proof', 'confirmation'
        }
        
        words = text.lower().split()
        if any(word in non_name_words for word in words):
            return False
        
        return True

    def _validate_location(self, text: str) -> bool:
        """验证地名的有效性"""
        # 地名应该以大写字母开头
        if not text[0].isupper():
            return False
        
        # 无效的地名模式
        invalid_location_patterns = [
            r'^\d+$',  # 纯数字
            r'^[A-Z]$',  # 单个字母
            r'^(?:said|told|announced|declared|stated)$',  # 动词
            r'^(?:the|and|or|in|on|at)(?:\s+\w+)*$',  # 介词开头
        ]
        
        for pattern in invalid_location_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return False
        
        return True

    def _validate_organization(self, text: str) -> bool:
        """验证组织机构的有效性"""
        # 组织名应该以大写字母开头
        if not text[0].isupper():
            return False
        
        # 组织名不应该太短
        if len(text) < 3:
            return False
        
        return True

    def _validate_money(self, text: str) -> bool:
        """验证金额的有效性"""
        # 金额应该包含数字
        if not re.search(r'\d', text):
            return False
        
        # 检查无效的金额格式
        if re.match(r'^[\$,\.%]+$', text):  # 只有符号
            return False
        
        return True

    def _validate_contact(self, text: str) -> bool:
        """验证联系方式的有效性"""
        # 邮箱格式验证
        if '@' in text:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(email_pattern, text))
        
        # 电话号码验证
        if re.search(r'\d{3}', text):
            return True
        
        # URL验证
        if text.startswith(('http', 'www', 'ftp')):
            return True
        
        return True

    def _validate_quote(self, text: str) -> bool:
        """验证引用内容的有效性"""
        # 引用不应该太短
        if len(text) < 10:
            return False
        
        # 引用不应该只是标点符号
        if re.match(r'^[\.\,\!\?\;\:\"\']+$', text):
            return False
        
        # 引用应该包含实际内容（字母）
        if not re.search(r'[a-zA-Z]', text):
            return False
        
        return True

    def _validate_time(self, text: str) -> bool:
        """验证时间信息的有效性"""
        # 时间表达不应该太短
        if len(text) < 3:
            return False
        
        return True
    
    def _extract_context(self, text: str, start: int, end: int, context_size: int = 60) -> str:
        """提取上下文信息"""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        
        context = text[context_start:context_end]
        
        # 在匹配的实体周围加标记
        entity_in_context = text[start:end]
        relative_start = start - context_start
        relative_end = end - context_start
        
        marked_context = (
            context[:relative_start] + 
            f"[{entity_in_context}]" + 
            context[relative_end:]
        )
        
        # 清理上下文（移除多余的空白）
        marked_context = re.sub(r'\s+', ' ', marked_context.strip())
        
        return marked_context
    
    def _get_pattern_description(self, entity_type: str, pattern_idx: int) -> str:
        """获取模式描述"""
        descriptions = {
            'person': [
                '政治人物和官员', 'NPR记者归属', '引用中的人名', 
                '标准人名格式', '带中间名', '其他人名模式', '补充模式'
            ],
            'location': [
                '政治中心', '国际热点', '美国州名', 
                '城市州格式', '主要城市', '其他地名', '补充模式'
            ],
            'organization': [
                '政府机构', '媒体组织', '大学院校', 
                '企业公司', '国际组织', '其他组织'
            ],
            'time': [
                '新闻时间', '具体日期', '相对时间', 
                '时间段', '政治时间', '时间点', '其他时间', '补充模式'
            ],
            'money': [
                '大额资金', '政府预算', '货币符号', 
                '百分比', '其他金额', '补充模式'
            ],
            'contact': [
                '官方邮箱', '政府电话', '官方网址', 
                '普通邮箱', '其他联系方式', '补充模式'
            ],
            'quote': [
                '政治声明', '直接引用', '专家观点', '间接引用'
            ]
        }
        
        if entity_type in descriptions and pattern_idx < len(descriptions[entity_type]):
            return descriptions[entity_type][pattern_idx]
        
        return f"{entity_type}模式{pattern_idx}"
    
    def _post_process_results(self, results: List[ExtractionResult], text: str) -> List[ExtractionResult]:
        """后处理抽取结果"""
        if not results:
            return results
        
        # 1. 按位置排序
        results.sort(key=lambda x: x.start_position)
        
        # 2. 去重相似结果
        filtered_results = []
        for result in results:
            if not self._is_duplicate_result(result, filtered_results):
                filtered_results.append(result)
        
        # 3. 按置信度过滤和排序
        high_confidence_results = [
            r for r in filtered_results 
            if r.confidence >= self.confidence_threshold
        ]
        
        # 4. 按置信度排序（同类型内部）
        final_results = sorted(high_confidence_results, 
                             key=lambda x: (x.entity_type, -x.confidence, x.start_position))
        
        return final_results
    
    def _is_duplicate_result(self, result: ExtractionResult, existing_results: List[ExtractionResult]) -> bool:
        """检查是否为重复结果"""
        for existing in existing_results:
            # 1. 完全相同的实体
            if (result.entity_type == existing.entity_type and 
                result.entity_value.lower() == existing.entity_value.lower()):
                return True
            
            # 2. 高度重叠的位置
            overlap_start = max(result.start_position, existing.start_position)
            overlap_end = min(result.end_position, existing.end_position)
            
            if overlap_start < overlap_end:  # 有重叠
                overlap_length = overlap_end - overlap_start
                min_length = min(
                    result.end_position - result.start_position,
                    existing.end_position - existing.start_position
                )
                
                if overlap_length / min_length > 0.8:  # 80%重叠
                    # 保留置信度更高的
                    return result.confidence <= existing.confidence
        
        return False
    
    def get_supported_entity_types(self) -> List[str]:
        """获取支持的实体类型列表"""
        return list(self.patterns.keys()) if self.patterns else []
    
    def get_extraction_summary(self, results: List[ExtractionResult]) -> Dict[str, Any]:
        """获取抽取结果摘要"""
        if not results:
            return {
                'total_extractions': 0,
                'entity_type_counts': {},
                'avg_confidence': 0.0,
                'confidence_distribution': {'high': 0, 'medium': 0, 'low': 0},
                'field_distribution': {},
                'top_entities': {}
            }
        
        summary = {
            'total_extractions': len(results),
            'entity_type_counts': {},
            'avg_confidence': 0.0,
            'confidence_distribution': {'high': 0, 'medium': 0, 'low': 0},
            'field_distribution': {},
            'top_entities': {},
            'quality_metrics': {}
        }
        
        # 统计各类型数量
        for result in results:
            entity_type = result.entity_type
            if entity_type not in summary['entity_type_counts']:
                summary['entity_type_counts'][entity_type] = 0
            summary['entity_type_counts'][entity_type] += 1
        
        # 计算平均置信度
        total_confidence = sum(r.confidence for r in results)
        summary['avg_confidence'] = total_confidence / len(results)
        
        # 置信度分布
        for result in results:
            if result.confidence >= 0.9:
                summary['confidence_distribution']['high'] += 1
            elif result.confidence >= 0.7:
                summary['confidence_distribution']['medium'] += 1
            else:
                summary['confidence_distribution']['low'] += 1
        
        # 字段分布
        for result in results:
            field = result.field
            if field not in summary['field_distribution']:
                summary['field_distribution'][field] = 0
            summary['field_distribution'][field] += 1
        
        # 每种类型的热门实体
        entity_counts = {}
        for result in results:
            key = f"{result.entity_type}:{result.entity_value}"
            if key not in entity_counts:
                entity_counts[key] = {'count': 0, 'avg_confidence': 0, 'confidences': []}
            entity_counts[key]['count'] += 1
            entity_counts[key]['confidences'].append(result.confidence)
        
        # 计算平均置信度并获取热门实体
        for entity_type in summary['entity_type_counts']:
            type_entities = []
            for entity_key, stats in entity_counts.items():
                if entity_key.startswith(entity_type + ':'):
                    entity_name = entity_key.split(':', 1)[1]
                    avg_conf = sum(stats['confidences']) / len(stats['confidences'])
                    type_entities.append((entity_name, stats['count'], avg_conf))
            
            # 按出现次数和置信度排序
            type_entities.sort(key=lambda x: (x[1], x[2]), reverse=True)
            summary['top_entities'][entity_type] = type_entities[:5]  # 前5个
        
        # 质量指标
        summary['quality_metrics'] = {
            'high_confidence_ratio': summary['confidence_distribution']['high'] / len(results),
            'avg_entities_per_type': len(results) / len(summary['entity_type_counts']) if summary['entity_type_counts'] else 0,
            'most_common_type': max(summary['entity_type_counts'], key=summary['entity_type_counts'].get) if summary['entity_type_counts'] else None
        }
        
        return summary


# 测试代码
if __name__ == "__main__":
    print("=== 正则表达式抽取器测试 ===")
    
    # 使用NPR风格的测试文本
    test_text = """
    President Joe Biden announced today that the United States will provide
    $2.5 billion in aid to Ukraine. The announcement was made at the White House
    during a meeting with Ukrainian President Volodymyr Zelenskyy on March 15, 2024.
    
    "This support is crucial for democracy," Biden said during the press conference
    at 2:30 PM EST. NPR's David Folkenflik reported from Washington, D.C.
    
    The funding will be distributed through the Department of Defense according to
    Secretary Lloyd Austin. Katherine Maher, NPR's CEO, testified before Congress yesterday.
    
    The Corporation for Public Broadcasting typically receives about 8-10% of revenues
    from federal sources. For information, contact the White House at 202-456-1414 
    or email press@whitehouse.gov. Visit https://npr.org for updates.
    
    "We are committed to supporting our international allies," said the President
    during the ceremony in the Rose Garden.
    """
    
    # 初始化抽取器
    print("初始化抽取器...")
    extractor = RegexExtractor(confidence_threshold=0.6)
    
    if not extractor.initialize():
        print("❌ 抽取器初始化失败")
        exit(1)
    
    print(f"\n📄 测试文本 ({len(test_text)} 字符):")
    print("=" * 80)
    print(test_text)
    print("=" * 80)
    
    # 执行抽取
    print("\n🔍 开始信息抽取...")
    results = extractor.extract_from_text(test_text, doc_id=1, field="content")
    
    print(f"\n✅ 抽取完成！找到 {len(results)} 个实体")
    print("=" * 80)
    
    # 按类型分组显示结果
    results_by_type = {}
    for result in results:
        if result.entity_type not in results_by_type:
            results_by_type[result.entity_type] = []
        results_by_type[result.entity_type].append(result)
    
    for entity_type, type_results in results_by_type.items():
        print(f"\n🏷️ 【{entity_type.upper()}】({len(type_results)} 个)")
        for i, result in enumerate(sorted(type_results, key=lambda x: x.confidence, reverse=True), 1):
            print(f"  {i}. {result.entity_value}")
            print(f"     置信度: {result.confidence:.3f} | {result.metadata.get('match_type', 'default')}")
            print(f"     位置: {result.start_position}-{result.end_position}")
            print(f"     模式: {result.metadata.get('pattern_description', 'unknown')}")
            print(f"     上下文: ...{result.context[:80]}...")
            print()
    
    # 显示抽取摘要
    print("=" * 80)
    print("📊 抽取摘要:")
    summary = extractor.get_extraction_summary(results)
    
    print(f"  📈 总计: {summary['total_extractions']} 个实体")
    print(f"  📊 平均置信度: {summary['avg_confidence']:.3f}")
    print(f"  📋 类型分布: {summary['entity_type_counts']}")
    print(f"  🎯 置信度分布: {summary['confidence_distribution']}")
    print(f"  📄 字段分布: {summary['field_distribution']}")
    print(f"  ⭐ 质量指标:")
    print(f"     高置信度占比: {summary['quality_metrics']['high_confidence_ratio']:.1%}")
    print(f"     平均每类实体数: {summary['quality_metrics']['avg_entities_per_type']:.1f}")
    print(f"     最常见类型: {summary['quality_metrics']['most_common_type']}")
    
    # 显示热门实体
    print(f"\n🔥 热门实体:")
    for entity_type, top_entities in summary['top_entities'].items():
        if top_entities:
            print(f"  {entity_type}: ", end="")
            top_3 = [f"{name}({count})" for name, count, conf in top_entities[:3]]
            print(", ".join(top_3))
    
    print("\n✅ 正则表达式抽取器测试完成！")
    print("🎯 下一步：实现抽取管理器")