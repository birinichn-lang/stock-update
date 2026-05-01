import os
import yfinance as yf
import requests

def get_stock_data():
    # รายชื่อหุ้นที่คุณต้องการติดตาม
    tickers = {
        "S&P 500 Sharia (SPUS)": "SPUS",
        "Apple (AAPL)": "AAPL",
        "TSMC (TSM)": "TSM",
        "ASML (ASML)": "ASML",
        "Nvidia (NVDA)": "NVDA",
        "Alphabet (GOOGL)": "GOOGL",
        "Microsoft (MSFT)": "MSFT",
        "Tesla (TSLA)": "TSLA",
        "Water ETF (PHO)": "PHO"
    }
    
    header = "📊 [Market Update]\n"
    header += "---------------------------\n"
    body = ""
    
    for name, symbol in tickers.items():
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="5d")
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change = ((current_price - prev_price) / prev_price) * 100
                emoji = "📈" if change >= 0 else "📉"
                body += f"{emoji} {name}\n   Price: {current_price:.2f}\n   Chg: {change:+.2f}%\n\n"
            else:
                body += f"⚪ {name}: No Data\n\n"
        except:
            body += f"⚠️ {name}: Error\n\n"
    return header + body

def get_world_news():
    # ดึงข่าวธุรกิจโลกจาก NewsAPI
    api_key = os.environ.get('NEWS_API_KEY')
    url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={api_key}"
    
    header = "🌍 [World Business News]\n"
    header += "---------------------------\n"
    news_body = ""
    
    try:
        response = requests.get(url).json()
        articles = response.get('articles', [])[:5]  # เลือก 5 ข่าวเด่น
        for i, art in enumerate(articles, 1):
            title = art.get('title', 'No Title')
            news_body += f"{i}. {title}\n\n"
    except:
        news_body = "ไม่สามารถดึงข้อมูลข่าวได้ในขณะนี้"
        
    return header + news_body

def send_to_line(stock_text, news_text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['LINE_ACCESS_TOKEN']}"
    }
    # ส่ง 2 ข้อความแยกกันในคราวเดียว เพื่อความสวยงาม
    payload = {
        "to": os.environ["LINE_USER_ID"],
        "messages": [
            {"type": "text", "text": stock_text},
            {"type": "text", "text": news_text}
        ]
    }
    r = requests.post(url, headers=headers, json=payload)
    return r.status_code

if __name__ == "__main__":
    try:
        # ดึงข้อมูลทั้งสองส่วน
        stock_info = get_stock_data()
        news_info = get_world_news()
        
        # ส่งเข้า LINE
        status = send_to_line(stock_info, news_info)
        print(f"Update Sent! Status: {status}")
    except Exception as e:
        print(f"An error occurred: {e}")
