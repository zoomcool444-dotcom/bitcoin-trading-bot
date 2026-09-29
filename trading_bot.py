import time
import pandas as pd
import yfinance as yf
import urllib.request
import urllib.parse
import os

# Winsound safe import for cross-platform (Windows / Linux-Railway)
try:
    import winsound
except ImportError:
    winsound = None

# Telegram Configuration
TELEGRAM_TOKEN = '8711625179:AAENf-W7ddWXK8iz2TTgz_wF84okEfXGvS4'
TELEGRAM_CHAT_ID = '7865764285'

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        pass  # Network issue hone par bot crash nahi hoga

print("--- Professional Paper Trading Bot with PnL Tracker Started ---")
print("Bot live market monitor kar raha hai aur trades track kar raha hai.")
print("Band karne ke liye keyboard se 'Ctrl + C' dabayein.\n")

in_position = False
buy_price = 0.0
total_pnl_pct = 0.0

# Log file check karein ya banayein
log_file = "trade_history.csv"
if not os.path.exists(log_file):
    with open(log_file, "w") as f:
        f.write("Type,Price,PnL_Pct\n")

while True:
    try:
        df = yf.download('BTC-USD', period='5d', interval='1h', progress=False)

        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            df['SMA'] = df['Close'].rolling(window=3).mean()
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            current_price = df['Close'].iloc[-1]
            sma = df['SMA'].iloc[-1]
            rsi = df['RSI'].iloc[-1]
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] BTC: {current_price:.2f} | SMA: {sma:.2f} | RSI: {rsi:.1f} | Total PnL: {total_pnl_pct:+.2f}% | Status: {'IN POSITION' if in_position else 'WAITING'}")

            # 1. Buy Condition
            if current_price < sma and rsi < 40 and not in_position:
                buy_price = current_price
                in_position = True
                msg = f"🚨 [PAPER BUY]\nBTC Purchased at: {buy_price:.2f}\nRSI: {rsi:.1f}"
                print(f"--> {msg}")
                send_telegram_message(msg)
                if winsound:
                    winsound.Beep(1000, 500)
                
                with open(log_file, "a") as f:
                    f.write(f"BUY,{buy_price},0.0\n")
            
            # 2. Take Profit (3%)
            elif in_position and current_price >= (buy_price * 1.03):
                pnl = ((current_price - buy_price) / buy_price) * 100
                total_pnl_pct += pnl
                in_position = False
                msg = f"✅ [TAKE PROFIT HIT]\nSold at: {current_price:.2f}\nProfit: +{pnl:.2f}%\nTotal PnL: {total_pnl_pct:+.2f}%"
                print(f"--> {msg}")
                send_telegram_message(msg)
                if winsound:
                    winsound.Beep(1500, 800)
                
                with open(log_file, "a") as f:
                    f.write(f"SELL_PROFIT,{current_price},{pnl:.2f}\n")
            
            # 3. Stop Loss (2%)
            elif in_position and current_price <= (buy_price * 0.98):
                pnl = ((current_price - buy_price) / buy_price) * 100
                total_pnl_pct += pnl
                in_position = False
                msg = f"❌ [STOP LOSS HIT]\nSold at: {current_price:.2f}\nLoss: {pnl:.2f}%\nTotal PnL: {total_pnl_pct:+.2f}%"
                print(f"--> {msg}")
                send_telegram_message(msg)
                if winsound:
                    winsound.Beep(500, 1000)
                
                with open(log_file, "a") as f:
                    f.write(f"SELL_LOSS,{current_price},{pnl:.2f}\n")
        else:
            print("Data fetch nahi ho saka, agli koshish 1 minute baad...")

        time.sleep(60)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
