import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import time

# 分类模块 URL
section_urls = [
    "https://www.npr.org/sections/national",
    "https://www.npr.org/sections/world",
    "https://www.npr.org/sections/politics",
    "https://www.npr.org/sections/business",
    "https://www.npr.org/sections/health",
    "https://www.npr.org/sections/science",
    "https://www.npr.org/sections/climate",
    "https://www.npr.org/sections/codeswitch"
]

# 保存目录
if not os.path.exists('npr_articles'):
    os.makedirs('npr_articles')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0"
}

seen_titles = set()
articles = []
article_count = 0
max_articles = 100  # 总爬取数量限制


def parse_article(article_url):
    try:
        resp = requests.get(article_url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')

        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else '无标题'
        if title in seen_titles:
            print(f"标题重复，跳过重复文章：{title}")
            return None
        seen_titles.add(title)

        content_div = soup.find('div', id='storytext')
        if content_div:
            paragraphs = content_div.find_all('p')
            content = '\n'.join(p.get_text(strip=True) for p in paragraphs)
        else:
            content = '无内容'

        summary_tag = soup.find('div', class_='teaser')
        summary = summary_tag.get_text(strip=True) if summary_tag else content[:150]

        author_tag = soup.select_one('p.byline__name--block a')
        author = author_tag.get_text(strip=True) if author_tag else None

        time_tag = soup.find('time')
        publish_time = time_tag['datetime'][:10] if time_tag and 'datetime' in time_tag.attrs else None

        word_count = len(content.split())
        crawl_time = datetime.utcnow().isoformat()

        return {
            "url": article_url,
            "title": title,
            "content": content,
            "summary": summary,
            "author": author,
            "publish_time": publish_time,
            "word_count": word_count,
            "crawl_time": crawl_time
        }

    except Exception as e:
        print(f"解析失败：{article_url}, 错误：{e}")
        return None


for section_url in section_urls:
    print(f"访问：{section_url}")
    try:
        resp = requests.get(section_url, headers=headers, timeout=10)
    except Exception as e:
        print(f"请求失败：{section_url}，错误：{e}")
        continue  # 跳到下一个section_url

    if resp.status_code != 200:
        print(f"页面失败：{section_url}")
        continue

    soup = BeautifulSoup(resp.text, 'html.parser')
    links = soup.select("h2.title a")
    if not links:
        print(f"没有文章链接：{section_url}")
        continue

    for link in links:
        if article_count >= max_articles:
            break
        article_data = parse_article(link['href'])
        if article_data:
            articles.append(article_data)
            article_count += 1

            # 保存为 TXT
            txt_path = os.path.join("npr_articles", f"article_{article_count}.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(article_data['content'])

            print(f"✅ 保存第 {article_count} 篇：{article_data['title']}")
            time.sleep(1)

    if article_count >= max_articles:
        break  # 达到最大文章数，跳出循环
    time.sleep(2)


# 保存为 JSON 文件
json_path = os.path.join("npr_articles", "all_articles.json")
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=4)

print(f"\n🎉 共保存 {article_count} 篇文章到 JSON：{json_path}")
