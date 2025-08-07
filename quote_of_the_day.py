import os
import asyncio
import random
from dotenv import load_dotenv

import quote_of_the_day_config

from telegram_service.bot import TelegramNotifier

from LLMs.openRouter import OpenRouterLLM

load_dotenv(override=True)

OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
QOTD_BOT_TOKEN = os.getenv("QOTD_BOT_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

# --- Main Asynchronous Logic ---
async def main():
    # --- Initialization ---
    chat_instance = OpenRouterLLM(
        api_key=OPEN_ROUTER_API_KEY,
        model_id=quote_of_the_day_config.OPEN_ROUTER_MODEL_ID,
        system_message=quote_of_the_day_config.SYSTEM_MESSAGE,
        temperature=quote_of_the_day_config.TEMPERATURE,
        top_p=quote_of_the_day_config.TOP_P
    )
    notifier = TelegramNotifier(token=QOTD_BOT_TOKEN)

    # --- LLM Interaction ---
    print("Generating LLM response...")
    topic = random.choice(quote_of_the_day_config.TOPICS)
    message = f"Quote of the day about {topic}, please."
    response, usage = chat_instance.conv(message)
    print("LLM response received.")

    final_message = (
        f"{response}\n\n"
        f"Topic: {topic}\n"
        f"LLM: {chat_instance.model_id}\n"
    )
    
    # --- Send Notifications (within the same async context) ---
    print("Sending notifications to Telegram...")
    # These two tasks will run sequentially.
    await notifier.send_message(msg=final_message, chat_id=TELEGRAM_USER_ID)
    print("Notification sent.")


if __name__ == "__main__":
    # Run the entire async main function once.
    asyncio.run(main())