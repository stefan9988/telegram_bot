import pandas as pd
import os
from dotenv import load_dotenv
from LLMs.utils import create_trading_prompt
import config
from bot import send_telegram_message, send_telegram_photo
from crypto.data_analysis import analyze_bollinger, analyze_macd, analyze_moving_averages
from crypto.data_analysis import analyze_rsi, analyze_volume, analyze_market_regime
import asyncio

from crypto.calculations import calculate_purchase_amount

from LLMs.openAI import AzureChat
from LLMs.openRouter import OpenRouterLLM

load_dotenv(override=True)

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT:
    raise ValueError("Required environment variables are not set")

chat_instance = AzureChat(
            model_id = config.AZURE_MODEL_ID,
            api_key = AZURE_OPENAI_API_KEY,
            azure_endpoint = AZURE_OPENAI_ENDPOINT,
            system_message = config.SYSTEM_MESSAGE,
            temperature= config.TEMPERATURE,
            top_p = config.TOP_P,
        )
# chat_instance = OpenRouterLLM(
#             api_key=OPEN_ROUTER_API_KEY,
#             model_id=config.OPEN_ROUTER_MODEL_ID,
#             system_message=config.SYSTEM_MESSAGE,
#             temperature=config.TEMPERATURE,
#             top_p=config.TOP_P
#         )

#Load data
btc_data = pd.read_csv(config.BTC_DATA_PATH, index_col=False)
historical_data = pd.read_csv(config.HISTORICAL_DATA_PATH, index_col=False)
df_ohcl = pd.read_csv(config.OHLC_DATA_PATH, index_col=False)

# Perform technical analysis
ma_analysis = analyze_moving_averages(historical_data, window=config.WINDOW)
macd_analysis = analyze_macd(historical_data, window=config.WINDOW)
rsi_analysis = analyze_rsi(historical_data, window=config.WINDOW)
bollinger_analysis = analyze_bollinger(historical_data, window=config.WINDOW)
volume_analysis = analyze_volume(historical_data)
market_regime_analysis = analyze_market_regime(df_ohcl)

ta = ma_analysis + "\n" + macd_analysis + "\n" + rsi_analysis + "\n" + bollinger_analysis + "\n" + \
    volume_analysis + "\n" + market_regime_analysis

# Create message for LLM
message = create_trading_prompt(
    historical_data=historical_data,
    btc_data=btc_data,
    ta=ta,
    last_n_days=config.LAST_N_DAYS
)
response, usage = chat_instance.conv(message)
current_price = btc_data['current_price'].iloc[-1]
purchase_amount = calculate_purchase_amount(btc_data,historical_data)
msg = (
    f"{response}\n\n"
    f"Current Price: ${current_price:,}\n"
    f"Purchase Amount: ${purchase_amount:,}\n"
    f"Technical Analysis: \n{ta}"
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