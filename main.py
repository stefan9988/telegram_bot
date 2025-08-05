import pandas as pd
import os
from dotenv import load_dotenv
import config
from bot import send_telegram_message, send_telegram_photo
import asyncio

from crypto.get_btc_data import get_historical_price_data, get_current_price_and_dominance, save_data_to_csv
from crypto.data_visualisation import plot_crypto_indicators
from crypto.calculations import calculate_macd, calculate_moving_averages, calculate_purchase_amount
from crypto.calculations import calculate_mean_dominance, calculate_rsi, calculate_bollinger_bands
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
    historical_data = calculate_bollinger_bands(historical_data)    
    historical_data.to_csv(config.HISTORICAL_DATA_PATH)
else:
    asyncio.run(send_telegram_message(
        msg="Failed to fetch historical Bitcoin data.",
        bot_token=BOT_TOKEN,
        user_id=TELEGRAM_USER_ID
    ))
    exit(1)

plot_crypto_indicators(historical_data, last_n_days=config.LAST_N_DAYS, savepath=config.CRYPTO_INDICATORS_PATH)

current_data = get_current_price_and_dominance()
if current_data is None:
    asyncio.run(send_telegram_message(
        msg="Failed to fetch current Bitcoin data.",
        bot_token=BOT_TOKEN,
        user_id=TELEGRAM_USER_ID
    ))
    exit(1)
else:
    save_data_to_csv(config.BTC_DATA_PATH, current_data)    

btc_data = pd.read_csv(config.BTC_DATA_PATH)
btc_mean_dominance = calculate_mean_dominance(btc_data)

chat_instance = AzureChat(
            model_id = config.AZURE_MODEL_ID,
            api_key = AZURE_OPENAI_API_KEY,
            azure_endpoint = AZURE_OPENAI_ENDPOINT,
            system_message = config.SYSTEM_MESSAGE,
            temperature= config.TEMPERATURE,
            top_p = config.TOP_P,
        )

message = chat_instance.create_msg(
    historical_data=historical_data,
    btc_data=btc_data,
    last_n_days=config.LAST_N_DAYS
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
asyncio.run(send_telegram_photo(
    image_path=config.CRYPTO_INDICATORS_PATH, 
    caption="Crypto Indicators", 
    bot_token=BOT_TOKEN, 
    user_id=TELEGRAM_USER_ID
))