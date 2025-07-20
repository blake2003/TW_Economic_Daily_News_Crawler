#!/usr/bin/env python3
"""
爬蟲功能測試腳本
測試crawler.py中的scrape_news函數是否正常工作
"""

from crawler import scrape_news
import json

def test_crawler():
    """測試爬蟲功能"""
    print("=== 爬蟲功能測試 ===")
    print("開始測試crawler.py中的scrape_news函數...")
    
    try:
        # 調用爬蟲函數
        news_data = scrape_news()
        
        # 檢查結果
        print(f"\n爬蟲執行完成！")
        print(f"獲取到 {len(news_data)} 條新聞")
        
        if news_data:
            print("\n=== 新聞資料範例 ===")
            for i, news in enumerate(news_data[:3], 1):  # 只顯示前3條
                print(f"\n第 {i} 條新聞:")
                print(f"標題: {news.get('title', '無標題')}")
                print(f"時間: {news.get('publish_time', '無時間')}")
                print(f"記者: {news.get('reporter', '無記者')}")
                print(f"內容摘要: {news.get('content', '無內容')[:100]}...")
                if 'url' in news:
                    print(f"網址: {news['url']}")
                print("-" * 50)
            
            # 檢查資料完整性
            print("\n=== 資料完整性檢查 ===")
            complete_news = 0
            for news in news_data:
                if (news.get('title') and news.get('title') != '標題不明' and
                    news.get('content') and news.get('content') != '內容不明'):
                    complete_news += 1
            
            print(f"完整新聞數量: {complete_news}/{len(news_data)}")
            print(f"完整度: {complete_news/len(news_data)*100:.1f}%")
            
        else:
            print("未獲取到任何新聞資料")
            print("可能的原因:")
            print("1. 網路連接問題")
            print("2. 網站結構變更")
            print("3. 被網站阻擋")
            
    except Exception as e:
        print(f"爬蟲測試失敗: {e}")
        print("請檢查:")
        print("1. 網路連接是否正常")
        print("2. crawler.py是否存在語法錯誤")
        print("3. 依賴套件是否正確安裝")

if __name__ == "__main__":
    test_crawler()