from flask import Flask, jsonify, render_template
from flask_cors import CORS

from crawler import scrape_news

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['GET'])
def scrape():
    news_data = scrape_news()
    return jsonify(news_data)

# 主程式入口
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)