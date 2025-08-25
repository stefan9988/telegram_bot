# tests/test_telegram_notifier.py
import asyncio
import pytest

from telegram_service import bot as bot_module


def test_telegram_notifier_requires_token():
    with pytest.raises(ValueError):
        bot_module.TelegramNotifier(token="")


class DummyBotSendOnly:
    def __init__(self, token):
        self.token = token
        self.sent_messages = []

    async def send_message(self, chat_id, text):
        self.sent_messages.append((chat_id, text))


def test_send_message(monkeypatch):
    dummy = DummyBotSendOnly("token")
    monkeypatch.setattr(bot_module, "Bot", lambda token: dummy)
    notifier = bot_module.TelegramNotifier("token")
    asyncio.run(notifier.send_message("hello", chat_id=123))
    assert dummy.sent_messages == [(123, "hello")]


# -------- New tests for get_updates --------

class DummyBotGetUpdatesOK:
    def __init__(self, token):
        self.token = token
        self.called = False

    async def get_updates(self):
        self.called = True
        # Return a realistic minimal shape (list of anything)
        return [{"update_id": 1, "message": {"text": "hi"}}]


def test_get_updates_success(monkeypatch):
    dummy = DummyBotGetUpdatesOK("token")
    monkeypatch.setattr(bot_module, "Bot", lambda token: dummy)

    notifier = bot_module.TelegramNotifier("token")
    updates = asyncio.run(notifier.get_updates())

    assert dummy.called is True
    assert isinstance(updates, list)
    assert updates and updates[0].get("update_id") == 1


class DummyBotGetUpdatesTelegramError:
    def __init__(self, token):
        self.token = token

    async def get_updates(self):
        # Raise whatever bot_module.TelegramError is (we monkeypatch it below)
        raise bot_module.TelegramError("boom")


def test_get_updates_telegram_error_returns_empty_list(monkeypatch):
    # Ensure TelegramError exists and is what we expect to raise
    class FakeTelegramError(Exception):
        pass

    monkeypatch.setattr(bot_module, "TelegramError", FakeTelegramError)
    monkeypatch.setattr(bot_module, "Bot", lambda token: DummyBotGetUpdatesTelegramError(token))

    notifier = bot_module.TelegramNotifier("token")
    updates = asyncio.run(notifier.get_updates())

    assert updates == []  # graceful fallback on TelegramError


class DummyBotGetUpdatesGenericError:
    def __init__(self, token):
        self.token = token

    async def get_updates(self):
        raise RuntimeError("unexpected crash")


def test_get_updates_generic_exception_returns_empty_list(monkeypatch):
    monkeypatch.setattr(bot_module, "Bot", lambda token: DummyBotGetUpdatesGenericError(token))

    notifier = bot_module.TelegramNotifier("token")
    updates = asyncio.run(notifier.get_updates())

    assert updates == []  # graceful fallback on generic Exception
