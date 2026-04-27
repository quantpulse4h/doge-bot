import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# --- AYARLAR ---
SYMBOL = "DOGEUSDT"
SENDER_EMAIL = "quantpulse4h@gmail.com"
PASSWORD = "gjkkwqwcbzdcxclm" 

def get_data():
    url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval=4h&limit=300"
    res = requests.get(url).json()
    df = pd.DataFrame(res, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qa', 't', 'tb', 'tq', 'i'])
    df['c'] = df['c'].astype(float)
    df['h'] = df['h'].astype(float)
    df['l'] = df['l'].astype(float)
    return df

def run_analysis():
    df = get_data()
    # EMA 200 hesaplama
    df['ema200'] = df['c'].ewm(span=200, adjust=False).mean()
    # RSI hesaplama
    delta = df['c'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    last = df.iloc[-1]
    price = last['c']
    ema = last['ema200']
    rsi = last['rsi']
    
    signal = "BEKLE"
    if price > ema and rsi < 65:
        signal = "LONG"
    elif price < ema and rsi > 35:
        signal = "SHORT"
    
    # Mail İçeriği
    ts = datetime.now().strftime('%d/%m/%Y %H:%M')
    subject = f"DOGE Raporu: {signal}"
    body = f"Zaman: {ts}\nFiyat: {price}\nSinyal: {signal}\nEMA200: {ema:.5f}\nRSI: {rsi:.2f}"
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = SENDER_EMAIL
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, PASSWORD)
            server.sendmail(SENDER_EMAIL, SENDER_EMAIL, msg.as_string())
        print("Mail basariyla gonderildi.")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    run_analysis()
