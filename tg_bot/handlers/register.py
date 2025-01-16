from aiogram import F
from functools import partial
from tg_bot.handlers.admin import (
    list_admin_orders,
    handle_order_update,
    analytics_placeholder,
    back_to_admin_menu,
    analytics_statuses,
    analytics_users,
    analytics_products,
    analytics_dates,
    back_to_analytics_menu
)
from tg_bot.handlers.controls import (
    show_orders,
    back_to_main,
    increase_quantity,
    decrease_quantity,
    disabled_callback,
    add_to_cart_callback,
    view_cart,
    remove_item,
    confirm_order
)
from tg_bot.handlers.start import register_handlers as register_start_handlers


def register_all_handlers(dp, bot, database_path):
    """
    Регистрирует все обработчики бота
    """
    register_controls_handlers(dp, bot)
    register_start_handlers(dp)
    register_admin_handlers(dp, bot, database_path)


def register_controls_handlers(dp, bot):
    dp.callback_query.register(partial(show_orders, bot=bot), F.data == "my_orders")
    dp.callback_query.register(partial(back_to_main, bot=bot), F.data == "main_menu")
    dp.callback_query.register(increase_quantity, lambda c: c.data.startswith("increase_quantity_"))
    dp.callback_query.register(decrease_quantity, lambda c: c.data.startswith("decrease_quantity_"))
    dp.callback_query.register(disabled_callback, F.data == "disabled")
    dp.callback_query.register(add_to_cart_callback, lambda c: c.data.startswith("add_to_cart_"))
    dp.callback_query.register(view_cart, F.data == "view_cart")
    dp.callback_query.register(remove_item, lambda c: c.data.startswith("remove_item_"))
    dp.callback_query.register(confirm_order, F.data == "confirm_order")


def register_admin_handlers(dp, bot, database_path):
    dp.message.register(partial(list_admin_orders, bot=bot, database_path=database_path), F.text == "/admin_orders")
    dp.callback_query.register(partial(list_admin_orders, bot=bot, database_path=database_path),
                               F.data == "admin_orders")
    dp.callback_query.register(partial(handle_order_update, bot=bot, database_path=database_path),
                               F.data.startswith("update_order_"))
    dp.callback_query.register(analytics_placeholder, F.data == "analytics_placeholder")
    dp.callback_query.register(partial(back_to_admin_menu, bot=bot), F.data == "back_to_admin_menu")
    # Регистрация обработчиков для аналитики
    dp.callback_query.register(partial(analytics_statuses, database_path=database_path), F.data == "analytics_statuses")
    dp.callback_query.register(partial(analytics_users, database_path=database_path), F.data == "analytics_users")
    dp.callback_query.register(partial(analytics_products, database_path=database_path), F.data == "analytics_products")
    dp.callback_query.register(partial(analytics_dates, database_path=database_path), F.data == "analytics_dates")
    dp.callback_query.register(back_to_analytics_menu, F.data == "back_to_analytics_menu")
