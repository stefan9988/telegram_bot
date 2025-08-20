from crypto.get_btc_data import (
    get_historical_price_data,
    get_current_price_and_dominance,
    merge_dataframes,
    save_data_to_csv,
    get_historical_ohlc_data
)

from crypto.calculations import (
    calculate_macd,
    calculate_moving_averages,
    calculate_rsi,
    calculate_bollinger_bands
)

from crypto.data_visualisation import plot_crypto_indicators
import config.crypto_config as crypto_config
import os
from dotenv import load_dotenv
from telegram_service.bot import TelegramNotifier
import asyncio
import pandas as pd

load_dotenv(override=True)

BTC_BOT_TOKEN = os.getenv("BTC_BOT_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

notifier = TelegramNotifier(token=BTC_BOT_TOKEN)

def notify_and_exit(message: str):
    asyncio.run(notifier.send_message(msg=message, chat_id=TELEGRAM_USER_ID))
    exit(1)

historical_data = get_historical_price_data()
if historical_data is not None:
    historical_data = calculate_moving_averages(historical_data)
    historical_data = calculate_macd(historical_data)
    historical_data = calculate_rsi(historical_data)
    historical_data = calculate_bollinger_bands(historical_data)        
else:
    notify_and_exit("Failed to fetch historical Bitcoin data.")


current_data = get_current_price_and_dominance()
if current_data is None:
    notify_and_exit("Failed to fetch current Bitcoin data.")
else:
    save_data_to_csv(crypto_config.BTC_DATA_PATH, current_data)    

ohcl_data = get_historical_ohlc_data(coin_id='bitcoin', days=30)
if ohcl_data is not None:
    ohcl_data.to_csv(crypto_config.OHLC_DATA_PATH, index=False)
else:
    notify_and_exit("Failed to fetch OHLC data for Bitcoin.")

try:
    current_data = pd.read_csv(crypto_config.BTC_DATA_PATH, index_col=False)
    historical_data = merge_dataframes(current_data, historical_data)
    historical_data.to_csv(crypto_config.HISTORICAL_DATA_PATH, index=False)
except Exception as e:
    notify_and_exit(f"Error merging dataframes: {e}")

plot_crypto_indicators(historical_data, last_n_days=crypto_config.LAST_N_DAYS, savepath=crypto_config.CRYPTO_INDICATORS_PATH)