import pandas as pd

def create_trading_prompt(historical_data: pd.DataFrame, btc_data: pd.DataFrame, ta: str, last_n_days: int) -> str:
    """
    Creates a prompt for the LLM based on Bitcoin market data.
    """
    prompt = f"""
        Analyze the following Bitcoin market data and return a trading strategy with clear buy/sell signals, 
        technical justification, and a risk assessment.

        Below is the recent historical price data with calculated technical indicators (MA, MACD, RSI):

        HISTORICAL_DATA:
        {historical_data.tail(last_n_days).to_string()}

        Current market snapshot:

        BTC_DATA:
        {btc_data.tail(last_n_days).to_string()}

        Technical Analysis Summary:
        {ta}
    """
    return prompt