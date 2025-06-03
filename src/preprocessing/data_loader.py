import json
import pandas as pd
from typing import List, Dict, Any

class DataLoader:
    """数据加载器：负责从JSON文件中加载NPR文章数据"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.articles = []
    
    def load_articles(self) -> List[Dict[str, Any]]:
        """加载文章数据"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.articles = json.load(f)
            print(f"成功加载 {len(self.articles)} 篇文章")
            return self.articles
        except Exception as e:
            print(f"加载数据时出错: {e}")
            return []
    
    def get_article_info(self) -> Dict[str, Any]:
        """获取数据集的基本信息"""
        if not self.articles:
            return {}
        
        info = {
            "总文章数": len(self.articles),
            "字段信息": list(self.articles[0].keys()) if self.articles else [],
            "有URL的文章数": sum(1 for article in self.articles if article.get('url')),
            "有标题的文章数": sum(1 for article in self.articles if article.get('title')),
            "有内容的文章数": sum(1 for article in self.articles if article.get('content')),
            "有摘要的文章数": sum(1 for article in self.articles if article.get('summary')),
        }
        return info
    
    def preview_articles(self, num: int = 3) -> None:
        """预览前几篇文章"""
        if not self.articles:
            print("没有数据可预览")
            return
        
        for i, article in enumerate(self.articles[:num]):
            print(f"\n=== 文章 {i+1} ===")
            print(f"标题: {article.get('title', 'N/A')}")
            print(f"URL: {article.get('url', 'N/A')}")
            print(f"发布时间: {article.get('publish_time', 'N/A')}")
            print(f"摘要: {article.get('summary', 'N/A')[:100]}...")
            print(f"内容长度: {len(article.get('content', ''))}")


# 测试代码
if __name__ == "__main__":
    # 测试数据加载器
    loader = DataLoader("../../data/npr_articles.json")
    articles = loader.load_articles()
    
    if articles:
        print("\n=== 数据集信息 ===")
        info = loader.get_article_info()
        for key, value in info.items():
            print(f"{key}: {value}")
        
        print("\n=== 文章预览 ===")
        loader.preview_articles(2)