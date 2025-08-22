import os
import asyncio
import random
import logging
from dotenv import load_dotenv

import config.business_psychology_config as business_psychology_config

from telegram_service.bot import TelegramNotifier

from LLMs.factory import get_llm_instance

load_dotenv(override=True)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BUSINESS_BOT_TOKEN = os.getenv("BUSINESS_BOT_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

async def main():
    # Initialize LLM and notifier
    chat_instance = get_llm_instance(business_psychology_config)
    notifier = TelegramNotifier(token=BUSINESS_BOT_TOKEN)

    # Generate advice from LLM
    scenario = random.choice(business_psychology_config.SCENARIOS)
    context_twist = random.choice(business_psychology_config.CONTEXT_TWISTS)
    alternative_context_twist = random.choice(business_psychology_config.CONTEXT_TWISTS)
    logger.info("Generating LLM response...")
    prompt = (
        f"Provide psychological advice for the following situation in a business context: {scenario}. "
        f"Consider the following context twist: {context_twist}. Alternative context twist: {alternative_context_twist}"
    )
    response, usage = chat_instance.conv(prompt)
    logger.info("LLM response received.")

    final_message = (
        f"Scenario: {scenario}\n"
        f"Context Twist: {context_twist}\n"
        f"Alternative Context Twist: {alternative_context_twist}\n\n"
        f"{response}\n\n"
        f"LLM: {chat_instance.model_id}"
    )

    # Send advice to Telegram
    logger.info("Sending notifications to Telegram...")
    await notifier.send_message(msg=final_message, chat_id=TELEGRAM_USER_ID)
    logger.info("Notification sent.")


if __name__ == "__main__":
    asyncio.run(main())
