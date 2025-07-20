import requests
import json
import time

def test_api():
    """測試API端點"""
    base_url = "http://localhost:5000"
    
    print("=== API 測試開始 ===")
    
    # 測試健康檢查
    print("\n1. 測試健康檢查...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
    except Exception as e:
        print(f"健康檢查失敗: {e}")
        return
    
    # 測試根路徑
    print("\n2. 測試根路徑...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"狀態碼: {response.status_code}")
        print(f"回應: {response.json()}")
    except Exception as e:
        print(f"根路徑測試失敗: {e}")
    
    # 測試新聞API
    print("\n3. 測試新聞API...")
    try:
        print("發送請求到 /api/news...")
        start_time = time.time()
        
        response = requests.get(f"{base_url}/api/news", timeout=60)  # 增加超時時間
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"狀態碼: {response.status_code}")
        print(f"請求耗時: {duration:.2f} 秒")
        
        if response.status_code == 200:
            data = response.json()
            print(f"獲取狀態: {data.get('status')}")
            print(f"新聞數量: {data.get('count', 0)}")
            
            # 顯示前3條新聞標題
            if data.get('data'):
                print("\n前3條新聞標題:")
                for i, news in enumerate(data['data'][:3], 1):
                    print(f"{i}. {news.get('title', '無標題')}")
        else:
            print(f"請求失敗: {response.text}")
            
    except requests.exceptions.Timeout:
        print("請求超時！請檢查服務器是否正常運行")
    except requests.exceptions.ConnectionError:
        print("連接錯誤！請確認服務器已啟動並監聽5000端口")
    except Exception as e:
        print(f"新聞API測試失敗: {e}")
    
    print("\n=== API 測試結束 ===")

def stress_test():
    """壓力測試 - 多次調用API"""
    base_url = "http://localhost:5000"
    test_count = 5
    
    print(f"\n=== 壓力測試開始 ({test_count} 次請求) ===")
    
    success_count = 0
    total_time = 0
    
    for i in range(test_count):
        try:
            print(f"\n第 {i+1}/{test_count} 次請求...")
            start_time = time.time()
            
            response = requests.get(f"{base_url}/api/health", timeout=10)
            
            end_time = time.time()
            duration = end_time - start_time
            total_time += duration
            
            if response.status_code == 200:
                success_count += 1
                print(f"✅ 成功 - 耗時: {duration:.2f}秒")
            else:
                print(f"❌ 失敗 - 狀態碼: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 異常: {e}")
        
        # 請求間隔
        time.sleep(1)
    
    success_rate = (success_count / test_count) * 100
    avg_time = total_time / test_count if test_count > 0 else 0
    
    print(f"\n=== 壓力測試結果 ===")
    print(f"總請求數: {test_count}")
    print(f"成功數: {success_count}")
    print(f"成功率: {success_rate:.1f}%")
    print(f"平均響應時間: {avg_time:.2f}秒")

if __name__ == "__main__":
    # 基本功能測試
    test_api()
    
    # 詢問是否進行壓力測試
    while True:
        choice = input("\n是否進行壓力測試？(y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            stress_test()
            break
        elif choice in ['n', 'no']:
            print("測試完成！")
            break
        else:
            print("請輸入 y 或 n")