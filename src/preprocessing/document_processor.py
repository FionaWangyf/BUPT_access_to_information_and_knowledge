from typing import List, Dict, Any
from .data_loader import DataLoader
from .text_processor import TextProcessor

class Document:
    """文档类：表示一篇文章"""
    
    def __init__(self, doc_id: int, title: str, content: str, summary: str, 
                 url: str, publish_time: str, author: str = ""):
        self.doc_id = doc_id
        self.title = title
        self.content = content
        self.summary = summary
        self.url = url
        self.publish_time = publish_time
        self.author = author
        
        # 处理后的文本
        self.processed_title = []
        self.processed_content = []
        self.processed_summary = []
        self.all_tokens = []  # 所有处理后的词汇
    
    def __str__(self):
        return f"Document(id={self.doc_id}, title='{self.title[:50]}...', tokens={len(self.all_tokens)})"


class DocumentProcessor:
    """文档处理器：将原始文章数据转换为结构化文档"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.documents = []
    
    def process_articles(self, articles: List[Dict[str, Any]]) -> List[Document]:
        """处理文章列表，返回Document对象列表"""
        self.documents = []
        
        print("开始处理文档...")
        for i, article in enumerate(articles):
            # 创建文档对象
            doc = Document(
                doc_id=i,
                title=article.get('title', ''),
                content=article.get('content', ''),
                summary=article.get('summary', ''),
                url=article.get('url', ''),
                publish_time=article.get('publish_time', ''),
                author=article.get('author', '')
            )
            
            # 处理文本
            if doc.title:
                doc.processed_title = self.text_processor.process_text(doc.title)
            
            if doc.content:
                doc.processed_content = self.text_processor.process_text(doc.content)
            
            if doc.summary:
                doc.processed_summary = self.text_processor.process_text(doc.summary)
            
            # 合并所有处理后的词汇
            doc.all_tokens = doc.processed_title + doc.processed_content + doc.processed_summary
            
            self.documents.append(doc)
            
            # 显示进度
            if (i + 1) % 50 == 0:
                print(f"已处理 {i + 1}/{len(articles)} 篇文档")
        
        print(f"文档处理完成！共处理 {len(self.documents)} 篇文档")
        return self.documents
    
    def get_document_stats(self) -> Dict[str, Any]:
        """获取文档统计信息"""
        if not self.documents:
            return {}
        
        total_tokens = sum(len(doc.all_tokens) for doc in self.documents)
        vocab = set()
        for doc in self.documents:
            vocab.update(doc.all_tokens)
        
        return {
            "文档总数": len(self.documents),
            "总词汇数": total_tokens,
            "平均每文档词汇数": total_tokens / len(self.documents),
            "唯一词汇数": len(vocab),
            "有标题的文档数": sum(1 for doc in self.documents if doc.processed_title),
            "有内容的文档数": sum(1 for doc in self.documents if doc.processed_content),
            "有摘要的文档数": sum(1 for doc in self.documents if doc.processed_summary),
        }
    
    def preview_documents(self, num: int = 3) -> None:
        """预览处理后的文档"""
        if not self.documents:
            print("没有文档可预览")
            return
        
        for i, doc in enumerate(self.documents[:num]):
            print(f"\n=== 文档 {doc.doc_id} ===")
            print(f"原标题: {doc.title}")
            print(f"处理后标题: {doc.processed_title}")
            print(f"原摘要: {doc.summary[:100]}...")
            print(f"处理后摘要: {doc.processed_summary}")
            print(f"内容词汇数: {len(doc.processed_content)}")
            print(f"总词汇数: {len(doc.all_tokens)}")
            print(f"前10个词汇: {doc.all_tokens[:10]}")


# 测试代码
if __name__ == "__main__":
    # 测试文档处理器
    print("=== 测试文档处理器 ===")
    
    # 加载数据
    loader = DataLoader("../../data/npr_articles.json")
    articles = loader.load_articles()
    
    if articles:
        # 只处理前10篇文章进行测试
        test_articles = articles[:10]
        
        # 处理文档
        doc_processor = DocumentProcessor()
        documents = doc_processor.process_articles(test_articles)
        
        # 显示统计信息
        print("\n=== 文档统计 ===")
        stats = doc_processor.get_document_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # 预览文档
        print("\n=== 文档预览 ===")
        doc_processor.preview_documents(2)