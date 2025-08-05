import pandas as pd
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
#TODO remove this import
df = pd.read_csv(config.HISTORICAL_DATA_PATH, index_col=False)

def analyze_moving_averages(df, window=3):
    """Check recent trend in MA50 vs MA200 over a few days"""
    recent = df.tail(window)
    golden_cross_days = (recent['MA50'] > recent['MA200']).sum()
    death_cross_days = (recent['MA50'] < recent['MA200']).sum()

    if golden_cross_days == window:
        return f"Consistent Uptrend (Golden Cross for {window} days)"
    elif death_cross_days == window:
        return f"Consistent Downtrend (Death Cross for {window} days)"
    elif recent.iloc[-1]['MA50'] > recent.iloc[-1]['MA200']:
        return "MA50 just crossed above MA200 (Potential Golden Cross)"
    elif recent.iloc[-1]['MA50'] < recent.iloc[-1]['MA200']:
        return "MA50 just crossed below MA200 (Potential Death Cross)"
    else:
        return "MAs are converging (Unclear trend)"


def analyze_macd(df, window=3):
    """Analyze MACD crossovers over the recent days"""
    recent = df.tail(window)
    signals = []

    for i in range(1, len(recent)):
        prev = recent.iloc[i - 1]
        curr = recent.iloc[i]

        if prev['MACD'] < prev['Signal_Line'] and curr['MACD'] > curr['Signal_Line']:
            signals.append("Bullish crossover")
        elif prev['MACD'] > prev['Signal_Line'] and curr['MACD'] < curr['Signal_Line']:
            signals.append("Bearish crossover")

    if signals:
        return f"MACD Crossovers Detected: {', '.join(signals)}"
    elif recent.iloc[-1]['MACD'] > recent.iloc[-1]['Signal_Line']:
        return "MACD shows bullish momentum"
    else:
        return "MACD shows bearish momentum"


def analyze_rsi(df, overbought=70, oversold=30, window=3):
    """Interpret RSI behavior over last few days"""
    recent_rsi = df.tail(window)['RSI']
    overbought_days = (recent_rsi > overbought).sum()
    oversold_days = (recent_rsi < oversold).sum()

    if overbought_days == window:
        return f"RSI consistently overbought ({recent_rsi.iloc[-1]:.2f})"
    elif oversold_days == window:
        return f"RSI consistently oversold ({recent_rsi.iloc[-1]:.2f})"
    elif recent_rsi.iloc[-1] > overbought:
        return f"RSI just entered overbought ({recent_rsi.iloc[-1]:.2f})"
    elif recent_rsi.iloc[-1] < oversold:
        return f"RSI just entered oversold ({recent_rsi.iloc[-1]:.2f})"
    else:
        return f"RSI neutral range ({recent_rsi.iloc[-1]:.2f})"


def analyze_bollinger(df, window=3):
    """Check if price has broken upper/lower Bollinger Band recently"""
    recent = df.tail(window)
    above_upper = (recent['price'] > recent['bollinger_upper']).sum()
    below_lower = (recent['price'] < recent['bollinger_lower']).sum()

    if above_upper == window:
        return f"Price consistently above upper band ({window} days) → Overbought"
    elif below_lower == window:
        return f"Price consistently below lower band ({window} days) → Oversold"
    elif recent.iloc[-1]['price'] > recent.iloc[-1]['bollinger_upper']:
        return "Price just broke above upper band → Overbought"
    elif recent.iloc[-1]['price'] < recent.iloc[-1]['bollinger_lower']:
        return "Price just broke below lower band → Oversold"
    else:
        return "Price within Bollinger Bands (Normal)"



print(analyze_moving_averages(df))
print(analyze_macd(df))
print(analyze_rsi(df))
print(analyze_bollinger(df))