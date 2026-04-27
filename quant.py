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
    url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval=4h&limit=350"
    res = requests.get(url).json()
    df = pd.DataFrame(res, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qa', 't', 'tb', 'tq', 'i'])
    df[['o', 'h', 'l', 'c', 'v']] = df[['o', 'h', 'l', 'c', 'v']].astype(float)
    return df

def calculate_manual_indicators(df):
    df['ema200'] = df['c'].ewm(span=200, adjust=False).mean()
    delta = df['c'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    exp1 = df['c'].ewm(span=12, adjust=False).mean()
    exp2 = df['c'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['hist'] = df['macd'] - df['signal_line']
    df['atr'] = (df['h'] - df['l']).rolling(14).mean()
    return df

def send_mail(signal, price, sl, tp):
    ts = datetime.now().strftime('%d/%m/%Y %H:%M')
    subject = f"📊 DOGE Raporu: {signal}"
    content = f"Zaman: {ts}\nFiyat: {price:.5f}\nSinyal: {signal}\nSL: {sl:.5f}\nTP: {tp:.5f}"
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = SENDER_EMAIL
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, PASSWORD)
            server.sendmail(SENDER_EMAIL, SENDER_EMAIL, msg.as_string())
            print("Mail basariyla gonderildi.")
    except Exception as e:
        print(f"Mail gonderme hatasi: {e}")
        raise # Hatayi GitHub loglarina gonder

# Calistir
try:
    df = get_data()
    df = calculate_manual_indicators(df)
    last = df.iloc[-1]
    price, atr, rsi, hist, ema = last['c'], last['atr'], last['rsi'], last['hist'], last['ema200']
    
    signal = "BEKLE"
    sl, tp = 0, 0
    if price > ema and hist > 0 and rsi < 65:
        signal = "LONG"
        sl, tp = price - (atr * 1.5), price + (atr * 3)
    elif price < ema and hist < 0 and rsi > 35:
        signal = "SHORT"
        sl, tp = price + (atr * 1.5), price - (atr * 3)
    
    send_mail(signal, price, sl, tp)
except Exception as e:
    print(f"Genel hata: {e}")
    exit(1)
