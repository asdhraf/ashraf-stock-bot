import yfinance as yf
import requests
import datetime
import pytz
import csv
import time
import threading
from flask import Flask
import os

# إعدادات البوت
BOT_TOKEN = '7698515759:AAGJzxXN4t5yPUzSHHr4nv4xSzqUM5E1FHs'
CHAT_ID = '@ashraf_1m_bot'
PRICE_LIMIT = 10.0

# توقيت الرياض
riyadh = pytz.timezone('Asia/Riyadh')

# سيرفر وهمي لتجاوز متطلبات Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Ashraf Bot is running!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# إرسال الرسائل للتيليجرام
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"خطأ أثناء الإرسال: {e}")

# تحليل الأسهم
def analyze_stock(symbol, now):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="7d", interval="1d")

        if hist.empty or len(hist) < 2:
            return

        last_close = hist['Close'][-1]
        prev_high = hist['High'][:-1].max()
        volume = hist['Volume'][-1]

        if last_close < PRICE_LIMIT and last_close > prev_high and volume > 500000:
            stop_loss = round(last_close * 0.93, 2)
            target1 = round(last_close * 1.07, 2)
            target2 = round(last_close * 1.15, 2)
            message = f"""📈 <b>فرصة ممتازة: {symbol}</b>
⏰ وقت الدخول: {now}
💵 سعر الدخول: {last_close:.2f}
🛑 وقف الخسارة: {stop_loss}
🎯 الهدف الأول: {target1}
🎯 الهدف الثاني: {target2}
📌 القرار: دخول"""
            send_to_telegram(message)
    except Exception as e:
        print(f"خطأ أثناء تحليل السهم {symbol}: {e}")

# الحلقة الرئيسية
def main():
    while True:
        try:
            with open("all_us_tickers.csv", newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                now = datetime.datetime.now(riyadh).strftime('%Y-%m-%d %H:%M:%S')
                for row in reader:
                    symbol = row['Symbol']
                    analyze_stock(symbol, now)
        except Exception as e:
            print(f"خطأ عام: {e}")

        # انتظار 30 ثانية قبل الفحص التالي
        time.sleep(30)

# تشغيل السكربت
if __name__ == "__main__":
    threading.Thread(target=run_web_server).start()
    main()
