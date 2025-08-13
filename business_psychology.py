import os
import asyncio
import random
from dotenv import load_dotenv

import business_psychology_config

from telegram_service.bot import TelegramNotifier

from LLMs.openRouter import OpenRouterLLM

load_dotenv(override=True)

OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
BUSINESS_BOT_TOKEN = os.getenv("BUSINESS_BOT_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

async def main():
    # Initialize LLM and notifier
    chat_instance = OpenRouterLLM(
        api_key=OPEN_ROUTER_API_KEY,
        model_id=business_psychology_config.OPEN_ROUTER_MODEL_ID,
        system_message=business_psychology_config.SYSTEM_MESSAGE,
        temperature=business_psychology_config.TEMPERATURE,
        top_p=business_psychology_config.TOP_P,
    )
    notifier = TelegramNotifier(token=BUSINESS_BOT_TOKEN)

    # Generate advice from LLM
    scenario = random.choice(business_psychology_config.SCENARIOS)
    print("Generating LLM response...")
    prompt = (
        f"Provide psychological advice for the following situation in a business context: {scenario}."
    )
    response, usage = chat_instance.conv(prompt)
    print("LLM response received.")

    final_message = (
        f"{response}\n\n"
        f"Scenario: {scenario}\n"
        f"LLM: {chat_instance.model_id}\n"
    )

    # Send advice to Telegram
    print("Sending notifications to Telegram...")
    await notifier.send_message(msg=final_message, chat_id=TELEGRAM_USER_ID)
    print("Notification sent.")


if __name__ == "__main__":
    asyncio.run(main())
