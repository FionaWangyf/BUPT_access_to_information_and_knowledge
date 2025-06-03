import math
import datetime
from typing import List, Dict, Any, Tuple
from dateutil import parser

class TemporalScoring:
    """时间新鲜度评分：根据文档发布时间调整相关性分数"""
    
    def __init__(self, decay_factor: float = 0.1, max_days: int = 365):
        """
        初始化时间新鲜度评分器
        
        Args:
            decay_factor: 时间衰减因子，控制时间衰减的速度 (0.1-1.0)
            max_days: 最大考虑天数，超过此天数的文档权重为最小值
        """
        self.decay_factor = decay_factor
        self.max_days = max_days
        self.current_date = datetime.datetime.now()
        
        # 统计信息
        self.document_dates = []
        self.date_range_days = 0
        self.oldest_date = None
        self.newest_date = None
    
    def analyze_document_dates(self, publish_times: List[str]) -> None:
        """分析文档日期分布，用于优化时间衰减参数"""
        print("分析文档时间分布...")
        
        self.document_dates = []
        valid_dates = []
        
        for i, time_str in enumerate(publish_times):
            try:
                if time_str and time_str.strip():
                    # 解析日期字符串
                    doc_date = self._parse_date(time_str)
                    if doc_date:
                        self.document_dates.append(doc_date)
                        valid_dates.append(doc_date)
                    else:
                        self.document_dates.append(None)
                else:
                    self.document_dates.append(None)
            except Exception as e:
                print(f"解析日期失败 (文档{i}): {time_str} - {e}")
                self.document_dates.append(None)
        
        if valid_dates:
            self.oldest_date = min(valid_dates)
            self.newest_date = max(valid_dates)
            self.date_range_days = (self.newest_date - self.oldest_date).days
            
            print(f"日期分析完成:")
            print(f"  有效日期数: {len(valid_dates)}/{len(publish_times)}")
            print(f"  最早日期: {self.oldest_date.strftime('%Y-%m-%d')}")
            print(f"  最新日期: {self.newest_date.strftime('%Y-%m-%d')}")
            print(f"  日期跨度: {self.date_range_days} 天")
        else:
            print("⚠️ 没有找到有效的日期信息")
    
    def _parse_date(self, date_str: str) -> datetime.datetime:
        """解析各种日期格式"""
        if not date_str or not date_str.strip():
            return None
        
        try:
            # 尝试使用dateutil解析（支持多种格式）
            return parser.parse(date_str)
        except:
            try:
                # 尝试常见格式
                formats = [
                    '%Y-%m-%d',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%d %H:%M:%S',
                    '%m/%d/%Y',
                    '%d/%m/%Y'
                ]
                
                for fmt in formats:
                    try:
                        return datetime.datetime.strptime(date_str, fmt)
                    except:
                        continue
                
                return None
            except:
                return None
    
    def calculate_temporal_scores(self, document_indices: List[int] = None) -> List[float]:
        """
        计算时间新鲜度分数
        
        Args:
            document_indices: 要计算的文档索引列表，None表示所有文档
            
        Returns:
            时间新鲜度分数列表 (0.0-1.0)
        """
        if not self.document_dates:
            print("⚠️ 未分析文档日期，请先调用 analyze_document_dates()")
            return []
        
        if document_indices is None:
            document_indices = list(range(len(self.document_dates)))
        
        temporal_scores = []
        
        for doc_idx in document_indices:
            if doc_idx < len(self.document_dates):
                doc_date = self.document_dates[doc_idx]
                score = self._calculate_single_temporal_score(doc_date)
                temporal_scores.append(score)
            else:
                temporal_scores.append(0.0)
        
        return temporal_scores
    
    def _calculate_single_temporal_score(self, doc_date: datetime.datetime) -> float:
        """计算单个文档的时间新鲜度分数"""
        if not doc_date:
            return 0.1  # 无日期信息的文档给予最低分数
        
        # 计算天数差
        days_diff = (self.current_date - doc_date).days
        
        if days_diff < 0:
            # 未来日期（可能是数据错误），给予最高分数
            return 1.0
        
        if days_diff > self.max_days:
            # 超过最大考虑天数，给予最低分数
            return 0.01
        
        # 使用指数衰减函数计算时间新鲜度
        # score = exp(-decay_factor * days_diff / max_days)
        normalized_days = days_diff / self.max_days
        temporal_score = math.exp(-self.decay_factor * normalized_days)
        
        # 确保分数在合理范围内
        return max(0.01, min(1.0, temporal_score))
    
    def get_adaptive_decay_factor(self) -> float:
        """根据文档日期分布自适应调整衰减因子"""
        if not self.document_dates or self.date_range_days <= 0:
            return self.decay_factor
        
        # 如果文档日期跨度很大，减小衰减因子（让旧文档有更多机会）
        # 如果文档日期跨度很小，增大衰减因子（更强调新鲜度）
        if self.date_range_days > 1000:  # 超过3年
            adaptive_factor = self.decay_factor * 0.5
        elif self.date_range_days > 365:  # 超过1年
            adaptive_factor = self.decay_factor * 0.7
        elif self.date_range_days < 30:   # 少于1个月
            adaptive_factor = self.decay_factor * 1.5
        else:
            adaptive_factor = self.decay_factor
        
        return max(0.01, min(2.0, adaptive_factor))
    
    def combine_content_and_temporal_scores(self, content_scores: List[float], 
                                          document_indices: List[int],
                                          temporal_weight: float = 0.2) -> List[float]:
        """
        结合内容相关性和时间新鲜度分数
        
        Args:
            content_scores: 内容相关性分数列表
            document_indices: 对应的文档索引列表
            temporal_weight: 时间新鲜度权重 (0.0-1.0)
            
        Returns:
            综合分数列表
        """
        if len(content_scores) != len(document_indices):
            raise ValueError("内容分数和文档索引列表长度不匹配")
        
        temporal_scores = self.calculate_temporal_scores(document_indices)
        
        if len(temporal_scores) != len(content_scores):
            raise ValueError("时间分数和内容分数列表长度不匹配")
        
        combined_scores = []
        content_weight = 1.0 - temporal_weight
        
        for content_score, temporal_score in zip(content_scores, temporal_scores):
            # 线性组合
            combined_score = content_weight * content_score + temporal_weight * temporal_score
            combined_scores.append(combined_score)
        
        return combined_scores
    
    def get_temporal_explanation(self, doc_index: int) -> Dict[str, Any]:
        """解释时间新鲜度分数计算过程"""
        if doc_index >= len(self.document_dates):
            return {"错误": "文档索引超出范围"}
        
        doc_date = self.document_dates[doc_index]
        if not doc_date:
            return {
                "文档索引": doc_index,
                "发布日期": "无日期信息",
                "时间新鲜度分数": 0.1,
                "说明": "缺少日期信息，给予最低分数"
            }
        
        days_diff = (self.current_date - doc_date).days
        temporal_score = self._calculate_single_temporal_score(doc_date)
        
        return {
            "文档索引": doc_index,
            "发布日期": doc_date.strftime('%Y-%m-%d'),
            "当前日期": self.current_date.strftime('%Y-%m-%d'),
            "天数差": days_diff,
            "标准化天数": days_diff / self.max_days,
            "衰减因子": self.decay_factor,
            "时间新鲜度分数": temporal_score,
            "计算公式": f"exp(-{self.decay_factor} * {days_diff}/{self.max_days})"
        }
    
    def get_temporal_stats(self) -> Dict[str, Any]:
        """获取时间新鲜度统计信息"""
        if not self.document_dates:
            return {"状态": "未初始化"}
        
        valid_dates = [d for d in self.document_dates if d is not None]
        
        if not valid_dates:
            return {"状态": "无有效日期"}
        
        # 计算所有文档的时间分数
        all_temporal_scores = self.calculate_temporal_scores()
        
        return {
            "文档总数": len(self.document_dates),
            "有效日期数": len(valid_dates),
            "最早日期": self.oldest_date.strftime('%Y-%m-%d'),
            "最新日期": self.newest_date.strftime('%Y-%m-%d'),
            "日期跨度天数": self.date_range_days,
            "当前衰减因子": self.decay_factor,
            "自适应衰减因子": self.get_adaptive_decay_factor(),
            "平均时间分数": sum(all_temporal_scores) / len(all_temporal_scores),
            "最高时间分数": max(all_temporal_scores),
            "最低时间分数": min(all_temporal_scores),
            "高分数文档数": sum(1 for score in all_temporal_scores if score > 0.8),
            "中等分数文档数": sum(1 for score in all_temporal_scores if 0.3 <= score <= 0.8),
            "低分数文档数": sum(1 for score in all_temporal_scores if score < 0.3)
        }


