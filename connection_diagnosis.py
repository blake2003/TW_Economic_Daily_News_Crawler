#!/usr/bin/env python3
import socket
import subprocess
import requests
import time
import sys

def check_port_availability(port):
    """檢查端口是否可用"""
    print(f"檢查端口 {port} 是否可用...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', port))
        sock.close()
        print(f"✅ 端口 {port} 可用")
        return True
    except OSError:
        print(f"❌ 端口 {port} 已被占用")
        return False

def check_process_on_port(port):
    """檢查哪個進程在使用該端口"""
    print(f"\n檢查端口 {port} 的使用情況...")
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], 
                              capture_output=True, text=True)
        if result.stdout:
            print("端口使用情況:")
            print(result.stdout)
        else:
            print(f"沒有進程使用端口 {port}")
    except FileNotFoundError:
        print("lsof 命令不可用，無法檢查端口使用情況")

def test_socket_connection(port):
    """測試socket連接"""
    print(f"\n測試socket連接到 localhost:{port}...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    
    try:
        result = sock.connect_ex(('localhost', port))
        if result == 0:
            print(f"✅ Socket連接成功")
            sock.close()
            return True
        else:
            print(f"❌ Socket連接失敗，錯誤代碼: {result}")
            return False
    except Exception as e:
        print(f"❌ Socket連接異常: {e}")
        return False
    finally:
        sock.close()

def test_http_connection(port):
    """測試HTTP連接"""
    print(f"\n測試HTTP連接到 localhost:{port}...")
    
    try:
        response = requests.get(f'http://localhost:{port}/', timeout=10)
        print(f"✅ HTTP連接成功，狀態碼: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError as e:
        print(f"❌ HTTP連接失敗: {e}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ HTTP連接超時")
        return False
    except Exception as e:
        print(f"❌ HTTP連接異常: {e}")
        return False

def kill_process_on_port(port):
    """終止占用端口的進程"""
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        if result.stdout:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"正在終止進程 {pid}...")
                    subprocess.run(['kill', '-9', pid])
            print(f"✅ 已終止占用端口 {port} 的進程")
            return True
        else:
            print(f"沒有進程占用端口 {port}")
            return False
    except Exception as e:
        print(f"❌ 終止進程失敗: {e}")
        return False

def check_system_info():
    """檢查系統資訊"""
    print("\n=== 系統資訊 ===")
    try:
        # Python版本
        print(f"Python版本: {sys.version}")
        
        # 系統資訊
        result = subprocess.run(['uname', '-a'], capture_output=True, text=True)
        print(f"系統資訊: {result.stdout.strip()}")
        
        # 網路狀態
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        listening_ports = [line for line in result.stdout.split('\n') 
                          if 'LISTEN' in line and ('5000' in line)]
        if listening_ports:
            print("相關監聽端口:")
            for port in listening_ports:
                print(f"  {port}")
        
    except Exception as e:
        print(f"獲取系統資訊失敗: {e}")

def main():
    """主診斷函數"""
    print("=== Flask API 連接診斷工具 ===")
    print(f"診斷時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 檢查系統資訊
    check_system_info()
    
    # 要檢查的端口
    ports_to_check = [5000]
    
    for port in ports_to_check:
        print(f"\n{'='*50}")
        print(f"診斷端口 {port}")
        print(f"{'='*50}")
        
        # 1. 檢查端口使用情況
        check_process_on_port(port)
        
        # 2. 測試socket連接
        socket_ok = test_socket_connection(port)
        
        # 3. 測試HTTP連接
        if socket_ok:
            test_http_connection(port)
        
        # 4. 如果端口被占用，詢問是否終止
        if not check_port_availability(port):
            while True:
                choice = input(f"\n端口 {port} 被占用，是否終止占用的進程？(y/n/s=跳過): ").strip().lower()
                if choice in ['y', 'yes']:
                    kill_process_on_port(port)
                    time.sleep(2)  # 等待進程終止
                    check_port_availability(port)
                    break
                elif choice in ['n', 'no', 's', 'skip']:
                    break
                else:
                    print("請輸入 y, n, 或 s")
    
    print(f"\n{'='*50}")
    print("診斷建議:")
    print("1. 確保 Flask 服務器在正確的端口上運行")
    print("2. 檢查防火牆設置是否阻擋了連接")
    print("3. 嘗試使用 127.0.0.1 而不是 localhost")
    print("4. 如果使用虛擬環境，確保已正確激活")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()