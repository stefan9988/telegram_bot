import asyncio
from telegram import Bot
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

async def send_telegram_message(msg, bot_token, user_id):
    bot = Bot(token=bot_token)

    try:
        await bot.send_message(
            chat_id=user_id,
            text= msg
        )
        print("Message sent successfully!")
    except Exception as e:
        print(f"Error sending message: {e}")

async def send_telegram_photo(image_path: str, caption: str, bot_token: str, user_id: int):
    """Sends a photo to a specified Telegram user."""
    bot = Bot(token=bot_token)
    try:
        with open(image_path, 'rb') as photo_file:
            await bot.send_photo(
                chat_id=user_id,
                photo=photo_file,
                caption=caption
            )
        print("Photo sent successfully!")
    except FileNotFoundError:
        print(f"Error: The file at {image_path} was not found.")
    except Exception as e:
        print(f"Error sending photo: {e}")

if __name__ == "__main__":
    asyncio.run(send_telegram_message('HI', BOT_TOKEN, TELEGRAM_USER_ID))
    asyncio.run(send_telegram_photo("data/crypto_indicators.png", "Crypto Indicators", BOT_TOKEN, TELEGRAM_USER_ID))