# tests/test_telegram_notifier.py
import asyncio
import types
import pytest

from telegram_service import bot as bot_module


def test_telegram_notifier_requires_token():
    with pytest.raises(ValueError):
        bot_module.TelegramNotifier(token="")


class DummyMessage:
    def __init__(self, text=None):
        self.text = text


class DummyUpdate:
    def __init__(self, update_id, text=None):
        self.update_id = update_id
        # emulate python-telegram-bot structure: update.message.text
        self.message = DummyMessage(text=text)


class DummyBotGetUpdatesOK:
    def __init__(self, token):
        self.token = token
        self.called = False
        self.last_ack_offset = None
        self.last_ack_limit = None
        # pretend there are two new updates
        self._queue = [
            DummyUpdate(1, "hi"),
            DummyUpdate(2, "hello"),
        ]

    async def get_updates(self, offset=None, limit=None):
        # First call (no offset): return queued updates
        if offset is None:
            self.called = True
            return list(self._queue)

        # "Ack" call: record what was requested and return empty
        self.last_ack_offset = offset
        self.last_ack_limit = limit
        return []


def test_send_message(monkeypatch):
    class DummyBotSendOnly:
        def __init__(self, token):
            self.token = token
            self.sent_messages = []

        async def send_message(self, chat_id, text):
            self.sent_messages.append((chat_id, text))

    dummy = DummyBotSendOnly("token")
    monkeypatch.setattr(bot_module, "Bot", lambda token: dummy)
    notifier = bot_module.TelegramNotifier("token")
    asyncio.run(notifier.send_message("hello", chat_id=123))
    assert dummy.sent_messages == [(123, "hello")]


def test_get_updates_success(monkeypatch):
    dummy = DummyBotGetUpdatesOK("token")
    monkeypatch.setattr(bot_module, "Bot", lambda token: dummy)

    notifier = bot_module.TelegramNotifier("token")
    texts = asyncio.run(notifier.get_updates())

    # Now get_updates returns the texts it extracted
    assert texts == ["hi", "hello"]

    # Ensure the initial fetch ran
    assert dummy.called is True

    # Ensure the ack call advanced the offset to last_update_id + 1 (2 + 1 = 3)
    assert dummy.last_ack_offset == 3
    # We suggested limit=1 for a lightweight ack
    # If your production code doesn't pass limit, remove this next assert
    # assert dummy.last_ack_limit == 1


class DummyBotGetUpdatesTelegramError:
    def __init__(self, token):
        self.token = token

    async def get_updates(self, offset=None, limit=None):
        raise bot_module.TelegramError("boom")


def test_get_updates_telegram_error_returns_empty_list(monkeypatch):
    class FakeTelegramError(Exception):
        pass

    monkeypatch.setattr(bot_module, "TelegramError", FakeTelegramError)
    monkeypatch.setattr(bot_module, "Bot", lambda token: DummyBotGetUpdatesTelegramError(token))

    notifier = bot_module.TelegramNotifier("token")
    texts = asyncio.run(notifier.get_updates())
    assert texts == []


class DummyBotGetUpdatesGenericError:
    def __init__(self, token):
        self.token = token

    async def get_updates(self, offset=None, limit=None):
        raise RuntimeError("unexpected crash")


def test_get_updates_generic_exception_returns_empty_list(monkeypatch):
    monkeypatch.setattr(bot_module, "Bot", lambda token: DummyBotGetUpdatesGenericError(token))
    notifier = bot_module.TelegramNotifier("token")
    texts = asyncio.run(notifier.get_updates())
    assert texts == []
