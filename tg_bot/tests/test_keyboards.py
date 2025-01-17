import pytest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from tg_bot.keyboards.inline import (
    main_menu_keyboard,
    back_button_keyboard,
    product_keyboard,
    cart_keyboard,
    quantity_keyboard,
    disable_keyboard,
    cart_actions_keyboard,
    admin_order_keyboard,
    back_to_admin_menu_keyboard,
    user_main_menu_keyboard,
    admin_main_menu_keyboard,
    dynamic_main_menu_keyboard,
    analytics_menu_keyboard,
    analytics_back_keyboard,
)


def test_main_menu_keyboard():
    keyboard = main_menu_keyboard()
    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 1
    assert len(keyboard.inline_keyboard[0]) == 2


def test_back_button_keyboard():
    keyboard = back_button_keyboard()
    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 1
    assert len(keyboard.inline_keyboard[0]) == 1


def test_product_keyboard():
    keyboard = product_keyboard(123)
    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 1
    assert keyboard.inline_keyboard[0][0].callback_data == "add_to_cart_123"
