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
    # Binance bazen bağlantıyı reddedebilir, 3 kez deneme yapıyoruz
    for i in range(3):
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval=4h&limit=300"
            response = requests.get(url, timeout=20)
            res = response.json()
            
            if res and len(res) > 200:
                df = pd.DataFrame(res, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qa', 't', 'tb', 'tq', 'i'])
                df['c'] = df['c'].astype(float)
                
                # EMA 200
                df['ema200'] = df['c'].ewm(span=200, adjust=False).mean()
                last_row = df.iloc[-1]
                price = last_row['c']
                ema = last_row['ema200']
                
                signal = "LONG" if price > ema else "SHORT"
                
                # Mail Gönder
                ts = datetime.now().strftime('%d/%m/%Y %H:%M')
                subject = f"DOGE 4H Raporu: {signal}"
                body = f"Zaman: {ts}\nFiyat: {price}\nEMA200: {ema:.5f}\nSinyal: {signal}"
                
                msg = MIMEText(body)
                msg['Subject'] = subject
                msg['From'] = SENDER_EMAIL
                msg['To'] = SENDER_EMAIL
                
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(SENDER_EMAIL, PASSWORD)
                    server.sendmail(SENDER_EMAIL, SENDER_EMAIL, msg.as_string())
                
                print(f"Islem Basarili: {signal} maili gonderildi.")
                return # İşlem başarılı, döngüden çık
            
            print(f"Deneme {i+1}: Veri bos geldi, tekrar deneniyor...")
            time.sleep(5)
            
        except Exception as e:
            print(f"Hata: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
