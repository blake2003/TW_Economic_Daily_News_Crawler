from flask import Flask, jsonify, request
from flask_cors import CORS
from crawler import scrape_news
import socket
import time
import logging

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

socket.setdefaulttimeout(30)

# 增加錯誤處理和連接管理
from werkzeug.serving import WSGIRequestHandler

class CustomRequestHandler(WSGIRequestHandler):
    def handle(self):
        try:
            super().handle()
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            if hasattr(e, 'errno') and e.errno == 57:  # Socket is not connected
                logger.warning(f"客戶端提前斷開連接: {self.client_address}")
            elif hasattr(e, 'errno') and e.errno == 32:  # Broken pipe
                logger.warning(f"管道破裂錯誤: {self.client_address}")
            else:
                logger.error(f"連接錯誤: {e} - 客戶端: {self.client_address}")
        except Exception as e:
            logger.error(f"處理請求時發生未知錯誤: {e}")

app = Flask(__name__)
CORS(app)  # 允許跨域請求，讓Flutter可以調用

def ensure_images_field(news_item):
    """確保新聞項目包含images字段，提供向後兼容性"""
    if 'images' not in news_item:
        news_item['images'] = []
    elif news_item['images'] is None:
        news_item['images'] = []
    elif not isinstance(news_item['images'], list):
        news_item['images'] = []
    
    # 驗證每個圖片物件的格式
    valid_images = []
    for img in news_item['images']:
        if isinstance(img, dict) and 'url' in img and img['url']:
            # 確保每個圖片物件都有必要的字段
            validated_img = {
                'url': str(img.get('url', '')),
                'alt': str(img.get('alt', '')),
                'title': str(img.get('title', '')),
                'is_main': bool(img.get('is_main', False))
            }
            valid_images.append(validated_img)
    
    news_item['images'] = valid_images
    return news_item

@app.route('/api/news', methods=['GET'])
def get_news():
    """獲取新聞資料的API端點"""
    try:
        logger.info("收到新聞爬取請求")
        
        # 執行爬蟲
        news_data = scrape_news()
        
        # 確保每條新聞都有images字段
        processed_news = []
        for news_item in news_data:
            try:
                processed_item = ensure_images_field(news_item.copy())
                processed_news.append(processed_item)
            except Exception as e:
                logger.error(f"處理新聞項目時發生錯誤: {e}")
                # 為有問題的新聞項目添加空的images字段
                news_item['images'] = []
                processed_news.append(news_item)
        
        if not processed_news:
            logger.warning("未獲取到任何新聞資料")
            return jsonify({
                'status': 'warning',
                'message': '未獲取到新聞資料',
                'data': [],
                'count': 0
            }), 200
        
        # 統計圖片資訊
        total_images = sum(len(item.get('images', [])) for item in processed_news)
        news_with_images = sum(1 for item in processed_news if item.get('images'))
        
        response_data = {
            'status': 'success',
            'message': f'成功獲取 {len(processed_news)} 條新聞',
            'data': processed_news,
            'count': len(processed_news),
            'timestamp': time.time(),
            'stats': {
                'total_images': total_images,
                'news_with_images': news_with_images,
                'image_coverage': round(news_with_images / len(processed_news) * 100, 1) if processed_news else 0
            }
        }
        
        logger.info(f"成功返回 {len(processed_news)} 條新聞資料，包含 {total_images} 張圖片")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"API處理過程中發生錯誤: {e}")
        return jsonify({
            'status': 'error',
            'message': '服務器內部錯誤',
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'message': 'API服務正常運行',
        'timestamp': time.time()
    }), 200

@app.route('/', methods=['GET'])
def index():
    """根路徑"""
    return jsonify({
        'message': 'TW Economic Daily News Crawler API',
        'version': '1.1',
        'features': ['新聞抓取', '圖片抓取', '向後兼容'],
        'endpoints': {
            '/api/news': 'GET - 獲取空汙相關新聞',
            '/api/health': 'GET - 健康檢查'
        }
    })

if __name__ == '__main__':
    logger.info("啟動新聞API服務器...")
    logger.info("API端點: http://localhost:5000/api/news")
    logger.info("健康檢查: http://localhost:5000/api/health")
    
    try:
        app.run(
            host='0.0.0.0', 
            port=5000, 
            request_handler=CustomRequestHandler, 
            threaded=True, 
            use_reloader=False,
            debug=False
        )
    except KeyboardInterrupt:
        logger.info("服務器已停止")
    except Exception as e:
        logger.error(f"服務器啟動失敗: {e}")