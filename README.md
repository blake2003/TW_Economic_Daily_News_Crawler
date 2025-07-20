# 聯合新聞網爬蟲 API 服務

這是一個用於爬取聯合新聞網新聞資料並提供 REST API 的 Flask 應用程式。

## 功能特色

- 自動爬取聯合新聞網最新新聞
- 提供 RESTful API 端點
- 支援跨域請求（CORS）
- 返回 JSON 格式的新聞資料

## 安裝與設置

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 運行服務

```bash
python app.py
```

服務將在 `http://localhost:5000` 啟動

## API 端點

### 獲取新聞列表
- **URL**: `/api/news`
- **方法**: GET
- **響應格式**: JSON

#### 響應示例
```json
[
  {
    "title": "新聞標題",
    "publish_time": "2024-01-XX XX:XX:XX",
    "reporter": "記者姓名",
    "content": "新聞內容..."
  }
]
```

### 健康檢查
- **URL**: `/health`
- **方法**: GET
- **響應**: `{"status": "healthy"}`

## 與 Flutter 應用整合

確保在 Flutter 的 `NewsService` 中設置正確的 API 地址：

```dart
static const String _baseUrl = 'http://YOUR_IP:5000';
```

## 注意事項

1. 請遵守聯合新聞網的 robots.txt 和使用條款
2. 建議添加適當的請求間隔以避免對伺服器造成負擔
3. 生產環境中應配置適當的錯誤處理和日誌記錄

## 開發說明

- `crawler.py`: 新聞爬蟲核心邏輯
- `app.py`: Flask API 服務器
- `requirements.txt`: Python 依賴列表