from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard():
    """
    Клавиатура главного меню.
    """
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Мои заказы", callback_data="my_orders"),
        InlineKeyboardButton(text="Сделать заказ", callback_data="make_order"),
    ).as_markup()


def back_button_keyboard():
    """
    Клавиатура с кнопкой "Назад".
    """
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text="Назад", callback_data="main_menu")
    ).as_markup()


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

def cart_actions_keyboard(cart=None):
    """
    Клавиатура для управления корзиной.
    """
    keyboard = InlineKeyboardBuilder()

    if cart:
        for item in cart:
            keyboard.row(
                InlineKeyboardButton(
                    text=f"Удалить {item['product_name']}",
                    callback_data=f"remove_item_{item['product_id']}"
                )
            )

    keyboard.row(
        InlineKeyboardButton(text="Подтвердить заказ", callback_data="start_delivery_process"),
        InlineKeyboardButton(text="Назад", callback_data="main_menu")
    )

    return keyboard.as_markup()


def admin_order_keyboard(order_id):
    """
    Клавиатура для управления статусом заказа.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="В обработку", callback_data=f"update_order_{order_id}_processing"),
                InlineKeyboardButton(text="Завершён", callback_data=f"update_order_{order_id}_completed"),
                InlineKeyboardButton(text="Отменён", callback_data=f"update_order_{order_id}_cancelled"),
            ]
        ]
    )

def back_to_admin_menu_keyboard():
    """
    Клавиатура с кнопкой "Назад" для возврата в меню администратора.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back_to_admin_menu")]]
    )


def user_main_menu_keyboard():
    """
    Клавиатура для обычного пользователя.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Мои заказы", callback_data="my_orders"),
                InlineKeyboardButton(text="Сделать заказ", callback_data="make_order"),
            ],
        ]
    )


def admin_main_menu_keyboard():
    """
    Клавиатура для администратора.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Мои заказы", callback_data="my_orders"),
                InlineKeyboardButton(text="Сделать заказ", callback_data="make_order"),
            ],
            [
                InlineKeyboardButton(text="Статус", callback_data="admin_orders"),
                InlineKeyboardButton(text="Аналитика", callback_data="analytics_placeholder"),
            ],
        ]
    )
