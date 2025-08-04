def calculate_moving_averages(df):
    """
    Add 50-day and 200-day simple moving averages to the DataFrame.
    
    Parameters:
    - df: DataFrame with Bitcoin prices and datetime index.

    Returns:
    - DataFrame with 'MA50' and 'MA200' columns added.
    """
    if df is None or df.empty:
        print("Input DataFrame is empty or None.")
        return None

    df['MA50'] = df['price'].rolling(window=50).mean()
    df['MA200'] = df['price'].rolling(window=200).mean()

    return df

def calculate_mean_dominance(df):
    last_50_dominance = df['dominance_percentage'].tail(50)
    mean_dominance = last_50_dominance.mean()

    return mean_dominance

def calculate_rsi(df, period=14):
    """
    Calculate the Relative Strength Index (RSI).

    Parameters:
    - df: DataFrame with 'price' column.
    - period: Period over which RSI is calculated.

    Returns:
    - DataFrame with 'RSI' column added.
    """
    delta = df['price'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df

def calculate_macd(df, fast=12, slow=26, signal=9):
    """
    Calculate MACD and Signal Line.

    Parameters:
    - df: DataFrame with 'price' column.
    - fast: Fast EMA period (default 12)
    - slow: Slow EMA period (default 26)
    - signal: Signal line EMA period (default 9)

    Returns:
    - DataFrame with 'MACD' and 'Signal_Line' columns added.
    """
    ema_fast = df['price'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['price'].ewm(span=slow, adjust=False).mean()

    df['MACD'] = ema_fast - ema_slow
    df['Signal_Line'] = df['MACD'].ewm(span=signal, adjust=False).mean()

    return df

def calculate_purchase_amount(data,historical_data):
    ma200 = historical_data['MA200'].iloc[-1]
    current_price = historical_data['price'].iloc[-1]
    current_dominance = data['dominance_percentage'].iloc[-1]
    dom200 = calculate_mean_dominance(data)

    purchase = 100 * (ma200 / current_price) * (dom200/current_dominance)

    return round(purchase, 2)