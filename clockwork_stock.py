import os
import yfinance as yf
from anthropic import Anthropic
import requests

def get_stock_data():
    # รายชื่อหุ้นที่คุณต้องการติดตาม
    # SPY (S&P 500), AAPL (Apple), TSM (TSMC), ASML, NVDA (Nvidia), 
    # GOOGL (Google), MSFT (Microsoft), TSLA (Tesla), PHO (Water Resources ETF)
    tickers = {
        "S&P 500 (SPY)": "SPY",
        "Apple (AAPL)": "AAPL",
        "TSMC (TSM)": "TSM",
        "ASML (ASML)": "ASML",
        "Nvidia (NVDA)": "NVDA",
        "Alphabet (GOOGL)": "GOOGL",
        "Microsoft (MSFT)": "MSFT",
        "Tesla (TSLA)": "TSLA",
        "Water ETF (PHO)": "PHO"
    }
    
    report = "ราคาปิดตลาดล่าสุด:\n"
    for name, symbol in tickers.items():
        try:
            stock = yf.Ticker(symbol)
            # ดึงข้อมูล 2 วันล่าสุดเพื่อดูการเปลี่ยนแปลง
            hist = stock.history(period="2d")
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change = ((current_price - prev_price) / prev_price) * 100
                report += f"- {name}: {current_price:.2f} ({change:+.2f}%)\n"
            else:
                # กรณีวันหยุดหรือข้อมูลไม่ครบ
                current_price = hist['Close'].iloc[-1] if not hist.empty else 0
                report += f"- {name}: {current_price:.2f} (N/A)\n"
        except Exception as e:
            report += f"- {name}: Error fetching data\n"
            
    return report

def ask_claude_to_summarize(raw_info):
    client = Anthropic(api_key=os.environ["CLAUDE_API_KEY"])
    
    # ปรับ Prompt ให้เน้นการวิเคราะห์กลุ่ม Tech/Semi และการ DCA
    prompt = f"""
    นี่คือข้อมูลราคาหุ้นรายวัน:
    {raw_info}
    
    ในฐานะผู้เชี่ยวชาญด้านการลงทุน ช่วยสรุปข้อมูลนี้เป็นภาษาไทย:
    1. ภาพรวมของหุ้นกลุ่ม Big Tech และ Semiconductor (NVDA, TSM, ASML) ว่าวันนี้เป็นอย่างไร
    2. วิเคราะห์สั้นๆ ว่ากระทบต่อแผนการ DCA ระยะยาวอย่างไร (เช่น เป็นจังหวะเก็บเพิ่ม หรือควรระวัง)
    3. เชื่อมโยงกับภาวะเงินเฟ้อหรือปัจจัยเศรษฐกิจมหภาคที่น่าสนใจ (ถ้ามี)
    
    ข้อกำหนด: 
    - สรุปให้กระชับสำหรับอ่านใน LINE (ไม่เกิน 12-15 บรรทัด)
    - ใช้ภาษาที่เป็นกันเองแต่ดูเป็นมืออาชีพ
    - เน้นสาระสำคัญที่นักลงทุนต้องรู้ก่อนเริ่มงาน
    """
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

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
        raw_data = get_stock_data()
        final_summary = ask_claude_to_summarize(raw_data)
        status = send_to_line(final_summary)
        print(f"Daily Update Sent! Status: {status}")
    except Exception as e:
        print(f"An error occurred: {e}")
