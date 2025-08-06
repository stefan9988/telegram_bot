from telegram import Bot
from telegram.error import TelegramError

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
            print(f"Error sending message: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

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
            print(f"Error: The file at {image_path} was not found.")
        except TelegramError as e:
            print(f"Error sending photo: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")







