import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import time

# 创建保存文章的目录
if not os.path.exists('npr_articles'):
    os.makedirs('npr_articles')

# 设置请求头，模拟浏览器访问
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
}


# 初始化变量
base_url = 'https://www.npr.org/sections/news/archive'
article_count = 0
max_articles = 100
page = 1
articles = []

# 循环爬取文章，直到达到指定数量
while article_count < max_articles:
    print(f'正在爬取第 {page} 页...')
    url = f'{base_url}?page={page}'
    response = requests.get(url, headers=headers, proxies={"http": None, "https": None}, timeout=10)
    if response.status_code != 200:
        print(f'无法访问页面：{url}')
        break

    soup = BeautifulSoup(response.text, 'html.parser')
    # 查找当前页面中的所有文章链接
    article_links = soup.select('h2.title a')
    if not article_links:
        print('未找到更多文章链接。')
        break

    for link in article_links:
        if article_count >= max_articles:
            break
        article_url = link['href']
        try:
            article_resp = requests.get(article_url, headers=headers)
            if article_resp.status_code != 200:
                print(f'无法访问文章：{article_url}')
                continue
            article_soup = BeautifulSoup(article_resp.text, 'html.parser')

            # 提取文章标题
            title_tag = article_soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else '无标题'

            # 提取文章内容（正文）
            content_div = article_soup.find('div', id='storytext')
            if content_div:
                paragraphs = content_div.find_all('p')
                content = '\n'.join(p.get_text(strip=True) for p in paragraphs)
            else:
                content = '无内容'

            # 提取文章摘要（如果有）
            summary_tag = article_soup.find('div', class_='teaser')
            summary = summary_tag.get_text(strip=True) if summary_tag else content[:150]

            # 提取作者
            author_tag = article_soup.select_one('p.byline__name--block a')
            author = author_tag.get_text(strip=True) if author_tag else None

            # 提取发布日期
            time_tag = article_soup.find('time')
            publish_time = time_tag['datetime'][:10] if time_tag and 'datetime' in time_tag.attrs else None

            # 计算词数
            word_count = len(content.split())

            # 获取当前爬取时间
            crawl_time = datetime.utcnow().isoformat()

            # 构建文章数据字典
            article_data = {
                "url": article_url,
                "title": title,
                "content": content,
                "summary": summary,
                "author": author,
                "publish_time": publish_time,
                "word_count": word_count,
                "crawl_time": crawl_time
            }

            articles.append(article_data)

            # 保存为 TXT（可选）
            txt_filename = os.path.join('npr_articles', f'article_{article_count + 1}.txt')
            with open(txt_filename, 'w', encoding='utf-8') as txt_file:
                txt_file.write(content)

            print(f'已保存文章 {article_count + 1}: {title}')
            article_count += 1
            time.sleep(1)

        except Exception as e:
            print(f'处理文章出错：{article_url} 错误信息：{e}')
            continue

        page += 1
        time.sleep(2)

# 所有文章保存到一个 JSON 文件
json_path = os.path.join('npr_articles', 'all_articles.json')
with open(json_path, 'w', encoding='utf-8') as json_file:
    json.dump(articles, json_file, ensure_ascii=False, indent=4)

print(f'\n✅ 共爬取并保存了 {article_count} 篇文章。所有 JSON 已写入 {json_path}')