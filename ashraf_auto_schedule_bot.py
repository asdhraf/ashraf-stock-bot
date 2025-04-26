import yfinance as yf
import requests
import datetime
import pytz
import csv
import time

BOT_TOKEN = '7698515759:AAGJzxXN4t5yPUZsHHr4nv4xSzqUM5E1FHs'
CHAT_ID = '@ashraf_1m_bot'
PRICE_LIMIT = 10.0

riyadh = pytz.timezone('Asia/Riyadh')

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    requests.post(url, data=payload)

def analyze_stock(symbol, now):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="7d", interval="1d")

        if hist.empty or len(hist) < 2:
            return None

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
            return message
    except Exception as e:
        return None

def run_analysis():
    with open("all_us_tickers.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        now = datetime.datetime.now(riyadh).strftime('%Y-%m-%d %H:%M:%S')
        for row in reader:
            symbol = row['Symbol']
            result = analyze_stock(symbol, now)
            if result:
                send_to_telegram(result)

def schedule_runner():
    while True:
        now = datetime.datetime.now(pytz.timezone('US/Eastern'))
        hour = now.hour
        minute = now.minute

        if (hour == 8 and minute == 0) or (hour == 10 and minute == 30) or (hour == 16 and minute == 5):
            run_analysis()
            time.sleep(60 * 60)

        time.sleep(30)

if __name__ == '__main__':
    schedule_runner()

