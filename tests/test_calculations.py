import pandas as pd
import pytest

from crypto.calculations import (
    calculate_moving_averages,
    calculate_mean_dominance,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_purchase_amount,
)


def test_calculate_moving_averages():
    df = pd.DataFrame({'price': range(1, 211)})
    result = calculate_moving_averages(df.copy())
    assert result['MA50'].iloc[-1] == pytest.approx(185.5)
    assert result['MA200'].iloc[-1] == pytest.approx(110.5)


def test_calculate_mean_dominance():
    df = pd.DataFrame({'dominance_percentage': [40, 50, 60, 70, 80]})
    expected = (60 + 70 + 80) / 3
    assert calculate_mean_dominance(df, period=3) == pytest.approx(expected)


def test_calculate_rsi_all_gains():
    df = pd.DataFrame({'price': list(range(1, 16))})
    result = calculate_rsi(df.copy(), period=14)
    assert result['RSI'].iloc[-1] == pytest.approx(100)


def test_calculate_macd():
    df = pd.DataFrame({'price': range(1, 61)})
    result = calculate_macd(df.copy())
    ema_fast = df['price'].ewm(span=12, adjust=False).mean().round(2)
    ema_slow = df['price'].ewm(span=26, adjust=False).mean().round(2)
    macd_series = (ema_fast - ema_slow).round(2)
    signal_series = macd_series.ewm(span=9, adjust=False).mean().round(2)
    assert result['MACD'].iloc[-1] == macd_series.iloc[-1]
    assert result['Signal_Line'].iloc[-1] == signal_series.iloc[-1]


def test_calculate_bollinger_bands():
    df = pd.DataFrame({'price': range(1, 51)})
    result = calculate_bollinger_bands(df.copy(), window=20, num_std_dev=2)
    mid = df['price'].rolling(20).mean().round(2).iloc[-1]
    std = df['price'].rolling(20).std().round(2).iloc[-1]
    assert result['bollinger_mid'].iloc[-1] == mid
    assert result['bollinger_upper'].iloc[-1] == pytest.approx(round(mid + 2 * std, 2))
    assert result['bollinger_lower'].iloc[-1] == pytest.approx(round(mid - 2 * std, 2))


def test_calculate_purchase_amount():
    df = pd.DataFrame({'price': [100] * 200, 'dominance_percentage': [50] * 200})
    df = calculate_moving_averages(df)
    purchase = calculate_purchase_amount(df)
    assert purchase == 100
