import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime
import random


class NPRNewsCrawler:
    def __init__(self):
        self.base_url = "https://www.npr.org"
        self.news_url = "https://www.npr.org/sections/news/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.articles = []

    def get_page_content(self, url, max_retries=3):
        """获取页面内容，带重试机制"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                print(f"尝试 {attempt + 1} 失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(3, 6))
                else:
                    return None
        return None

    def extract_article_links(self, soup):
        """从页面中提取文章链接"""
        links = set()

        # NPR网站的文章链接选择器
        selectors = [
            'h2 a[href]',  # 标题链接
            'h3 a[href]',  # 副标题链接
            '.item-info h3 a',  # 新闻项目链接
            '.story-text h3 a',  # 故事文本链接
            'article h2 a',  # 文章标题
            'article h3 a',  # 文章副标题
            '.story-wrap h2 a',  # 故事包装器
            '.story-wrap h3 a',
            '.teaser h2 a',  # 预告链接
            '.teaser h3 a'
        ]

        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href and self.is_valid_article_url(href):
                    full_url = urljoin(self.base_url, href)
                    links.add(full_url)

        # 查找所有包含年份的链接
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href')
            if href and self.is_valid_article_url(href):
                full_url = urljoin(self.base_url, href)
                links.add(full_url)

        return list(links)

    def is_valid_article_url(self, url):
        """检查是否为有效的文章URL"""
        if not url:
            return False

        # 排除不需要的链接
        exclude_patterns = [
            '/podcasts/', '/music/', '/programs/', '/shows/', '/series/',
            '/newsletters/', '/events/', '/about/', '/contact/', '/support/',
            '.jpg', '.png', '.gif', '.pdf', '.mp3', '.mp4',
            'mailto:', 'tel:', '#', 'javascript:', 'twitter.com', 'facebook.com',
            'instagram.com', 'youtube.com', '/donate/', '/shop/', '/careers/'
        ]

        for pattern in exclude_patterns:
            if pattern in url.lower():
                return False

        # NPR文章URL通常包含年月日格式
        if re.search(r'/20(2[0-4]|1\d)/\d{2}/\d{2}/', url):
            return True

        # 或者包含sections/news等路径
        if any(pattern in url for pattern in
               ['/sections/', '/news/', '/world/', '/politics/', '/business/', '/health/', '/science/', '/national/',
                '/climate/', '/codeswitch/', '/technology/', 'education']):
            return True

        return False

    def extract_article_content(self, url):
        """提取单篇文章的内容"""
        print(f"正在爬取文章: {url}")

        response = self.get_page_content(url)
        if not response:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # 提取标题
        title = self.extract_title(soup)
        if not title:
            return None

        # 提取正文内容
        content = self.extract_content(soup)
        if not content or len(content.split()) < 50:  # 至少50个单词
            return None

        # 提取发布时间
        publish_time = self.extract_publish_time(soup)

        # 提取作者
        author = self.extract_author(soup)

        # 提取摘要
        summary = self.extract_summary(soup)

        article_data = {
            'url': url,
            'title': title.strip(),
            'content': content.strip(),
            'summary': summary,
            'author': author,
            'publish_time': publish_time,
            'word_count': len(content.split()),
            'crawl_time': datetime.now().isoformat()
        }

        return article_data

    def extract_title(self, soup):
        """提取文章标题"""
        title_selectors = [
            'h1.storytitle',
            'h1[data-testid="headline"]',
            'h1.title',
            '.storytitle h1',
            'article h1',
            '.story-header h1',
            'h1',
            'title'
        ]

        for selector in title_selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                title = element.get_text().strip()
                # 清理标题，移除网站名称
                title = re.sub(r'\s*:\s*NPR$', '', title)
                title = re.sub(r'\s*\|\s*NPR$', '', title)
                return title

        return None

    def extract_content(self, soup):
        """提取文章正文"""
        # 移除不需要的标签
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
            tag.decompose()

        content_selectors = [
            '#storytext',
            '.storytext',
            '[data-testid="story-text"]',
            '.story-text',
            'article .story-text',
            '.story-body',
            'article .body',
            '.post-body'
        ]

        content_parts = []

        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # 获取所有段落
                paragraphs = element.find_all(['p', 'div'])
                for p in paragraphs:
                    text = p.get_text().strip()
                    # 过滤掉太短的段落和广告文本
                    if (text and len(text) > 30 and
                            not re.search(r'(subscribe|newsletter|podcast|follow us|copyright)', text.lower())):
                        content_parts.append(text)
                break

        # 如果没有找到特定的内容区域，尝试提取文章标签内的段落
        if not content_parts:
            article_tag = soup.find('article')
            if article_tag:
                paragraphs = article_tag.find_all('p')
                for p in paragraphs:
                    text = p.get_text().strip()
                    if text and len(text) > 30:
                        content_parts.append(text)

        # 最后尝试提取所有长段落
        if not content_parts:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 50:
                    content_parts.append(text)

        return '\n\n'.join(content_parts) if content_parts else ""

    def extract_summary(self, soup):
        """提取文章摘要"""
        summary_selectors = [
            '.teaser',
            '.story-teaser',
            '[data-testid="teaser"]',
            '.excerpt',
            '.summary',
            'meta[name="description"]'
        ]

        for selector in summary_selectors:
            if selector.startswith('meta'):
                element = soup.select_one(selector)
                if element:
                    return element.get('content', '').strip()
            else:
                element = soup.select_one(selector)
                if element and element.get_text().strip():
                    return element.get_text().strip()

        return None

    def extract_publish_time(self, soup):
        """提取发布时间"""
        time_selectors = [
            'time[datetime]',
            '.story-date time',
            '.dateblock time',
            '[data-testid="story-date"]',
            '.story-meta time'
        ]

        for selector in time_selectors:
            element = soup.select_one(selector)
            if element:
                datetime_attr = element.get('datetime')
                if datetime_attr:
                    return datetime_attr
                return element.get_text().strip()

        # 尝试从文本中提取日期
        date_patterns = [
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+20\d{2}',
            r'\d{1,2}/\d{1,2}/20\d{2}',
            r'20\d{2}-\d{2}-\d{2}'
        ]

        page_text = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, page_text)
            if match:
                return match.group()

        return None

    def extract_author(self, soup):
        """提取作者信息"""
        author_selectors = [
            '.byline a',
            '.story-byline a',
            '[data-testid="byline"] a',
            '.author-name',
            '.byline-name',
            '.story-meta .author'
        ]

        authors = []
        for selector in author_selectors:
            elements = soup.select(selector)
            for element in elements:
                author_name = element.get_text().strip()
                if author_name and author_name not in authors:
                    authors.append(author_name)

        return ', '.join(authors) if authors else None

    def crawl_articles(self, target_count=100):
        """爬取指定数量的文章"""
        print(f"开始爬取NPR新闻，目标文章数: {target_count}")

        # 从多个NPR栏目页面收集文章链接
        all_links = set()

        pages_to_crawl = [
            "https://www.npr.org/sections/news/",
            "https://www.npr.org/sections/national/",
            "https://www.npr.org/sections/world/",
            "https://www.npr.org/sections/politics/",
            "https://www.npr.org/sections/business/",
            "https://www.npr.org/sections/health/",
            "https://www.npr.org/sections/science/",
            "https://www.npr.org/sections/climate/",
            "https://www.npr.org/sections/codeswitch/",
            "https://www.npr.org/sections/technology/",
            "https://www.npr.org/sections/education/",
            "https://www.npr.org/"  # 主页
        ]

        print("正在收集文章链接...")
        for page_url in pages_to_crawl:
            print(f"正在访问: {page_url}")
            response = self.get_page_content(page_url)
            if response:
                soup = BeautifulSoup(response.content, 'html.parser')
                links = self.extract_article_links(soup)
                all_links.update(links)
                print(f"从 {page_url} 收集到 {len(links)} 个链接")
            else:
                print(f"无法访问: {page_url}")
            time.sleep(random.uniform(2, 4))

        print(f"总共收集到 {len(all_links)} 个文章链接")

        # 爬取文章内容
        successful_count = 0
        failed_count = 0

        for i, article_url in enumerate(list(all_links)[:target_count * 3], 1):  # 多收集一些以防失败
            if successful_count >= target_count:
                break

            print(f"\n进度: {i}/{min(len(all_links), target_count * 3)} - 成功: {successful_count} - 失败: {failed_count}")

            try:
                article_data = self.extract_article_content(article_url)

                if article_data:
                    self.articles.append(article_data)
                    successful_count += 1
                    print(f"✓ 成功爬取: {article_data['title'][:60]}...")
                else:
                    failed_count += 1
                    print(f"✗ 爬取失败: {article_url}")

                # 随机延时，避免被反爬
                time.sleep(random.uniform(2, 5))

            except Exception as e:
                failed_count += 1
                print(f"✗ 爬取出错: {article_url} - {str(e)}")
                continue

        print(f"\n爬取完成！成功: {successful_count}, 失败: {failed_count}")
        return self.articles

    def save_to_json(self, filename="npr_articles.json"):
        """保存数据为JSON格式"""
        if not os.path.exists('data'):
            os.makedirs('data')

        filepath = os.path.join('data', filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=2)

        print(f"数据已保存到: {filepath}")
        print(f"共保存 {len(self.articles)} 篇文章")

    def save_to_text_files(self, folder_name="npr_articles"):
        """将每篇文章保存为单独的文本文件"""
        if not os.path.exists('data'):
            os.makedirs('data')

        folder_path = os.path.join('data', folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for i, article in enumerate(self.articles, 1):
            # 创建安全的文件名
            safe_title = re.sub(r'[^\w\s-]', '', article['title'])[:50]
            filename = f"{i:03d}_{safe_title}.txt"
            filepath = os.path.join(folder_path, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Title: {article['title']}\n")
                f.write(f"URL: {article['url']}\n")
                f.write(f"Author: {article.get('author', 'Unknown')}\n")
                f.write(f"Publish Time: {article.get('publish_time', 'Unknown')}\n")
                f.write(f"Summary: {article.get('summary', 'No summary')}\n")
                f.write(f"Word Count: {article['word_count']}\n")
                f.write(f"Crawl Time: {article['crawl_time']}\n")
                f.write("-" * 80 + "\n\n")
                f.write(article['content'])

        print(f"文章已保存到文件夹: {folder_path}")
        print(f"共保存 {len(self.articles)} 个文本文件")

    def get_statistics(self):
        """输出爬取统计信息"""
        if not self.articles:
            print("没有爬取到文章数据")
            return

        total_articles = len(self.articles)
        total_words = sum(article['word_count'] for article in self.articles)
        avg_words = total_words / total_articles if total_articles > 0 else 0

        # 统计有作者信息的文章数量
        articles_with_author = sum(1 for article in self.articles if article.get('author'))
        articles_with_summary = sum(1 for article in self.articles if article.get('summary'))

        print(f"\n=== NPR新闻爬取统计信息 ===")
        print(f"文章总数: {total_articles}")
        print(f"总词数: {total_words:,}")
        print(f"平均词数: {avg_words:.1f}")
        print(f"最短文章: {min(article['word_count'] for article in self.articles)} 词")
        print(f"最长文章: {max(article['word_count'] for article in self.articles)} 词")
        print(f"有作者信息: {articles_with_author} 篇 ({articles_with_author / total_articles * 100:.1f}%)")
        print(f"有摘要信息: {articles_with_summary} 篇 ({articles_with_summary / total_articles * 100:.1f}%)")


def main():
    """主函数"""
    crawler = NPRNewsCrawler()

    try:
        # 爬取100篇文章
        articles = crawler.crawl_articles(target_count=100)

        if articles:
            # 保存数据
            crawler.save_to_json()
            crawler.save_to_text_files()

            # 显示统计信息
            crawler.get_statistics()

            print("\n爬取任务完成！")
        else:
            print("没有成功爬取到任何文章")

    except KeyboardInterrupt:
        print("\n用户中断了爬取过程")
        if crawler.articles:
            print(f"已爬取 {len(crawler.articles)} 篇文章，正在保存...")
            crawler.save_to_json()
            crawler.save_to_text_files()
            crawler.get_statistics()
    except Exception as e:
        print(f"爬取过程中出现错误: {str(e)}")
        if crawler.articles:
            print(f"已爬取 {len(crawler.articles)} 篇文章，正在保存...")
            crawler.save_to_json()
            crawler.save_to_text_files()
            crawler.get_statistics()


if __name__ == "__main__":
    main()