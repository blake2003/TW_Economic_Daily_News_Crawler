#!/usr/bin/env python3
"""
圖片抓取測試腳本
測試crawler.py中的圖片抓取功能是否正常工作
"""

from crawler import scrape_news
import json

def test_image_extraction():
    """測試圖片抓取功能"""
    print("=== 圖片抓取測試 ===")
    print("開始測試圖片抓取功能...")
    
    try:
        # 調用爬蟲函數
        news_data = scrape_news()
        
        print(f"\n爬蟲執行完成！")
        print(f"獲取到 {len(news_data)} 條新聞")
        
        total_images = 0
        news_with_images = 0
        
        if news_data:
            print("\n=== 圖片抓取詳情 ===")
            for i, news in enumerate(news_data, 1):
                images = news.get('images', [])
                if images:
                    news_with_images += 1
                total_images += len(images)
                
                print(f"\n第 {i} 條新聞:")
                print(f"標題: {news['title'][:50]}...")
                print(f"圖片數量: {len(images)}")
                
                # 顯示圖片詳情
                for j, img in enumerate(images[:3], 1):  # 只顯示前3張
                    print(f"  圖片 {j}:")
                    print(f"    URL: {img['url']}")
                    if img.get('alt'):
                        print(f"    描述: {img['alt']}")
                    if img.get('is_main'):
                        print(f"    類型: 主圖")
                    print()
                
                if len(images) > 3:
                    print(f"  還有 {len(images) - 3} 張圖片...")
                
                print("-" * 60)
            
            # 統計資訊
            print(f"\n=== 統計資訊 ===")
            print(f"總新聞數: {len(news_data)}")
            print(f"有圖片的新聞: {news_with_images}")
            print(f"圖片覆蓋率: {news_with_images/len(news_data)*100:.1f}%")
            print(f"總圖片數: {total_images}")
            print(f"平均每篇新聞圖片數: {total_images/len(news_data):.1f}")
            
            # 測試JSON序列化
            print(f"\n=== JSON序列化測試 ===")
            try:
                json_data = json.dumps(news_data, ensure_ascii=False, indent=2)
                print("✅ JSON序列化成功")
                print(f"JSON大小: {len(json_data)} 字元")
            except Exception as e:
                print(f"❌ JSON序列化失敗: {e}")
            
            # 檢查圖片URL有效性
            print(f"\n=== 圖片URL檢查 ===")
            valid_urls = 0
            invalid_urls = 0
            
            for news in news_data:
                for img in news.get('images', []):
                    url = img['url']
                    if url.startswith('http') and any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                        valid_urls += 1
                    else:
                        invalid_urls += 1
                        print(f"⚠️  可能無效的URL: {url}")
            
            print(f"有效圖片URL: {valid_urls}")
            print(f"可能無效的URL: {invalid_urls}")
            print(f"URL有效率: {valid_urls/(valid_urls+invalid_urls)*100:.1f}%")
            
        else:
            print("未獲取到任何新聞資料")
            
    except Exception as e:
        print(f"圖片抓取測試失敗: {e}")
        import traceback
        traceback.print_exc()

def test_single_news_images():
    """測試單一新聞的圖片抓取詳情"""
    print("\n=== 單一新聞詳細測試 ===")
    
    try:
        news_data = scrape_news()
        if news_data and news_data[0].get('images'):
            first_news = news_data[0]
            images = first_news['images']
            
            print(f"新聞標題: {first_news['title']}")
            print(f"新聞URL: {first_news['url']}")
            print(f"圖片總數: {len(images)}")
            print()
            
            for i, img in enumerate(images, 1):
                print(f"圖片 {i}:")
                print(f"  URL: {img['url']}")
                print(f"  Alt文字: {img.get('alt', '無')}")
                print(f"  標題: {img.get('title', '無')}")
                print(f"  是否為主圖: {'是' if img.get('is_main') else '否'}")
                print()
        else:
            print("沒有找到包含圖片的新聞")
            
    except Exception as e:
        print(f"單一新聞測試失敗: {e}")

if __name__ == "__main__":
    test_image_extraction()
    test_single_news_images() 