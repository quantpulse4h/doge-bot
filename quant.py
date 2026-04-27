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

def send_mail(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = SENDER_EMAIL
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, PASSWORD)
            server.sendmail(SENDER_EMAIL, SENDER_EMAIL, msg.as_string())
        print("Mail gonderildi.")
    except Exception as e:
        print(f"Mail hatasi: {e}")

def run_bot():
    ts = datetime.now().strftime('%d/%m/%Y %H:%M')
    for i in range(3):
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval=4h&limit=300"
            res = requests.get(url, timeout=20).json()
            
            if res and len(res) > 200:
                df = pd.DataFrame(res, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qa', 't', 'tb', 'tq', 'i'])
                df['c'] = df['c'].astype(float)
                df['ema200'] = df['c'].ewm(span=200, adjust=False).mean()
                
                last_price = df.iloc[-1]['c']
                ema = df.iloc[-1]['ema200']
                signal = "LONG" if last_price > ema else "SHORT"
                
                body = f"Zaman: {ts}\nFiyat: {last_price}\nEMA200: {ema:.5f}\nSinyal: {signal}"
                send_mail(f"🚀 DOGE 4H Raporu: {signal}", body)
                return
            
            time.sleep(5)
        except Exception as e:
            print(f"Hata: {e}")
            time.sleep(5)
    
    # 3 deneme de başarısız olursa "Hata" maili atar
    send_mail("⚠️ DOGE Bot: Veri Alınamadı", f"{ts} tarihindeki taramada Binance verisi bos geldi.")

if __name__ == "__main__":
    run_bot()
