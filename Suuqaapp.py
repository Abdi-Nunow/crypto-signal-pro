import streamlit as st
from PIL import Image
import numpy as np
import pytesseract
import cv2
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
from ta.trend import EMAIndicator

# Title
st.title("📈 Crypto Signal Pro App")

# Upload Image
uploaded_file = st.file_uploader("Upload a chart screenshot", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Chart', use_container_width=True)
    
    # OCR extraction from image
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    text = pytesseract.image_to_string(img_cv)
    st.text("🔍 Extracted Text from Chart:\n" + text)
    
    # Dummy prices for testing
    close_prices = np.random.normal(100, 10, 100)
    
    # Get live data from Binance API
    binance_url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=100"
    response = requests.get(binance_url)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close time', 'Quote asset volume', 'Number of trades',
            'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
        ])
        df['Close'] = df['Close'].astype(float)
        close_prices = df['Close'].values
    
    # Calculate indicators
    close_series = pd.Series(close_prices)
    rsi = RSIIndicator(close_series).rsi().iloc[-1]
    macd = MACD(close_series)
    macd_val = macd.macd().iloc[-1]
    macd_signal = macd.macd_signal().iloc[-1]
    bb = BollingerBands(close_series)
    bb_upper = bb.bollinger_hband().iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]
    ema = EMAIndicator(close_series, window=20).ema_indicator().iloc[-1]
    
    st.text(f"🔍 RSI: {rsi:.2f}")
    st.text(f"🔍 MACD: {macd_val:.4f} vs Signal: {macd_signal:.4f}")
    st.text(f"🔍 Bollinger Bands: Upper {bb_upper:.2f}, Lower {bb_lower:.2f}")
    st.text(f"🔍 EMA(20): {ema:.2f}")
    
    # Decision logic
    decision = "LONG" if rsi < 30 and macd_val > macd_signal else \
               "SHORT" if rsi > 70 and macd_val < macd_signal else \
               "❓ Unclear Signal"
    st.text(f"🏁 Final Decision: {decision}")
    
    # Entry/TP/SL logic
    current_price = close_prices[-1]
    if decision == "LONG":
        entry = current_price
        tp = entry * 1.02
        sl = entry * 0.98
    elif decision == "SHORT":
        entry = current_price
        tp = entry * 0.98
        sl = entry * 1.02
    else:
        entry, tp, sl = None, None, None
    
    if entry:
        st.text(f"💰 Entry: {entry:.2f}")
        st.text(f"🎯 Take Profit: {tp:.2f}")
        st.text(f"🛑 Stop Loss: {sl:.2f}")
    else:
        st.warning("⚠️ Cannot provide Entry/TP/SL as the signal is unclear.")
else:
    st.info("📂 Please upload a chart screenshot to analyze.")

