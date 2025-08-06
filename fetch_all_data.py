from crypto.get_btc_data import get_historical_price_data, get_current_price_and_dominance
from crypto.get_btc_data import save_data_to_csv, get_historical_ohlc_data
from crypto.data_visualisation import plot_crypto_indicators
from crypto.calculations import calculate_macd, calculate_moving_averages
from crypto.calculations import calculate_rsi, calculate_bollinger_bands
import config
import os
from dotenv import load_dotenv
from telegram_service.bot import TelegramNotifier
import asyncio

load_dotenv(override=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

notifier = TelegramNotifier(token=BOT_TOKEN)

historical_data = get_historical_price_data()
if historical_data is not None:
    historical_data = calculate_moving_averages(historical_data)
    historical_data = calculate_macd(historical_data)
    historical_data = calculate_rsi(historical_data)
    historical_data = calculate_bollinger_bands(historical_data)    
    historical_data.to_csv(config.HISTORICAL_DATA_PATH, index=False)
else:
    asyncio.run(notifier.send_message(
        msg="Failed to fetch historical Bitcoin data.",
        chat_id=TELEGRAM_USER_ID
    ))
    exit(1)


current_data = get_current_price_and_dominance()
if current_data is None:
    asyncio.run(notifier.send_message(
        msg="Failed to fetch current Bitcoin data.",
        chat_id=TELEGRAM_USER_ID
    ))
    exit(1)
else:
    save_data_to_csv(config.BTC_DATA_PATH, current_data)    

ohcl_data = get_historical_ohlc_data(coin_id='bitcoin', days=30)
if ohcl_data is not None:
    ohcl_data.to_csv(config.OHLC_DATA_PATH, index=False)
else:
    asyncio.run(notifier.send_message(
        msg="Failed to fetch OHLC data for Bitcoin.",
        chat_id=TELEGRAM_USER_ID
    ))
    exit(1)

plot_crypto_indicators(historical_data, last_n_days=config.LAST_N_DAYS, savepath=config.CRYPTO_INDICATORS_PATH)