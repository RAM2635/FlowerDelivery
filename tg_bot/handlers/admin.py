import sqlite3
from aiogram import Bot, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.statuses import translate_status
from services.database import update_order_status, is_admin
from services.database import is_admin
from tg_bot.keyboards.inline import admin_order_keyboard, back_to_admin_menu_keyboard


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
    user_id = callback_query.from_user.id

    # Проверяем, является ли пользователь администратором
    if is_admin(user_id):
        keyboard = InlineKeyboardMarkup(
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
        welcome_text = "Добро пожаловать в меню администратора!"
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Мои заказы", callback_data="my_orders"),
                    InlineKeyboardButton(text="Сделать заказ", callback_data="make_order"),
                ],
            ]
        )
        welcome_text = "Добро пожаловать в магазин!"

    await callback_query.message.edit_text(
        welcome_text,
        reply_markup=keyboard
    )


async def analytics_placeholder(callback_query: types.CallbackQuery):
    await callback_query.answer("Раздел аналитики находится в разработке.", show_alert=True)
