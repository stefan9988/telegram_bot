import pandas as pd
import os
from dotenv import load_dotenv
import config
from bot import send_telegram_message
import asyncio

from crypto.get_btc_data import get_historical_price_data
from crypto.calculations import calculate_macd, calculate_moving_averages, calculate_purchase_amount
from crypto.calculations import calculate_mean_dominance, calculate_rsi
from openAI import AzureChat

load_dotenv(override=True)

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT:
    raise ValueError("Required environment variables are not set")

historical_data = get_historical_price_data()

if historical_data is not None:
    historical_data = calculate_moving_averages(historical_data)
    historical_data = calculate_macd(historical_data)
    historical_data = calculate_rsi(historical_data)    
    historical_data.to_csv(config.HISTORICAL_DATA_PATH)
else:
    historical_data = pd.read_csv(config.HISTORICAL_DATA_PATH, index_col=False)

btc_data = pd.read_csv(config.BTC_DATA_PATH, index_col=False)
btc_mean_dominance = calculate_mean_dominance(btc_data)

message = f"""
    Analyze the following Bitcoin market data and return a trading strategy with clear buy/sell signals, 
    technical justification, and a risk assessment.

    Below is the recent historical price data with calculated technical indicators (moving averages, MACD, RSI):

    HISTORICAL_DATA:
    {historical_data.tail(config.LAST_N_DAYS).to_dict(orient="records")}

    Current market snapshot:

    BTC_DATA:
    {btc_data.tail(config.LAST_N_DAYS).to_dict(orient="records")}"""


chat_instance = AzureChat(
            model_id = config.AZURE_MODEL_ID,
            api_key = AZURE_OPENAI_API_KEY,
            azure_endpoint = AZURE_OPENAI_ENDPOINT,
            system_message = config.SYSTEM_MESSAGE,
            temperature= config.TEMPERATURE,
            top_p = config.TOP_P,
        )

response, usage = chat_instance.conv(message)
current_price = btc_data['current_price'].iloc[-1]
purchase_amount = calculate_purchase_amount(btc_data,historical_data)
msg = (
    f"{response}\n\n"
    f"Current Price: ${current_price:,}\n"
    f"Purchase Amount: ${purchase_amount:,}"
)

asyncio.run(send_telegram_message(
    msg=msg,
    bot_token=BOT_TOKEN,
    user_id=TELEGRAM_USER_ID
))