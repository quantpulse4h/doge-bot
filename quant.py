import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import sys

# --- AYARLAR ---
SYMBOL = "DOGEUSDT"
SENDER_EMAIL = "quantpulse4h@gmail.com"
PASSWORD = "gjkkwqwcbzdcxclm" 

def get_data():
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval=4h&limit=300"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        df = pd.DataFrame(data, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qa', 't', 'tb', 'tq', 'i'])
        df['c'] = df['c'].astype(float)
        return df
    except Exception as e:
        print(f"Veri cekme hatasi: {e}")
        return None

def run_analysis():
    df = get_data()
    if df is None:
        sys.exit(1)
        
    # EMA 200 hesaplama
    df['ema200'] = df['c'].ewm(span=200, adjust=False).mean()
    
    last = df.iloc[-1]
    price = last['c']
    ema = last['ema200']
    
    signal = "LONG" if price > ema else "SHORT"
    
    # Mail Gönderimi
    ts = datetime.now().strftime('%d/%m/%Y %H:%M')
    subject = f"DOGE 4H Raporu: {signal}"
    body = f"Zaman: {ts}\nFiyat: {price}\nEMA200: {ema:.5f}\nSinyal: {signal}"
    
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
        print(f"Mail hatasi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_analysis()
