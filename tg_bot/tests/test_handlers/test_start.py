import pytest
from aiogram import types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from datetime import datetime
from unittest.mock import AsyncMock
from tg_bot.handlers.start import start_handler, exit_handler



@pytest.mark.asyncio
async def test_start_handler_admin(mocker):
    # Мокаем функции базы данных
    mocker.patch("tg_bot.handlers.start.is_admin", return_value=True)
    mocker.patch(
        "tg_bot.handlers.start.get_user_by_telegram_id",
        return_value={"id": 1, "username": "admin", "email": "admin@example.com"}
    )

    message = types.Message(
        message_id=1,
        date=datetime.now(),
        chat=types.Chat(id=123, type="private"),
        from_user=types.User(id=123, is_bot=False, first_name="Test Admin")
    )
    state = FSMContext(storage=MemoryStorage(), key=("chat", 123))

    bot = AsyncMock()  # Используем AsyncMock для корректной работы с await
    await start_handler(message.as_(bot), state)
    bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_start_handler_user(mocker):
    # Мокаем функции базы данных
    mocker.patch("tg_bot.handlers.start.is_admin", return_value=False)
    mocker.patch(
        "tg_bot.handlers.start.get_user_by_telegram_id",
        return_value={"id": 2, "username": "user", "email": "user@example.com"}
    )

    message = types.Message(
        message_id=2,
        date=datetime.now(),
        chat=types.Chat(id=124, type="private"),
        from_user=types.User(id=124, is_bot=False, first_name="Test User")
    )
    state = FSMContext(storage=MemoryStorage(), key=("chat", 124))

    bot = AsyncMock()  # Используем AsyncMock
    await start_handler(message.as_(bot), state)
    bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_exit_handler(mocker):
    bot = AsyncMock()  # Используем AsyncMock для мокирования бота
    message = types.Message(
        message_id=3,
        date=datetime.now(),
        chat=types.Chat(id=125, type="private"),
        from_user=types.User(id=125, is_bot=False, first_name="Test User")
    )
    state = FSMContext(storage=MemoryStorage(), key=("chat", 125))

    await exit_handler(message.as_(bot), state)
    bot.send_message.assert_not_called()
