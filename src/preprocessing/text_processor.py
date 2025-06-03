import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from typing import List, Set
import string

class TextProcessor:
    """文本处理器：负责文本清洗、分词、去停用词等操作"""
    
    def __init__(self):
        # 下载必需的NLTK数据
        self._download_nltk_data()
        
        # 初始化组件
        self.stemmer = PorterStemmer()
        
        # 尝试加载停用词，如果失败则使用默认列表
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            print("使用默认停用词列表...")
            self.stop_words = self._get_default_stopwords()
        
        # 添加自定义停用词
        custom_stops = {'said', 'say', 'says', 'npr', 'new', 'also', 'one', 'two', 'would', 'could'}
        self.stop_words.update(custom_stops)
    
    def _download_nltk_data(self):
        """下载必需的NLTK数据"""
        import nltk
        
        # 尝试下载所需资源
        resources = ['punkt', 'punkt_tab', 'stopwords']
        for resource in resources:
            try:
                if resource == 'punkt':
                    nltk.data.find('tokenizers/punkt')
                elif resource == 'punkt_tab':
                    nltk.data.find('tokenizers/punkt_tab')
                elif resource == 'stopwords':
                    nltk.data.find('corpora/stopwords')
            except LookupError:
                try:
                    print(f"下载NLTK {resource}数据...")
                    nltk.download(resource, quiet=True)
                except Exception as e:
                    print(f"下载{resource}失败: {e}")
    
    def _get_default_stopwords(self) -> Set[str]:
        """默认停用词列表"""
        return {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", 
            "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 
            'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 
            'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 
            'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 
            'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 
            'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after', 
            'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 
            'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 
            'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 
            'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 
            'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 
            've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', 
            "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 
            'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 
            'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', 
            "wouldn't"
        }
    
    def clean_text(self, text: str) -> str:
        """清洗文本：去除HTML标签、特殊字符等"""
        if not text:
            return ""
        
        # 转换为小写
        text = text.lower()
        
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 去除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 去除邮箱
        text = re.sub(r'\S+@\S+', '', text)
        
        # 去除数字（可选）
        # text = re.sub(r'\d+', '', text)
        
        # 去除多余的空白
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def tokenize(self, text: str) -> List[str]:
        """分词"""
        if not text:
            return []
        
        try:
            # 尝试使用NLTK分词
            tokens = word_tokenize(text)
        except:
            # 如果NLTK分词失败，使用简单的空格分词
            print("NLTK分词失败，使用简单分词...")
            tokens = text.split()
        
        # 过滤掉标点符号和单字符词
        tokens = [token for token in tokens 
                 if token not in string.punctuation and len(token) > 1]
        
        return tokens
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """去除停用词"""
        return [token for token in tokens if token.lower() not in self.stop_words]
    
    def stem_words(self, tokens: List[str]) -> List[str]:
        """词干提取"""
        return [self.stemmer.stem(token) for token in tokens]
    
    def process_text(self, text: str, use_stemming: bool = True) -> List[str]:
        """完整的文本处理流程"""
        # 清洗文本
        cleaned_text = self.clean_text(text)
        
        # 分词
        tokens = self.tokenize(cleaned_text)
        
        # 去停用词
        tokens = self.remove_stopwords(tokens)
        
        # 词干提取（可选）
        if use_stemming:
            tokens = self.stem_words(tokens)
        
        return tokens
    
    def get_vocabulary(self, texts: List[str]) -> Set[str]:
        """获取词汇表"""
        vocab = set()
        for text in texts:
            tokens = self.process_text(text)
            vocab.update(tokens)
        return vocab


# 测试代码
if __name__ == "__main__":
    # 测试文本处理器
    processor = TextProcessor()
    
    # 测试文本
    test_texts = [
        "This is a sample article from NPR. It discusses various topics including politics and culture.",
        "The president said that the new policy would help Americans. Many people are interested in this development.",
        "Scientists at the university are working on <b>important</b> research. Visit https://example.com for more info."
    ]
    
    print("=== 文本处理测试 ===")
    for i, text in enumerate(test_texts):
        print(f"\n原文 {i+1}: {text}")
        
        # 清洗
        cleaned = processor.clean_text(text)
        print(f"清洗后: {cleaned}")
        
        # 分词
        tokens = processor.tokenize(cleaned)
        print(f"分词: {tokens}")
        
        # 去停用词
        no_stops = processor.remove_stopwords(tokens)
        print(f"去停用词: {no_stops}")
        
        # 词干提取
        stemmed = processor.stem_words(no_stops)
        print(f"词干提取: {stemmed}")
        
        # 完整处理
        processed = processor.process_text(text)
        print(f"完整处理: {processed}")
    
    # 测试词汇表构建
    print(f"\n=== 词汇表 ===")
    vocab = processor.get_vocabulary(test_texts)
    print(f"词汇表大小: {len(vocab)}")
    print(f"词汇表示例: {list(vocab)[:10]}")