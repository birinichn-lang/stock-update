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
    
    header = "📊 รายงานหุ้นประจำวัน (DCA Plan)\n"
    header += "---------------------------\n"
    body = ""
    
    for name, symbol in tickers.items():
        try:
            stock = yf.Ticker(symbol)
            # ดึงข้อมูล 5 วันล่าสุดเพื่อให้ครอบคลุมช่วงวันหยุด
            hist = stock.history(period="5d")
            
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change = ((current_price - prev_price) / prev_price) * 100
                
                # ใส่ Emoji ตามสถานะราคา
                emoji = "📈" if change >= 0 else "📉"
                body += f"{emoji} {name}\n   Price: {current_price:.2f}\n   Chg: {change:+.2f}%\n\n"
            else:
                body += f"⚪ {name}: ข้อมูลไม่เพียงพอ\n\n"
        except Exception as e:
            body += f"⚠️ {name}: Error fetching data\n\n"
            
    footer = "---------------------------\n"
    footer += "ขอให้เป็นวันที่ดีสำหรับการลงทุนครับ! 🚀"
    
    return header + body + footer

def send_to_line(message_text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['LINE_ACCESS_TOKEN']}"
    }
    payload = {
        "to": os.environ["LINE_USER_ID"],
        "messages": [{"type": "text", "text": message_text}]
    }
    r = requests.post(url, headers=headers, json=payload)
    return r.status_code

if __name__ == "__main__":
    try:
        # ดึงข้อมูลและส่งเข้า LINE โดยตรง ไม่ผ่าน AI
        final_message = get_stock_data()
        status = send_to_line(final_message)
        print(f"Daily Update Sent! Status: {status}")
    except Exception as e:
        print(f"An error occurred: {e}")
