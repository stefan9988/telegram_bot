import pandas as pd

from crypto.get_btc_data import merge_dataframes


def test_merge_dataframes_replaces_last_price():
    btc_data = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'current_price': [100, 110],
        'dominance_percentage': [50, 60],
        'market_cap_usd': [1000, 1100],
        '24h_change_percentage': [1, 2]
    })
    hist = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'price': [90, 95]
    })
    merged = merge_dataframes(btc_data, hist)
    assert merged['price'].iloc[-1] == 110
    assert merged['dominance_percentage'].iloc[-1] == 60
