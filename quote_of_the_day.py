import os
import asyncio
import random
import re
import logging
from dotenv import load_dotenv

import quote_of_the_day_config

from telegram_service.bot import TelegramNotifier

from LLMs.openRouter import OpenRouterLLM
from requests.exceptions import HTTPError, RequestException

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv(override=True)

OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
QOTD_BOT_TOKEN = os.getenv("QOTD_BOT_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))
WORDS_OF_THE_DAY_FILE = 'words_of_the_day.txt'

def extract_word_from_message(message: str) -> str:
    """
    Extracts the C-Level word from the message using regular expressions.

    The function looks for the text between "C-Level Word:" and "Definition:",
    then cleans up the result.

    Args:
        message (str): The message containing the C-Level Word section.

    Returns:
        str: The extracted C-Level word, without formatting, or an empty string if not found.
    """
    pattern = r"C-Level Word:(.*?)Definition:"
    
    match = re.search(pattern, message, re.DOTALL | re.IGNORECASE)
    
    if match:
        # The captured word is in group 1 of the match
        word = match.group(1)
        # Clean up whitespace and special characters like asterisks
        return re.sub(r'[^a-zA-Z]', '', word)
        
    return ""

def save_word_to_file(word: str, filename: str) -> None:
    """
    Appends a word to a specified file, adding a newline after it.
    If the file doesn't exist, it will be created.

    Args:
        word (str): The word to be saved to the file.
        filename (str): The name of the file (e.g., 'words.txt').
    """
    try:
        with open(filename, mode='a') as file:
            file.write(word + '\n')
    except IOError as e:
        logger.error(f"Error writing to file {filename}: {e}")

def get_learned_words(filename: str) -> str:
    """
    Reads words from a file and returns them as a single, space-separated string.

    Args:
        filename (str): The name of the file to read from.

    Returns:
        str: A single string containing all words from the file, separated
             by spaces. Returns an empty string if the file doesn't exist or is empty.
    """
    try:
        with open(filename, 'r') as file:
            content = file.read()
            words_as_string = content.replace('\n', ', ')

            return words_as_string

    except FileNotFoundError:
        return ""
    except IOError as e:
        logger.error(f"Error reading from file {filename}: {e}")
        return ""
    
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
    learned_words = get_learned_words(WORDS_OF_THE_DAY_FILE)

    # --- LLM Interaction ---
    logger.info("Generating LLM response...")
    topic = random.choice(quote_of_the_day_config.TOPICS)
    message = f"Quote of the day about {topic}, please. DO NOT repeat following words: {learned_words}"
    try:
        response, usage = chat_instance.conv(message)
    except HTTPError as e:
        logger.error(f"OpenRouter API error: {e}")
        return
    except RequestException as e:
        logger.error(f"Network error contacting OpenRouter: {e}")
        return
    logger.info("LLM response received.")

    final_message = (
        f"Topic: {topic}\n\n"
        f"{response}\n\n"
        f"LLM: {chat_instance.model_id}"
    )
    advanced_word = extract_word_from_message(final_message)
    if advanced_word != "":
        save_word_to_file(advanced_word, WORDS_OF_THE_DAY_FILE)

    # --- Send Notifications (within the same async context) ---
    logger.info("Sending notifications to Telegram...")
    # These two tasks will run sequentially.
    await notifier.send_message(msg=final_message, chat_id=TELEGRAM_USER_ID)
    logger.info("Notification sent.")


if __name__ == "__main__":
    # Run the entire async main function once.
    asyncio.run(main())
