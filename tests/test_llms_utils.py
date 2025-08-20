import pandas as pd

from LLMs.utils import create_trading_prompt


def test_create_trading_prompt_includes_data_and_ta():
    df = pd.DataFrame({'price': [1, 2, 3], 'volume': [10, 20, 30]})
    ta = "Some analysis"
    prompt = create_trading_prompt(df, ta, last_n_days=2)
    assert "HISTORICAL_DATA:" in prompt
    assert ta in prompt
    assert df.tail(2).to_string() in prompt
