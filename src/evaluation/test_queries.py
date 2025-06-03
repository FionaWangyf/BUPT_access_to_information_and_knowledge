from typing import List, Dict, Any
import json
import os

class TestQuery:
    """测试查询类：存储查询和相关文档信息"""
    
    def __init__(self, query_id: int, query_text: str, description: str = ""):
        self.query_id = query_id
        self.query_text = query_text
        self.description = description
        self.relevant_docs = []  # 人工标注的相关文档ID列表
        self.relevance_scores = {}  # {doc_id: relevance_score} 相关度评分
        self.system_results = []  # 系统返回的结果
    
    def add_relevant_document(self, doc_id: int, relevance_score: int = 1):
        """添加相关文档"""
        if doc_id not in self.relevant_docs:
            self.relevant_docs.append(doc_id)
        self.relevance_scores[doc_id] = relevance_score
    
    def set_system_results(self, results: List[int]):
        """设置系统搜索结果"""
        self.system_results = results
    
    def __str__(self):
        return f"TestQuery(id={self.query_id}, query='{self.query_text}', relevant_docs={len(self.relevant_docs)})"


class TestQueryManager:
    """测试查询管理器：管理测试查询集合"""
    
    def __init__(self):
        self.test_queries = []
        self.queries_file = "results/test_queries.json"
    
    def create_default_queries(self) -> List[TestQuery]:
        """创建默认的测试查询集合"""
        default_queries = [
            TestQuery(1, "climate change", "关于气候变化的新闻"),
            TestQuery(2, "health care", "医疗保健相关报道"),
            TestQuery(3, "education", "教育相关新闻"),
            TestQuery(4, "politics election", "政治和选举新闻"),
            TestQuery(5, "technology AI", "科技和人工智能"),
            TestQuery(6, "economy financial", "经济和金融新闻"),
            TestQuery(7, "science research", "科学研究报道"),
            TestQuery(8, "culture arts", "文化艺术新闻"),
            TestQuery(9, "sports", "体育新闻"),
            TestQuery(10, "immigration", "移民相关报道"),
            TestQuery(11, "coronavirus COVID", "新冠疫情相关"),
            TestQuery(12, "vaccine", "疫苗相关新闻"),
            TestQuery(13, "social media", "社交媒体相关"),
            TestQuery(14, "mental health", "心理健康"),
            TestQuery(15, "environment pollution", "环境和污染")
        ]
        
        self.test_queries = default_queries
        return default_queries
    
    def add_custom_query(self, query_text: str, description: str = "") -> TestQuery:
        """添加自定义查询"""
        # 生成新的查询ID
        new_id = max([q.query_id for q in self.test_queries], default=0) + 1
        
        # 创建新的查询
        query = TestQuery(new_id, query_text, description)
        self.test_queries.append(query)
        
        # 保存更新后的查询列表
        self.save_queries()
        
        print(f"已添加新查询:")
        print(f"ID: {new_id}")
        print(f"查询: {query_text}")
        print(f"描述: {description}")
        
        return query
    
    def add_query(self, query: TestQuery):
        """添加测试查询"""
        self.test_queries.append(query)
    
    def get_query(self, query_id: int) -> TestQuery:
        """根据ID获取查询"""
        for query in self.test_queries:
            if query.query_id == query_id:
                return query
        return None
    
    def get_all_queries(self) -> List[TestQuery]:
        """获取所有测试查询"""
        return self.test_queries
    
    def save_queries(self, filepath: str = None):
        """保存查询到文件"""
        if filepath is None:
            filepath = self.queries_file
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 转换为可序列化的格式
        queries_data = []
        for query in self.test_queries:
            query_data = {
                'query_id': query.query_id,
                'query_text': query.query_text,
                'description': query.description,
                'relevant_docs': query.relevant_docs,
                'relevance_scores': query.relevance_scores,
                'system_results': query.system_results
            }
            queries_data.append(query_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(queries_data, f, indent=2, ensure_ascii=False)
        
        print(f"测试查询已保存到: {filepath}")
    
    def load_queries(self, filepath: str = None):
        """从文件加载查询"""
        if filepath is None:
            filepath = self.queries_file
        
        if not os.path.exists(filepath):
            print(f"查询文件不存在: {filepath}")
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                queries_data = json.load(f)
            
            self.test_queries = []
            for query_data in queries_data:
                query = TestQuery(
                    query_data['query_id'],
                    query_data['query_text'],
                    query_data.get('description', '')
                )
                query.relevant_docs = query_data.get('relevant_docs', [])
                query.relevance_scores = {int(k): v for k, v in query_data.get('relevance_scores', {}).items()}
                query.system_results = query_data.get('system_results', [])
                self.test_queries.append(query)
            
            print(f"成功加载 {len(self.test_queries)} 个测试查询")
            return True
            
        except Exception as e:
            print(f"加载查询文件时出错: {e}")
            return False
    
    def get_queries_summary(self) -> Dict[str, Any]:
        """获取查询集合摘要"""
        if not self.test_queries:
            return {}
        
        total_relevant = sum(len(q.relevant_docs) for q in self.test_queries)
        total_results = sum(len(q.system_results) for q in self.test_queries)
        
        return {
            "查询总数": len(self.test_queries),
            "总相关文档数": total_relevant,
            "平均每查询相关文档数": total_relevant / len(self.test_queries),
            "总系统结果数": total_results,
            "已完成标注的查询数": sum(1 for q in self.test_queries if q.relevant_docs),
            "已有系统结果的查询数": sum(1 for q in self.test_queries if q.system_results)
        }
    
    def display_queries(self):
        """显示所有查询"""
        print(f"\n测试查询集合 (共 {len(self.test_queries)} 条)")
        print("=" * 80)
        
        for query in self.test_queries:
            print(f"ID: {query.query_id}")
            print(f"查询: {query.query_text}")
            print(f"描述: {query.description}")
            print(f"相关文档: {len(query.relevant_docs)} 个")
            print(f"系统结果: {len(query.system_results)} 个")
            print("-" * 40)


# 测试代码
if __name__ == "__main__":
    # 测试查询管理器
    print("=== 测试查询管理器测试 ===")
    
    manager = TestQueryManager()
    
    # 创建默认查询
    queries = manager.create_default_queries()
    print(f"创建了 {len(queries)} 个默认查询")
    
    # 显示查询
    manager.display_queries()
    
    # 测试添加相关文档
    query1 = manager.get_query(1)
    if query1:
        query1.add_relevant_document(5, 2)  # 文档5，相关度2
        query1.add_relevant_document(12, 3)  # 文档12，相关度3
        query1.set_system_results([5, 12, 8, 15, 23])
        
        print(f"\n更新后的查询1:")
        print(f"相关文档: {query1.relevant_docs}")
        print(f"相关度评分: {query1.relevance_scores}")
        print(f"系统结果: {query1.system_results}")
    
    # 获取摘要
    print(f"\n=== 查询集合摘要 ===")
    summary = manager.get_queries_summary()
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    # 测试保存和加载
    print(f"\n=== 保存和加载测试 ===")
    test_file = "test_queries_demo.json"
    manager.save_queries(test_file)
    
    # 创建新的管理器并加载
    new_manager = TestQueryManager()
    if new_manager.load_queries(test_file):
        print("查询加载成功")
        loaded_summary = new_manager.get_queries_summary()
        print(f"加载的查询数: {loaded_summary['查询总数']}")
    
    # 清理测试文件
    if os.path.exists(test_file):
        os.remove(test_file)