import pandas_ta as ta
import pandas as pd

def analyze_moving_averages(df, window=3):
    """Check recent trend in MA50 vs MA200 over a few days"""
    recent = df.tail(window)
    golden_cross_days = (recent['MA50'] > recent['MA200']).sum()
    death_cross_days = (recent['MA50'] < recent['MA200']).sum()

    if golden_cross_days == window:
        return f"Consistent Uptrend (Golden Cross for {window} days) 🟢"
    elif death_cross_days == window:
        return f"Consistent Downtrend (Death Cross for {window} days) 🔴"
    elif recent.iloc[-1]['MA50'] > recent.iloc[-1]['MA200']:
        return "MA50 just crossed above MA200 (Potential Golden Cross) 🟢"
    elif recent.iloc[-1]['MA50'] < recent.iloc[-1]['MA200']:
        return "MA50 just crossed below MA200 (Potential Death Cross) 🔴"
    else:
        return "MAs are converging (Unclear trend) ⚪"


def analyze_macd(df, window=3):
    """Analyze MACD crossovers over the recent days"""
    recent = df.tail(window)
    signals = []

    last_index = recent.index[-1]
    is_datetime = pd.api.types.is_datetime64_any_dtype(recent.index)

    for i in range(1, len(recent)):
        prev = recent.iloc[i - 1]
        curr = recent.iloc[i]
        curr_index = recent.index[i]

        if prev['MACD'] < prev['Signal_Line'] and curr['MACD'] > curr['Signal_Line']:
            days_ago = (last_index - curr_index).days if is_datetime else len(recent) - i - 1
            signals.append(f"Bullish crossover {days_ago} days ago 🟢")
        elif prev['MACD'] > prev['Signal_Line'] and curr['MACD'] < curr['Signal_Line']:
            days_ago = (last_index - curr_index).days if is_datetime else len(recent) - i - 1
            signals.append(f"Bearish crossover {days_ago} days ago 🔴")

    if signals:
        return f"MACD Crossovers Detected:\n{',\n'.join(signals)}"
    elif recent.iloc[-1]['MACD'] > recent.iloc[-1]['Signal_Line']:
        return "MACD shows bullish momentum 🟢"
    else:
        return "MACD shows bearish momentum 🔴"


def analyze_rsi(df, overbought=70, oversold=30, window=3):
    """Interpret RSI behavior over last few days"""
    recent_rsi = df.tail(window)['RSI']
    overbought_days = (recent_rsi > overbought).sum()
    oversold_days = (recent_rsi < oversold).sum()

    if overbought_days == window:
        return f"RSI consistently overbought ({recent_rsi.iloc[-1]:.2f}) 🔴"
    elif oversold_days == window:
        return f"RSI consistently oversold ({recent_rsi.iloc[-1]:.2f}) 🟢"
    elif recent_rsi.iloc[-1] > overbought:
        return f"RSI just entered overbought ({recent_rsi.iloc[-1]:.2f}) 🔴"
    elif recent_rsi.iloc[-1] < oversold:
        return f"RSI just entered oversold ({recent_rsi.iloc[-1]:.2f}) 🟢"
    else:
        return f"RSI neutral range ({recent_rsi.iloc[-1]:.2f}) ⚪"


def analyze_bollinger(df, window=3):
    """Check if price has broken upper/lower Bollinger Band recently"""
    recent = df.tail(window)
    above_upper = (recent['price'] > recent['bollinger_upper']).sum()
    below_lower = (recent['price'] < recent['bollinger_lower']).sum()

    if above_upper == window:
        return f"Price consistently above upper band ({window} days) → Overbought 🔴"
    elif below_lower == window:
        return f"Price consistently below lower band ({window} days) → Oversold 🟢"
    elif recent.iloc[-1]['price'] > recent.iloc[-1]['bollinger_upper']:
        return "Price above upper band → Overbought 🔴"
    elif recent.iloc[-1]['price'] < recent.iloc[-1]['bollinger_lower']:
        return "Price below lower band → Oversold 🟢"
    else:
        return "Price within Bollinger Bands (Normal) ⚪"

def analyze_volume(df, ma_period=20, spike_multiplier=1.5):
    """
    Analyzes the most recent volume against its moving average.
    A price move on high volume is more significant than one on low volume.
    """
    df_copy = df.copy()
    volume_ma_col = f'volume_ma_{ma_period}'
    df_copy[volume_ma_col] = df_copy['volume'].rolling(window=ma_period).mean()
    
    recent = df_copy.iloc[-1]
    
    if pd.isna(recent[volume_ma_col]):
        return "Volume (Not enough data)"
        
    volume = recent['volume']
    volume_ma = recent[volume_ma_col]
    
    if volume > volume_ma * spike_multiplier:
        return f"High Volume Spike ({volume/volume_ma:.1f}x average) 🟢"
    elif volume > volume_ma:
        return "Above Average Volume 🟢"
    else:
        return "Below Average Volume 🔴"

def analyze_market_regime(df, adx_period=14):
    """
    Determines if the market is trending or ranging using the ADX.
    - ADX > 25: Trending market (strong)
    - ADX < 20: Ranging market (weak or no trend)
    - Direction is determined by comparing DMP and DMN lines.
    """
    df_copy = df.copy()
    
    df_copy.ta.adx(
        high=df_copy['high'], 
        low=df_copy['low'],
        close=df_copy['close'],
        length=adx_period, 
        append=True
    )
    
    adx_col = f'ADX_{adx_period}'
    dmp_col = f'DMP_{adx_period}' 
    dmn_col = f'DMN_{adx_period}' 
    
    # Handle cases where there isn't enough data
    if adx_col not in df_copy.columns or df_copy[adx_col].isna().all():
        return "Regime (Not enough data)"
        
    recent_adx = df_copy[adx_col].iloc[-1]
    recent_dmp = df_copy[dmp_col].iloc[-1]
    recent_dmn = df_copy[dmn_col].iloc[-1]
    
    if recent_adx > 25:
        if recent_dmp > recent_dmn:
            return f"Strong Bullish Trend (ADX: {recent_adx:.1f}) 🟢"
        else:
            return f"Strong Bearish Trend (ADX: {recent_adx:.1f}) 🔴"
    elif recent_adx < 20:
        return f"Sideways / Ranging Market (ADX: {recent_adx:.1f}) ⚪"
    else: # ADX is between 20 and 25
        return f"Neutral / Trend Developing (ADX: {recent_adx:.1f}) ⚪"