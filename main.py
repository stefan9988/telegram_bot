import pandas as pd
import os
import asyncio
from dotenv import load_dotenv

import config
from LLMs.utils import create_trading_prompt
from telegram_service.bot import TelegramNotifier
from crypto.data_analysis import (
    analyze_bollinger, analyze_macd, analyze_moving_averages,
    analyze_rsi, analyze_volume, analyze_market_regime
)
from crypto.calculations import calculate_purchase_amount
from LLMs.openAI import AzureChat
from LLMs.openRouter import OpenRouterLLM

def get_llm_instance():
    """Selects and initializes the LLM based on the config file."""
    if config.LLM_PROVIDER.upper() == "AZURE":
        print("Using Azure OpenAI LLM.")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not api_key or not endpoint:
            raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set.")
        return AzureChat(
            model_id=config.AZURE_MODEL_ID,
            api_key=api_key,
            azure_endpoint=endpoint,
            system_message=config.SYSTEM_MESSAGE,
            temperature=config.TEMPERATURE,
            top_p=config.TOP_P,
        )
    elif config.LLM_PROVIDER.upper() == "OPEN_ROUTER":
        print("Using OpenRouter LLM.")
        api_key = os.getenv("OPEN_ROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPEN_ROUTER_API_KEY must be set.")
        return OpenRouterLLM(
            api_key=api_key,
            model_id=config.OPEN_ROUTER_MODEL_ID,
            system_message=config.SYSTEM_MESSAGE,
            temperature=config.TEMPERATURE,
            top_p=config.TOP_P
        )
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {config.LLM_PROVIDER}")

# --- Main Asynchronous Logic ---
async def main():
    """
    Main execution function to perform analysis and send notifications.
    """
    # --- Setup ---
    load_dotenv(override=True)
    
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))
    
    if not BOT_TOKEN or not TELEGRAM_USER_ID:
        print("Error: Telegram environment variables not set.")
        return

    try:
        # --- Initialization ---
        chat_instance = get_llm_instance()
        notifier = TelegramNotifier(token=BOT_TOKEN)

        # --- Load Data (with error handling) ---
        print("Loading data...")
        btc_data = pd.read_csv(config.BTC_DATA_PATH, index_col=False)
        historical_data = pd.read_csv(config.HISTORICAL_DATA_PATH, index_col=False)
        df_ohcl = pd.read_csv(config.OHLC_DATA_PATH, index_col=False)
        print("Data loaded successfully.")

    except FileNotFoundError as e:
        print(f"Error: Data file not found - {e}")
        return
    except Exception as e:
        print(f"An error occurred during setup or data loading: {e}")
        return

    # --- Perform Technical Analysis ---
    print("Performing technical analysis...")
    analyses = [
        analyze_moving_averages(historical_data, window=config.WINDOW),
        analyze_macd(historical_data, window=config.WINDOW),
        analyze_rsi(historical_data, window=config.WINDOW),
        analyze_bollinger(historical_data, window=config.WINDOW),
        analyze_volume(historical_data),
        analyze_market_regime(df_ohcl)
    ]
    ta = "\n".join(analyses)
    print("Analysis complete.")

    # --- LLM Interaction ---
    print("Generating LLM response...")
    message = create_trading_prompt(
        historical_data=historical_data,
        btc_data=btc_data,
        ta=ta,
        last_n_days=config.LAST_N_DAYS
    )
    response, usage = chat_instance.conv(message)
    print("LLM response received.")

    # --- Final Calculations and Message Formatting ---
    current_price = btc_data['current_price'].iloc[-1]
    purchase_amount = calculate_purchase_amount(btc_data, historical_data)
    
    final_message = (
        f"{response}\n\n"
        f"**Current Price:** ${current_price:,.2f}\n"
        f"**Suggested Purchase:** ${purchase_amount:,.2f}\n\n"
        f"--- Technical Analysis Summary ---\n{ta}"
    )

    # --- Send Notifications (within the same async context) ---
    print("Sending notifications to Telegram...")
    # These two tasks will run sequentially.
    await notifier.send_message(msg=final_message, chat_id=TELEGRAM_USER_ID)
    await notifier.send_photo(
        image_path=config.CRYPTO_INDICATORS_PATH,
        caption="Crypto Indicators Chart",
        chat_id=TELEGRAM_USER_ID
    )
    print("Notifications sent.")


# --- Entry Point ---
if __name__ == "__main__":
    # Run the entire async main function once.
    asyncio.run(main())