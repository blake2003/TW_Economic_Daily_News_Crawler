import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_news():
    """改進的爬蟲函數，增加更好的錯誤處理和圖片抓取"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache',
    }
    
    base_url = 'https://udn.com/search/word/2/空汙'
    
    # 創建會話以重用連接
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        print("開始爬取聯合新聞網...")
        response = session.get(base_url, timeout=15)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"請求失敗，狀態碼: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # 找出所有<a>標籤，並篩選出符合條件的URL
        links = soup.find_all('a')
        story_urls = set()
        for link in links:
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                if full_url.startswith('https://udn.com/news/story/'):
                    story_urls.add(full_url)

        print(f"找到 {len(story_urls)} 個新聞連結")
        
        # 限制爬取數量
        story_urls = list(story_urls)[:10]
        news_data = []

        # 爬取每個新聞的內容
        for index, story_url in enumerate(story_urls, 1):
            try:
                print(f"正在爬取第 {index}/{len(story_urls)} 個新聞...")
                
                # 使用會話進行請求，增加重試機制
                for attempt in range(3):
                    try:
                        story_response = session.get(story_url, timeout=15)
                        story_response.encoding = 'utf-8'
                        break
                    except (requests.RequestException, OSError) as e:
                        if attempt == 2:
                            raise
                        print(f"請求重試 {attempt + 1}/3: {e}")
                        time.sleep(2)
                
                if story_response.status_code == 200:
                    story_soup = BeautifulSoup(story_response.text, 'html.parser')
                    
                    # 提取新聞資訊
                    title_tag = story_soup.select_one('h1.article-head__title, h1.story_art_title, h1')
                    title = title_tag.get_text(strip=True) if title_tag else '標題不明'
                    
                    time_tag = story_soup.find('time', class_='article-content__time')
                    if not time_tag:
                        time_tag = story_soup.find('div', class_='story_bady_info_author')
                    publish_time = time_tag.get_text(strip=True) if time_tag else '時間不明'
                    
                    reporter_tag = story_soup.find('span', class_='article-content__author')
                    if not reporter_tag:
                        reporter_tag = story_soup.find('span', class_='story_bady_info_author')
                    reporter = reporter_tag.get_text(strip=True) if reporter_tag else '記者不明'
                    
                    content_tag = story_soup.find('section', class_='article-content__editor')
                    if not content_tag:
                        content_tag = story_soup.find('div', class_='story_content')
                    
                    if content_tag:
                        paragraphs = content_tag.find_all('p')
                        content = '\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
                    else:
                        content = '內容不明'
                    
                    # 抓取圖片
                    images = extract_images(story_soup, story_url)
                    
                    # 只有當有實際內容時才添加到結果中
                    if title != '標題不明' and content != '內容不明':
                        news_item = {
                            'title': title,
                            'publish_time': publish_time,
                            'reporter': reporter,
                            'content': content,
                            'url': story_url,
                            'images': images  # 新增圖片字段
                        }
                        news_data.append(news_item)
                        print(f"成功爬取: {title[:50]}... (圖片: {len(images)}張)")
                else:
                    print(f"爬取失敗，狀態碼: {story_response.status_code}")
                    
                # 在請求之間添加延遲
                time.sleep(2)
                
            except Exception as e:
                print(f"爬取單個新聞時發生錯誤: {e}")
                continue
        
        print(f"爬取完成，共獲取 {len(news_data)} 條新聞")
        return news_data
        
    except requests.RequestException as e:
        print(f"網路請求錯誤: {e}")
        return []
    except Exception as e:
        print(f"爬取過程中發生未知錯誤: {e}")
        return []
    finally:
        session.close()

def extract_images(soup, story_url):
    """從新聞頁面提取圖片URL"""
    images = []
    
    # 尋找文章內容中的圖片
    content_section = soup.find('section', class_='article-content__editor')
    if not content_section:
        content_section = soup.find('div', class_='story_content')
    
    if content_section:
        # 尋找所有圖片標籤
        img_tags = content_section.find_all('img')
        
        for img in img_tags:
            # 獲取圖片URL
            img_url = img.get('src') or img.get('data-src') or img.get('data-original')
            
            if img_url:
                # 處理相對URL
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = urljoin('https://udn.com', img_url)
                elif not img_url.startswith('http'):
                    img_url = urljoin(story_url, img_url)
                
                # 過濾掉小圖片和廣告圖片
                if is_valid_news_image(img_url, img):
                    image_info = {
                        'url': img_url,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    }
                    images.append(image_info)
    
    # 也檢查文章頭部的主圖
    main_img = soup.find('div', class_='article-head__figure')
    if main_img:
        img_tag = main_img.find('img')
        if img_tag:
            img_url = img_tag.get('src') or img_tag.get('data-src')
            if img_url and is_valid_news_image(img_url, img_tag):
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = urljoin('https://udn.com', img_url)
                
                image_info = {
                    'url': img_url,
                    'alt': img_tag.get('alt', ''),
                    'title': img_tag.get('title', ''),
                    'is_main': True  # 標記為主圖
                }
                # 將主圖插入到列表開頭
                images.insert(0, image_info)
    
    return images

def is_valid_news_image(img_url, img_tag):
    """判斷是否為有效的新聞圖片"""
    # 排除小尺寸圖片
    width = img_tag.get('width')
    height = img_tag.get('height')
    
    if width and height:
        try:
            w, h = int(width), int(height)
            if w < 100 or h < 100:  # 排除太小的圖片
                return False
        except:
            pass
    
    # 排除廣告和社交媒體圖片
    exclude_keywords = [
        'ad', 'ads', 'advertisement', 'banner', 'logo', 
        'facebook', 'twitter', 'line', 'weibo',
        'pixel', 'tracking', 'beacon'
    ]
    
    img_url_lower = img_url.lower()
    for keyword in exclude_keywords:
        if keyword in img_url_lower:
            return False
    
    # 檢查圖片格式
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    if not any(ext in img_url_lower for ext in valid_extensions):
        return False
    
    return True

if __name__ == "__main__":
    # 測試爬蟲功能
    print("=== 爬蟲測試 ===")
    news = scrape_news()
    print(f"測試結果: 獲取到 {len(news)} 條新聞")
    
    if news:
        print("\n第一條新聞範例:")
        first_news = news[0]
        print(f"標題: {first_news['title']}")
        print(f"時間: {first_news['publish_time']}")
        print(f"記者: {first_news['reporter']}")
        print(f"內容摘要: {first_news['content'][:100]}...")
        print(f"圖片數量: {len(first_news.get('images', []))}")
        
        # 顯示圖片資訊
        images = first_news.get('images', [])
        if images:
            print("\n圖片資訊:")
            for i, img in enumerate(images[:3], 1):  # 只顯示前3張
                print(f"{i}. {img['url']}")
                if img.get('alt'):
                    print(f"   描述: {img['alt']}")
                if img.get('is_main'):
                    print(f"   (主圖)")