import pandas as pd
import os
from dotenv import load_dotenv
import config

from crypto.get_btc_data import get_historical_price_data
from crypto.calculations import calculate_macd, calculate_moving_averages, calculate_purchase_amount
from crypto.calculations import calculate_mean_dominance, calculate_rsi
from openAI import AzureChat

load_dotenv(override=True)

N=15
BTC_DATA_PATH = "/home/stefandragicevic/telegram_bot/data/btc_data.csv"
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT:
    raise ValueError("Required environment variables are not set")

historical_data = get_historical_price_data()

if historical_data is not None:
    historical_data = calculate_moving_averages(historical_data)
    historical_data = calculate_macd(historical_data)
    historical_data = calculate_rsi(historical_data)    

btc_data = pd.read_csv(BTC_DATA_PATH, index_col=False)
btc_mean_dominance = calculate_mean_dominance(btc_data)

message = f"""
    Analyze the following Bitcoin market data and return a trading strategy with clear buy/sell signals, 
    technical justification, and a risk assessment.

    Below is the recent historical price data with calculated technical indicators (moving averages, MACD, RSI):

    HISTORICAL_DATA:
    {historical_data.tail(N).to_dict(orient="records")}

    Current market snapshot:

    BTC_DATA:
    {btc_data.tail(N).to_dict(orient="records")}"""


chat_instance = AzureChat(
            model_id = config.AZURE_MODEL_ID,
            api_key = AZURE_OPENAI_API_KEY,
            azure_endpoint = AZURE_OPENAI_ENDPOINT,
            system_message = config.SYSTEM_MESSAGE,
        )

# response, usage = chat_instance.conv(message)
# print(f"Response: {response}")
pa = calculate_purchase_amount(btc_data,historical_data)
print(f"Calculated Purchase Amount: {pa}")
