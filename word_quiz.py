import os
import asyncio
import random
import re
import logging
from dotenv import load_dotenv
from quote_of_the_day import get_learned_words

import config.word_quiz_config as word_quiz_config

from telegram_service.bot import TelegramNotifier

from LLMs.factory import get_llm_instance
from requests.exceptions import HTTPError, RequestException

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv(override=True)

QOTD_BOT_TOKEN = os.getenv("QOTD_BOT_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

def clean_words(words: list[str]) -> list[str]:
    """Lowercase and strip extra spaces from each word."""
    return [w.strip().lower() for w in words]

def evaluate_answers(correct_words: list[str], user_words: list[str]) -> str:
    cw = clean_words(correct_words)
    uw = clean_words(user_words)

    results = []
    min_len = min(len(cw), len(uw))

    for i in range(min_len):
        if cw[i] == uw[i]:
            results.append(f"{i+1}. {cw[i]} == {uw[i]} ✅")
        else:
            results.append(f"{i+1}. {cw[i]} != {uw[i]} ❌")

    if len(cw) != len(uw):
        results.append(
            f"⚠️ List size mismatch: {len(cw)} correct words vs {len(uw)} user words"
        )

    return "\n".join(results)


# --- Main Asynchronous Logic ---
async def main():
    # --- Initialization ---
    chat_instance = get_llm_instance(word_quiz_config)
    notifier = TelegramNotifier(token=QOTD_BOT_TOKEN)
    learned_words = get_learned_words(word_quiz_config.FILEPATH)
    learned_words = learned_words.split(",")[:-1]
    learned_words = learned_words[-word_quiz_config.N_WORDS:]
    shuffled_words = learned_words.copy()
    random.shuffle(shuffled_words)

    # --- LLM Interaction ---
    logger.info("Generating LLM response for words: %s", ", ".join(shuffled_words))
    message = f"Create sentences for the following words: {', '.join(shuffled_words)}"
    response, usage = chat_instance.conv(message)
    logger.info("LLM response received. Usage: %s", usage)

    final_message = (
        f"📝 Word quiz:\n\n"
        "👉 Use the following words in sentences:\n"
        f"🔹 {', '.join(learned_words)}\n\n"
        f"{response}\n\n"
        f"📌 Response should be in this format: \nword1, word2, word3, word4\n\n"
        f"LLM: {chat_instance.model_id}"
    )

    # --- Send Notifications (within the same async context) ---
    logger.info("Sending notifications to Telegram...")
    # These two tasks will run sequentially.
    await notifier.send_message(msg=final_message, chat_id=TELEGRAM_USER_ID)
    logger.info("Notification sent.")

    # Start checking for updates for the next 30 minutes
    start_time = asyncio.get_event_loop().time()
    end_time = start_time + (30 * 60)  # 30 minutes in seconds
    
    while asyncio.get_event_loop().time() < end_time:
        try:
            telegram_response = await notifier.get_updates()
            if telegram_response != []:
                logger.info("Received user response. %s", telegram_response)
                break
            await asyncio.sleep(10)
        except (HTTPError, RequestException) as e:
            logger.error("Error getting updates: %s", e)
            await asyncio.sleep(10)
        except KeyboardInterrupt:
            logger.info("Stopping update checks...")
            break
    
    logger.info("30 minute update period completed.")
    
    user_answers = telegram_response[0].split(", ")

    evaluation = evaluate_answers(shuffled_words, user_answers)
    await notifier.send_message(msg=evaluation, chat_id=TELEGRAM_USER_ID)

if __name__ == "__main__":
    # Run the entire async main function once.
    asyncio.run(main())
