import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import time
import random

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

def get_binance_data():
    base_urls = [
        "https://api.binance.com",
        "https://api1.binance.com",
        "https://api2.binance.com",
        "https://api3.binance.com"
    ]
    
    # Kendimizi gerçek bir tarayıcı gibi tanıtıyoruz (User-Agent)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    random.shuffle(base_urls) # Sunucuları her seferinde farklı sırada dene
    
    for base in base_urls:
        try:
            # Rastgele kısa bir bekleme ekleyerek Binance radarına takılma ihtimalini düşür
            time.sleep(random.uniform(1, 3))
            
            url = f"{base}/api/v3/klines?symbol={SYMBOL}&interval=4h&limit=250"
            response = requests.get(url, headers=headers, timeout=20)
            res = response.json()
            
            if isinstance(res, list) and len(res) > 100:
                return res
        except:
            continue
    return None

def run_bot():
    ts = datetime.now().strftime('%d/%m/%Y %H:%M')
    data = get_binance_data()
    
    if data:
        df = pd.DataFrame(data, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qa', 't', 'tb', 'tq', 'i'])
        df['c'] = df['c'].astype(float)
        
        # EMA 200 Analizi
        df['ema200'] = df['c'].ewm(span=200, adjust=False).mean()
        last_price = df.iloc[-1]['c']
        ema = df.iloc[-1]['ema200']
        
        signal = "LONG" if last_price > ema else "SHORT"
        
        body = f"Zaman: {ts}\nFiyat: {last_price}\nEMA200: {ema:.5f}\nSinyal: {signal}"
        send_mail(f"🚀 DOGE 4H Raporu: {signal}", body)
    else:
        # Eğer hala veri gelmiyorsa, boş mail atarak seni haberdar eder
        send_mail("⚠️ DOGE Bot: Baglanti Hatasi", f"{ts} tarihinde tum sunucular reddedildi.")

if __name__ == "__main__":
    run_bot()
