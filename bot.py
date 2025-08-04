import asyncio
from telegram import Bot
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
YOUR_USER_ID = int(os.getenv("YOUR_USER_ID", "0"))

async def send_message_and_exit(msg):
    bot = Bot(token=BOT_TOKEN)
    
    try:
        await bot.send_message(
            chat_id=YOUR_USER_ID,
            text= msg
        )
        print("Message sent successfully!")
    except Exception as e:
        print(f"Error sending message: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(send_message_and_exit('HI'))