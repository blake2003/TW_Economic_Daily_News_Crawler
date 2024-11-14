import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_news():
    base_url = 'https://money.udn.com/money/index'
    response = requests.get(base_url)
    response.encoding = 'utf-8'

    # 檢查請求是否成功
    if response.status_code == 200:
        # 解析HTML內容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找出所有<a>標籤，並篩選出符合條件的URL
        links = soup.find_all('a')
        story_urls = set()
        for link in links:
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                if full_url.startswith('https://money.udn.com/money/story'):
                    story_urls.add(full_url)

        # 初始化，用於儲存新聞資訊
        news_data = []

        # 爬取每個新聞的內容
        for story_url in story_urls:
            story_response = requests.get(story_url)
            story_response.encoding = 'utf-8'
            if story_response.status_code == 200:
                story_soup = BeautifulSoup(story_response.text, 'html.parser')
                
                # 爬取標題
                title_tag = story_soup.find('h1', class_='article-head__title')
                title = title_tag.get_text(strip=True) if title_tag else 'N/A'
                
                # 爬取發布時間
                time_tag = story_soup.find('time', class_='article-body__time')
                publish_time = time_tag.get_text(strip=True) if time_tag else 'N/A'
                
                # 爬取報導者
                reporter_tag = story_soup.find('div', class_='article-body__info')
                reporter = reporter_tag.get_text(strip=True) if reporter_tag else 'N/A'
                
                # 爬取內文
                content_tag = story_soup.find('section', class_='article-body__editor')
                paragraphs = content_tag.find_all('p') if content_tag else []
                content = '\n'.join(p.get_text(strip=True) for p in paragraphs)
                
                # 將爬取到的內容存入字典
                news_item = {
                    'title': title,
                    'publish_time': publish_time,
                    'reporter': reporter,
                    'content': content
                }
                news_data.append(news_item)
        return news_data
    else:
        return []
