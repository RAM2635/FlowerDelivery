import pytest
from functools import partial
from unittest.mock import AsyncMock
from aiogram import Dispatcher
from tg_bot.handlers.register import (
    register_start_handlers,
    register_controls_handlers,
    register_admin_handlers
)
from tg_bot.handlers.start import (
    start_handler, exit_handler, handle_name, handle_email
)
from tg_bot.handlers.controls import (
    view_cart, add_to_cart_callback, remove_item, confirm_order
)
from tg_bot.handlers.admin import (
    list_admin_orders, analytics_statuses, analytics_users
)


@pytest.mark.asyncio
async def test_register_start_handlers():
    dp = Dispatcher()
    register_start_handlers(dp)

    # Проверяем регистрацию команды /start
    assert any(handler.callback == start_handler for handler in dp.message.handlers)

    # Проверяем регистрацию команды /exit
    assert any(handler.callback == exit_handler for handler in dp.message.handlers)

    # Проверяем регистрацию состояния waiting_for_name
    assert any(handler.callback == handle_name for handler in dp.message.handlers)

    # Проверяем регистрацию состояния waiting_for_email
    assert any(handler.callback == handle_email for handler in dp.message.handlers)


@pytest.mark.asyncio
async def test_register_controls_handlers():
    dp = Dispatcher()
    bot = AsyncMock()  # Замокированный бот
    register_controls_handlers(dp, bot)  # Передаём bot как аргумент

    # Проверяем регистрацию callback для просмотра корзины
    assert any(handler.callback == view_cart for handler in dp.callback_query.handlers)

    # Проверяем регистрацию callback для добавления в корзину
    assert any(handler.callback == add_to_cart_callback for handler in dp.callback_query.handlers)

    # Проверяем регистрацию callback для удаления из корзины
    assert any(handler.callback == remove_item for handler in dp.callback_query.handlers)

    # Проверяем регистрацию callback для подтверждения заказа
    assert any(handler.callback == confirm_order for handler in dp.callback_query.handlers)


@pytest.mark.asyncio
async def test_register_admin_handlers():
    dp = Dispatcher()
    bot = AsyncMock()  # Замокированный бот
    database_path = "test_database.db"  # Тестовый путь к базе данных
    register_admin_handlers(dp, bot, database_path)  # Передаём bot и database_path

    # Проверяем регистрацию команды на просмотр заказов администратором
    assert any(
        isinstance(handler.callback, partial) and handler.callback.func == list_admin_orders
        for handler in dp.message.handlers
    )

    # Проверяем регистрацию callback для аналитики статусов
    assert any(
        isinstance(handler.callback, partial) and handler.callback.func == analytics_statuses
        for handler in dp.callback_query.handlers
    )

    # Проверяем регистрацию callback для аналитики пользователей
    assert any(
        isinstance(handler.callback, partial) and handler.callback.func == analytics_users
        for handler in dp.callback_query.handlers
    )
