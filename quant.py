import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import time

# --- AYARLAR ---
SYMBOL = "DOGEUSDT"
SENDER_EMAIL = "quantpulse4h@gmail.com"
PASSWORD = "gjkkwqwcbzdcxclm" 

def run_bot():
    try:
        # 1. Veri Çekme (Hata kontrolü eklendi)
        url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval=4h&limit=300"
        response = requests.get(url, timeout=15)
        res = response.json()
        
        if not res or len(res) < 200:
            print("Veri henüz hazır değil veya boş geldi. Bekleniyor...")
            return

        df = pd.DataFrame(res, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qa', 't', 'tb', 'tq', 'i'])
        df['c'] = df['c'].astype(float)
        
        # 2. Teknik Analiz (EMA 200)
        df['ema200'] = df['c'].ewm(span=200, adjust=False).mean()
        
        # Son satırı kontrol ederek çek
        last_row = df.iloc[-1]
        last_price = last_row['c']
        ema_value = last_row['ema200']
        
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
        print(f"Islem basarili: {signal}")

    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    run_bot()