# 测试代码
if __name__ == "__main__":
    print("=== 时间新鲜度评分测试 ===")
    
    # 测试日期数据
    test_dates = [
        "2025-05-30",  # 最新
        "2025-05-15",  # 2周前
        "2025-04-01",  # 2个月前
        "2024-12-01",  # 6个月前
        "2024-01-01",  # 1年多前
        "2023-01-01",  # 2年多前
        "",            # 无日期
        "invalid",     # 无效日期
    ]
    
    print(f"测试日期: {test_dates}")
    
    # 创建时间评分器
    temporal_scorer = TemporalScoring(decay_factor=0.3, max_days=365)
    
    # 分析文档日期
    temporal_scorer.analyze_document_dates(test_dates)
    
    # 计算时间分数
    temporal_scores = temporal_scorer.calculate_temporal_scores()
    
    print(f"\n=== 时间分数结果 ===")
    for i, (date_str, score) in enumerate(zip(test_dates, temporal_scores)):
        print(f"文档{i}: {date_str} -> 时间分数: {score:.3f}")
    
    # 显示详细解释
    print(f"\n=== 分数解释 ===")
    for i in range(3):  # 解释前3个文档
        explanation = temporal_scorer.get_temporal_explanation(i)
        print(f"\n文档{i}的时间分数解释:")
        for key, value in explanation.items():
            print(f"  {key}: {value}")
    
    # 显示统计信息
    print(f"\n=== 时间评分统计 ===")
    stats = temporal_scorer.get_temporal_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # 测试与内容分数结合
    print(f"\n=== 综合分数测试 ===")
    mock_content_scores = [0.9, 0.7, 0.8, 0.6, 0.5, 0.4, 0.2, 0.1]
    document_indices = list(range(len(mock_content_scores)))
    
    combined_scores = temporal_scorer.combine_content_and_temporal_scores(
        mock_content_scores, document_indices, temporal_weight=0.3
    )
    
    print("内容分数 | 时间分数 | 综合分数")
    print("-" * 35)
    for i, (content, temporal, combined) in enumerate(zip(mock_content_scores, temporal_scores, combined_scores)):
        print(f"文档{i}: {content:.3f} | {temporal:.3f} | {combined:.3f}")
    
    # 测试自适应衰减因子
    print(f"\n=== 自适应衰减因子 ===")
    print(f"原始衰减因子: {temporal_scorer.decay_factor}")
    print(f"自适应衰减因子: {temporal_scorer.get_adaptive_decay_factor():.3f}")