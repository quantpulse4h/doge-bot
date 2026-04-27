import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# --- AYARLAR ---
SYMBOL = "DOGEUSDT"
SENDER_EMAIL = "quantpulse4h@gmail.com"
PASSWORD = "gjkkwqwcbzdcxclm" 

def run_bot():
    # 1. Veri Çekme
    url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval=4h&limit=250"
    res = requests.get(url).json()
    df = pd.DataFrame(res, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qa', 't', 'tb', 'tq', 'i'])
    df['c'] = df['c'].astype(float)
    
    # 2. Teknik Analiz (EMA 200)
    df['ema200'] = df['c'].ewm(span=200, adjust=False).mean()
    last_price = df.iloc[-1]['c']
    ema_value = df.iloc[-1]['ema200']
    
    signal = "LONG" if last_price > ema_value else "SHORT"
    
    # 3. Mail Hazırlığı
    ts = datetime.now().strftime('%d/%m/%Y %H:%M')
    subject = f"DOGE 4H Sinyali: {signal}"
    body = f"Zaman: {ts}\nFiyat: {last_price}\nEMA200: {ema_value:.5f}\nSinyal: {signal}"
    
    # 4. Mail Gönderme
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = SENDER_EMAIL
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, SENDER_EMAIL, msg.as_string())
    print("Islem basarili.")

if __name__ == "__main__":
    run_bot()
