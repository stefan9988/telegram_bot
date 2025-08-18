import datetime
import pandas as pd
import os
import asyncio
import logging
from dotenv import load_dotenv

import crypto_config
from LLMs.utils import create_trading_prompt
from telegram_service.bot import TelegramNotifier
from crypto.data_analysis import (
    analyze_bollinger, analyze_macd, analyze_moving_averages,
    analyze_rsi, analyze_volume, analyze_market_regime
)
from crypto.calculations import calculate_purchase_amount
from LLMs.openAI import AzureChat
from LLMs.openRouter import OpenRouterLLM

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_llm_instance():
    """Selects and initializes the LLM based on the config file."""
    if crypto_config.LLM_PROVIDER.upper() == "AZURE":
        logger.info("Using Azure OpenAI LLM.")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not api_key or not endpoint:
            raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set.")
        return AzureChat(
            model_id=crypto_config.AZURE_MODEL_ID,
            api_key=api_key,
            azure_endpoint=endpoint,
            system_message=crypto_config.SYSTEM_MESSAGE,
            temperature=crypto_config.TEMPERATURE,
            top_p=crypto_config.TOP_P,
        )
    elif crypto_config.LLM_PROVIDER.upper() == "OPEN_ROUTER":
        logger.info("Using OpenRouter LLM.")
        api_key = os.getenv("OPEN_ROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPEN_ROUTER_API_KEY must be set.")
        return OpenRouterLLM(
            api_key=api_key,
            model_id=crypto_config.OPEN_ROUTER_MODEL_ID,
            system_message=crypto_config.SYSTEM_MESSAGE,
            temperature=crypto_config.TEMPERATURE,
            top_p=crypto_config.TOP_P
        )
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {crypto_config.LLM_PROVIDER}")

def save_message_to_daily_log(msg: str, log_directory: str):
    """
    Constructs a message and appends it to a log file named with the current date.

    Args:
        msg (str): The message to log.
        log_directory (str): The directory where log files will be saved.
    """
    # --- 1. Create the log directory if it doesn't exist ---
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
        logger.info(f"Created directory: {log_directory}")

    # --- 2. Generate the filename based on the current date ---
    # e.g., 'report_2023-10-27.txt'
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    filename = os.path.join(log_directory, f"report_{current_date}.txt")

    # --- 4. Open the file in 'write' mode and write the message ---
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(msg)
        logger.info(f"Successfully wrote message to '{filename}'")
    except IOError as e:
        logger.error(f"Error: Could not write to file '{filename}'. Reason: {e}")

# --- Main Asynchronous Logic ---
async def main():
    """
    Main execution function to perform analysis and send notifications.
    """
    # --- Setup ---
    load_dotenv(override=True)
    
    BTC_BOT_TOKEN = os.getenv("BTC_BOT_TOKEN")
    TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

    if not BTC_BOT_TOKEN or not TELEGRAM_USER_ID:
        logger.error("Error: Telegram environment variables not set.")
        return

    try:
        # --- Initialization ---
        chat_instance = get_llm_instance()
        notifier = TelegramNotifier(token=BTC_BOT_TOKEN)

        # --- Load Data (with error handling) ---
        logger.info("Loading data...")
        historical_data = pd.read_csv(crypto_config.HISTORICAL_DATA_PATH, index_col=False)
        df_ohcl = pd.read_csv(crypto_config.OHLC_DATA_PATH, index_col=False)
        logger.info("Data loaded successfully.")

    except FileNotFoundError as e:
        logger.error(f"Error: Data file not found - {e}")
        return
    except Exception as e:
        logger.error(f"An error occurred during setup or data loading: {e}")
        return
        
    # --- Perform Technical Analysis ---
    logger.info("Performing technical analysis...")
    analyses = [
        analyze_moving_averages(historical_data, window=crypto_config.WINDOW),
        analyze_macd(historical_data, window=crypto_config.WINDOW),
        analyze_rsi(historical_data, window=crypto_config.WINDOW),
        analyze_bollinger(historical_data, window=crypto_config.WINDOW),
        analyze_volume(historical_data),
        analyze_market_regime(df_ohcl)
    ]
    ta = "\n".join(analyses)
    logger.info("Analysis complete.")

    # --- LLM Interaction ---
    logger.info("Generating LLM response...")
    message = create_trading_prompt(
        historical_data=historical_data,
        ta=ta,
        last_n_days=crypto_config.LAST_N_DAYS
    )
    response, usage = chat_instance.conv(message)
    logger.info("LLM response received.")

    # --- Final Calculations and Message Formatting ---
    current_price = historical_data['price'].iloc[-1]
    purchase_amount = calculate_purchase_amount(historical_data)
    btc_dominance = historical_data['dominance_percentage'].iloc[-1]

    final_message = (
        f"Current Price: ${current_price:,.2f}\n"
        f"Suggested Purchase: ${purchase_amount:,.2f}\n\n"
        f"Technical Analysis Summary: \n{ta}\n"
        f"BTC Dominance: {btc_dominance:.2f}%\n\n"
        f"{response}\n\n"
        f"LLM: {chat_instance.model_id}"
    )
    save_message_to_daily_log(final_message, "reports")

    # --- Send Notifications (within the same async context) ---
    logger.info("Sending notifications to Telegram...")
    # These two tasks will run sequentially.
    await notifier.send_message(msg=final_message, chat_id=TELEGRAM_USER_ID)
    await notifier.send_photo(
        image_path=crypto_config.CRYPTO_INDICATORS_PATH,
        caption="Crypto Indicators Chart",
        chat_id=TELEGRAM_USER_ID
    )
    logger.info("Notifications sent.")


if __name__ == "__main__":
    # Run the entire async main function once.
    asyncio.run(main())

    #TODO add fear and greed index
    #TODO add altseason index
