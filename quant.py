import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import time

# --- AYARLAR ---
SYMBOL = "DOGE"
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

def get_data_backup():
    """Binance yerine CryptoCompare üzerinden veri çeker (Daha stabil)."""
    try:
        url = f"https://min-api.cryptocompare.com/data/v2/histohour?fsym={SYMBOL}&tsym=USDT&limit=250&aggregate=4"
        res = requests.get(url, timeout=20).json()
        if res['Response'] == 'Success':
            df = pd.DataFrame(res['Data']['Data'])
            df.rename(columns={'close': 'c', 'time': 'ts'}, inplace=True)
            return df
    except:
        return None

def run_bot():
    ts = datetime.now().strftime('%d/%m/%Y %H:%M')
    print(f"Tarama basladi: {ts}")
    
    # Veriyi çek (CryptoCompare üzerinden)
    df = get_data_backup()
    
    if df is not None and not df.empty:
        df['c'] = df['c'].astype(float)
        # EMA 200 Analizi
        df['ema200'] = df['c'].ewm(span=200, adjust=False).mean()
        
        last_price = df.iloc[-1]['c']
        ema = df.iloc[-1]['ema200']
        
        signal = "LONG" if last_price > ema else "SHORT"
        
        body = f"Zaman: {ts}\nFiyat: {last_price}\nEMA200: {ema:.5f}\nSinyal: {signal}\nNot: Veri yedek kaynaktan alindi."
        send_mail(f"🚀 DOGE 4H Raporu: {signal}", body)
        print(f"Analiz tamamlandi: {signal}")
    else:
        send_mail("⚠️ DOGE Bot: Kritik Hata", f"{ts} tarihinde tum veri kaynaklari (Binance ve Yedek) reddedildi.")

if __name__ == "__main__":
    run_bot()
