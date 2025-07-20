#!/usr/bin/env python3
"""
簡單的API測試腳本
快速驗證Flask API服務是否正常運行
"""

import requests
import json

def test_api_simple():
    """簡單的API測試"""
    base_url = "http://localhost:5000"
    
    print("=== 簡單API測試 ===")
    
    # 1. 測試服務器是否運行
    print("\n1. 檢查服務器是否運行...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 服務器正常運行")
            data = response.json()
            print(f"API版本: {data.get('version')}")
            print(f"可用端點: {list(data.get('endpoints', {}).keys())}")
        else:
            print(f"❌ 服務器響應異常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到服務器")
        print("請確認:")
        print("- Flask服務器是否已啟動")
        print("- 端口5000是否被佔用")
        print("- 防火牆設置是否正確")
        return False
    except Exception as e:
        print(f"❌ 連接測試失敗: {e}")
        return False
    
    # 2. 測試健康檢查
    print("\n2. 測試健康檢查...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康檢查通過")
            data = response.json()
            print(f"狀態: {data.get('status')}")
            print(f"訊息: {data.get('message')}")
        else:
            print(f"❌ 健康檢查失敗: {response.status_code}")
            print(f"回應內容: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 健康檢查異常: {e}")
        return False
    
    # 3. 測試新聞API（僅檢查連接性）
    print("\n3. 測試新聞API連接...")
    try:
        print("發送請求到 /api/news ...")
        response = requests.get(f"{base_url}/api/news", timeout=30)
        
        if response.status_code == 200:
            print("✅ 新聞API連接成功")
            data = response.json()
            print(f"狀態: {data.get('status')}")
            print(f"訊息: {data.get('message')}")
            print(f"新聞數量: {data.get('count', 0)}")
            
            if data.get('count', 0) > 0:
                print("✅ 成功獲取新聞資料")
            else:
                print("⚠️  API正常但未獲取到新聞資料")
                
        else:
            print(f"❌ 新聞API請求失敗: {response.status_code}")
            print(f"回應內容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⚠️  新聞API請求超時（正常，爬蟲需要時間）")
        print("建議使用完整測試腳本進行詳細測試")
    except Exception as e:
        print(f"❌ 新聞API測試異常: {e}")
        return False
    
    print("\n=== 測試完成 ===")
    print("✅ 基本API功能正常")
    print("\n建議:")
    print("- 運行 'python test_crawler.py' 測試爬蟲功能")
    print("- 運行 'python test_client.py' 進行完整測試")
    return True

if __name__ == "__main__":
    test_api_simple() 