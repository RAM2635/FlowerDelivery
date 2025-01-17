import sqlite3
from aiogram import Bot, types
from tg_bot.services.statuses import translate_status
from tg_bot.services.database import update_order_status, is_admin
from tg_bot.keyboards.inline import (
    admin_order_keyboard,
    user_main_menu_keyboard,
    analytics_menu_keyboard,
    back_to_admin_menu_keyboard,
    analytics_back_keyboard,
    admin_main_menu_keyboard,
)


async def list_admin_orders(callback_query: types.CallbackQuery, bot: Bot, database_path: str):
    admin_telegram_id = callback_query.from_user.id

    # Проверяем права администратора
    if not is_admin(admin_telegram_id):
        await callback_query.answer("У вас нет прав администратора.")
        return

    # Получаем список заказов из базы данных
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT o.id, o.status, o.date_created, c.username FROM delivery_order o "
            "JOIN delivery_customuser c ON o.user_id = c.id "
            "ORDER BY o.date_created DESC"
        )
        orders = cursor.fetchall()

    # Если заказов нет
    if not orders:
        await callback_query.message.edit_text("Нет доступных заказов.")
        return

    # Формируем список заказов
    for order in orders:
        order_id, status, date_created, username = order
        translated_status = translate_status(status)
        buttons = admin_order_keyboard(order_id)

        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=(
                f"Заказ #{order_id}\n"
                f"Статус: {translated_status}\n"
                f"Дата: {date_created}\n"
                f"Пользователь: {username}"
            ),
            reply_markup=buttons
        )

    # Добавляем кнопку "Назад" после вывода заказов
    back_button = back_to_admin_menu_keyboard()

    await bot.send_message(callback_query.from_user.id, "Выберите действие:", reply_markup=back_button)


async def handle_order_update(callback_query: types.CallbackQuery, bot: Bot, database_path: str):
    admin_telegram_id = callback_query.from_user.id

    # Извлекаем ID заказа и новый статус из callback_data
    data = callback_query.data.split("_")
    order_id = int(data[2])
    new_status = data[3]

    try:
        # Обновляем статус заказа
        user_telegram_id = update_order_status(order_id, new_status, admin_telegram_id, database_path)

        if user_telegram_id:
            # Переводим статус на понятный язык
            translated_status = translate_status(new_status)

            # Отправляем уведомление пользователю
            await bot.send_message(
                chat_id=user_telegram_id,
                text=f"Ваш заказ #{order_id} теперь имеет статус: {translated_status}."
            )
            await callback_query.answer("Статус заказа обновлён.")
        else:
            await callback_query.answer("Пользователь для уведомления не найден.")
    except PermissionError:
        await callback_query.answer("У вас нет прав для выполнения этой операции.")


async def back_to_admin_menu(callback_query: types.CallbackQuery, bot: Bot):
    """
    Обработчик для возврата в главное меню администратора.
    """
    user_id = callback_query.from_user.id
    if is_admin(user_id):
        welcome_text = "Добро пожаловать в меню администратора!"
        keyboard = admin_main_menu_keyboard()
    else:
        welcome_text = "Добро пожаловать в магазин!"
        keyboard = user_main_menu_keyboard()  # Используем уже готовую клавиатуру для обычного пользователя.

    await callback_query.message.edit_text(
        welcome_text,
        reply_markup=keyboard
    )


async def analytics_placeholder(callback_query: types.CallbackQuery):
    """
    Обработчик кнопки "Аналитика".
    """
    # Отправляем меню аналитики
    await callback_query.message.edit_text(
        "Выберите интересующий вас отчёт:",
        reply_markup=analytics_menu_keyboard()
    )


async def analytics_statuses(callback_query: types.CallbackQuery, database_path=None):
    """
    Распределение заказов по статусам.
    """
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM delivery_order GROUP BY status;")
        results = cursor.fetchall()

    text = "Распределение заказов по статусам:\n"
    for status, count in results:
        text += f"- {status}: {count}\n"

    await callback_query.message.edit_text(text, reply_markup=analytics_back_keyboard())


async def analytics_users(callback_query: types.CallbackQuery, database_path=None):
    """
    Распределение заказов по пользователям.
    """
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.username, COUNT(*) 
            FROM delivery_order o
            JOIN delivery_customuser c ON o.user_id = c.id
            GROUP BY c.username;
        """)
        results = cursor.fetchall()

    text = "Распределение заказов по пользователям:\n"
    for user, count in results:
        text += f"- {user}: {count}\n"

    await callback_query.message.edit_text(text, reply_markup=analytics_back_keyboard())


async def analytics_products(callback_query: types.CallbackQuery, database_path=None):
    """
    Популярные продукты.
    """
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, COUNT(*)
            FROM delivery_orderproduct op
            JOIN delivery_product p ON op.product_id = p.id
            GROUP BY p.name
            ORDER BY COUNT(*) DESC;
        """)
        results = cursor.fetchall()

    text = "Популярные продукты:\n"
    for product, count in results:
        text += f"- {product}: {count}\n"

    await callback_query.message.edit_text(text, reply_markup=analytics_back_keyboard())


async def analytics_dates(callback_query: types.CallbackQuery, database_path=None):
    """
    Распределение заказов по датам.
    """
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT date_created, COUNT(*) FROM delivery_order GROUP BY date_created;")
        results = cursor.fetchall()

    text = "Распределение заказов по датам:\n"
    for date, count in results:
        text += f"- {date}: {count}\n"

    await callback_query.message.edit_text(text, reply_markup=analytics_back_keyboard())


async def back_to_analytics_menu(callback_query: types.CallbackQuery):
    """
    Обработчик для возврата в меню аналитики.
    """
    new_text = "Выберите интересующий вас отчёт:"
    new_markup = analytics_menu_keyboard()

    # Проверяем, нужно ли обновлять текст или клавиатуру
    if callback_query.message.text != new_text:
        await callback_query.message.edit_text(
            new_text,
            reply_markup=new_markup
        )
    elif callback_query.message.reply_markup != new_markup:
        await callback_query.message.edit_reply_markup(
            reply_markup=new_markup
        )
    else:
        # Если ничего не изменилось, просто ответить на callback
        await callback_query.answer("Вы уже в меню аналитики.")


