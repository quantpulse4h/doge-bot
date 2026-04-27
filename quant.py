import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# --- AYARLAR ---
SYMBOL = "DOGE"
SENDER_EMAIL = "quantpulse4h@gmail.com"
PASSWORD = "gjkkwqwcbzdcxclm" 

def get_data():
    """CryptoCompare üzerinden 4 saatlik detaylı veri çeker."""
    try:
        url = f"https://min-api.cryptocompare.com/data/v2/histohour?fsym={SYMBOL}&tsym=USDT&limit=300&aggregate=4"
        res = requests.get(url, timeout=20).json()
        if res['Response'] == 'Success':
            df = pd.DataFrame(res['Data']['Data'])
            # Sütun isimlerini standartlaştıralım
            df.rename(columns={'close': 'c', 'high': 'h', 'low': 'l', 'open': 'o', 'volumeto': 'v'}, inplace=True)
            return df
    except:
        return None

def calculate_indicators(df):
    df['c'] = df['c'].astype(float)
    # 1. EMA 200 (Ana Trend)
    df['ema200'] = df['c'].ewm(span=200, adjust=False).mean()
    # 2. RSI (Güç Endeksi)
    delta = df['c'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['rsi'] = 100 - (100 / (1 + (gain / loss)))
    # 3. MACD (Momentum)
    exp1 = df['c'].ewm(span=12, adjust=False).mean()
    exp2 = df['c'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['sig'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['hist'] = df['macd'] - df['sig']
    # 4. ATR (Kasa Yönetimi / TP-SL için)
    tr = pd.concat([df['h']-df['l'], abs(df['h']-df['c'].shift()), abs(df['l']-df['c'].shift())], axis=1).max(axis=1)
    df['atr'] = tr.rolling(window=14).mean()
    # 5. SMA 20 (Kısa Vade Onay)
    df['sma20'] = df['c'].rolling(window=20).mean()
    return df

def run_analysis():
    df = get_data()
    if df is None: return
    df = calculate_indicators(df)
    last = df.iloc[-1]
    
    price = last['c']
    ema = last['ema200']
    rsi = last['rsi']
    hist = last['hist']
    atr = last['atr']
    sma20 = last['sma200'] if 'sma200' in last else last['ema200'] # Güvenlik için

    # --- 5'TE 5 ONAY MEKANİZMASI ---
    long_conditions = [
        price > ema,        # 1. Fiyat EMA200 Üstü
        hist > 0,           # 2. MACD Histogram Pozitif
        rsi > 50,           # 3. RSI 50 Üstü (Güçlü)
        rsi < 70,           # 4. RSI Aşırı Alımda Değil
        price > last['o']   # 5. Mevcut Mum Yeşil
    ]
    
    short_conditions = [
        price < ema,        # 1. Fiyat EMA200 Altı
        hist < 0,           # 2. MACD Histogram Negatif
        rsi < 50,           # 3. RSI 50 Altı (Zayıf)
        rsi > 30,           # 4. RSI Aşırı Satımda Değil
        price < last['o']   # 5. Mevcut Mum Kırmızı
    ]

    onay_sayisi = 0
    signal = "BEKLE"
    leverage = "10x (Önerilen)"
    
    if all(long_conditions):
        signal = "LONG"
        onay_sayisi = 5
        tp = price + (atr * 3)
        sl = price - (atr * 1.5)
    elif all(short_conditions):
        signal = "SHORT"
        onay_sayisi = 5
        tp = price - (atr * 3)
        sl = price + (atr * 1.5)
    else:
        # Eğer 5'te 5 değilse kaç onay olduğunu hesapla (Bilgi amaçlı)
        onay_sayisi = sum(long_conditions) if price > ema else sum(short_conditions)
        tp, sl = 0, 0

    # --- MAIL GÖNDERİMİ ---
    ts = datetime.now().strftime('%d/%m/%Y %H:%M')
    subject = f"🤖 DOGE 4H: {signal} ({onay_sayisi}/5 Onay)"
    
    body = (f"🕒 Zaman: {ts}\n"
            f"💰 Güncel Fiyat: {price:.5f}\n"
            f"📊 Sinyal Durumu: {signal}\n"
            f"✅ Onay Skoru: {onay_sayisi}/5\n\n"
            f"⚙️ İşlem Detayları:\n"
            f"------------------------\n"
            f"🚀 Kaldıraç: {leverage}\n"
            f"🎯 Kar Al (TP): {tp:.5f}\n"
            f"🛑 Zarar Durdur (SL): {sl:.5f}\n\n"
            f"📈 Teknik Veriler:\n"
            f"EMA200: {ema:.5f}\n"
            f"RSI: {rsi:.2f}\n"
            f"MACD Hist: {hist:.6f}\n"
            f"ATR: {atr:.6f}\n\n"
            f"Not: Bu rapor CryptoCompare yedek hattı üzerinden oluşturulmuştur.")

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = SENDER_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, SENDER_EMAIL, msg.as_string())

if __name__ == "__main__":
    run_analysis()
