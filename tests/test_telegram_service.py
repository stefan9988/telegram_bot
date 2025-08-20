import asyncio
import pytest

from telegram_service import bot as bot_module


def test_telegram_notifier_requires_token():
    with pytest.raises(ValueError):
        bot_module.TelegramNotifier(token="")


class DummyBot:
    def __init__(self, token):
        self.token = token
        self.sent_messages = []

    async def send_message(self, chat_id, text):
        self.sent_messages.append((chat_id, text))


def test_send_message(monkeypatch):
    dummy = DummyBot("token")
    monkeypatch.setattr(bot_module, "Bot", lambda token: dummy)
    notifier = bot_module.TelegramNotifier("token")
    asyncio.run(notifier.send_message("hello", chat_id=123))
    assert dummy.sent_messages == [(123, "hello")]
