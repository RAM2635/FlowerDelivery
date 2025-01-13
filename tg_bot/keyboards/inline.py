from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def product_keyboard(product_id):
    """
    Клавиатура для добавления товара в корзину.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_to_cart_{product_id}")]
        ]
    )


def cart_keyboard():
    """
    Клавиатура для просмотра корзины и возврата в главное меню.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Посмотреть корзину", callback_data="view_cart")],
            [InlineKeyboardButton(text="Назад", callback_data="main_menu")]
        ]
    )



def quantity_keyboard(product_id, quantity):
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="-", callback_data=f"decrease_quantity_{product_id}_{quantity}"),
        InlineKeyboardButton(text=str(quantity), callback_data="current_quantity"),
        InlineKeyboardButton(text="+", callback_data=f"increase_quantity_{product_id}_{quantity}"),
    ).row(
        InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_to_cart_{product_id}_{quantity}")
    ).as_markup()



def disable_keyboard(keyboard: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    """
    Создаёт версию клавиатуры с отключёнными кнопками.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=button.text, callback_data="disabled") for button in row]
            for row in keyboard.inline_keyboard
        ]
    )
