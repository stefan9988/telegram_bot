from telegram import Bot
from telegram.error import TelegramError
import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class TelegramNotifier:
    """
    A class to handle sending messages and photos via a Telegram Bot.
    """
    def __init__(self, token: str):
        if not token:
            raise ValueError("Bot token cannot be empty.")
            
        self.bot = Bot(token=token)

    async def send_message(self, msg: str, chat_id: int):
        """Sends a text message to the specified Telegram user."""
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=msg
            )            
        except TelegramError as e:
            logger.error(f"Error sending message: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

    async def send_photo(self, image_path: str, caption: str, chat_id: int):
        """Sends a photo to the specified Telegram user."""
        try:
            with open(image_path, 'rb') as photo_file:
                await self.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_file,
                    caption=caption
                )
        except FileNotFoundError:
            logger.error(f"Error: The file at {image_path} was not found.")
        except TelegramError as e:
            logger.error(f"Error sending photo: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

    async def get_updates(self):
        """Fetches updates, returns their texts, then acknowledges them on Telegram."""
        try:
            updates = await self.bot.get_updates()
            texts = [u.message.text for u in updates if getattr(u, "message", None) and u.message.text]

            # Acknowledge: mark everything up to the newest update as "confirmed"
            if updates:
                last_id = updates[-1].update_id
                # We don't care about the response; this call tells Telegram to skip old updates next time
                try:
                    await self.bot.get_updates(offset=last_id + 1, limit=1)
                except TelegramError as ack_err:
                    # Not fatal: worst case you'll see duplicates next run
                    logger.warning(f"Ack failed (will retry next time): {ack_err}")

            return texts

        except TelegramError as e:
            logger.error(f"Error fetching updates: {e}")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return []

