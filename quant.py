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

def get_binance_data():
    # Binance'in 3 farklı bağlantı adresini sırayla deniyoruz
    base_urls = [
        "https://api.binance.com",
        "https://api1.binance.com",
        "https://api3.binance.com"
    ]
    
    for base in base_urls:
        try:
            # İstek miktarını 250'ye düşürdük (daha hızlı ve güvenli)
            url = f"{base}/api/v3/klines?symbol={SYMBOL}&interval=4h&limit=250"
            res = requests.get(url, timeout=15).json()
            if res and len(res) > 100:
                return res
        except:
            continue # Bu sunucu hata verirse diğerine geç
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
        print(f"Analiz tamamlandi: {signal}")
    else:
        # Tüm sunucular başarısız olursa mail atar
        send_mail("⚠️ DOGE Bot: Baglanti Hatasi", f"{ts} tarihinde Binance sunucularina ulasilamadi.")

if __name__ == "__main__":
    run_bot()
