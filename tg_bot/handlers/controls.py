import os
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import sqlite3
from aiogram import Bot, types
from dotenv import load_dotenv
from tg_bot.keyboards.inline import back_button_keyboard, admin_main_menu_keyboard, user_main_menu_keyboard
from tg_bot.keyboards.inline import quantity_keyboard
from tg_bot.keyboards.inline import cart_actions_keyboard
from services.statuses import translate_status
from services.database import is_admin


# Локальное хранилище корзин пользователей
CART_STORAGE = {}

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")


# Обработчик: Просмотр заказов
async def show_orders(callback_query: types.CallbackQuery, bot: Bot):
    telegram_id = callback_query.from_user.id
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.date_created, o.status, GROUP_CONCAT(p.name || ' (x' || op.quantity || ')', ', ') 
            FROM delivery_order o
            JOIN delivery_orderproduct op ON o.id = op.order_id
            JOIN delivery_product p ON op.product_id = p.id
            WHERE o.user_id = (SELECT id FROM delivery_customuser WHERE telegram_id=?)
            GROUP BY o.id
            ORDER BY o.date_created DESC
        """, (telegram_id,))
        orders = cursor.fetchall()

    if orders:
        text = "Ваши заказы:\n\n"
        for order in orders:
            human_readable_status = translate_status(order[2])
            text += f"Заказ #{order[0]} от {order[1]}:\n- Товары: {order[3]}\n- Статус: {human_readable_status}\n\n"

    else:
        text = "У вас пока нет заказов."

    await callback_query.message.edit_text(text, reply_markup=back_button_keyboard())


# Локальное хранилище сообщений с кнопками
active_messages = {}


# Обработчик: Возврат в главное меню
async def back_to_main(callback_query: CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id

    # Проверяем, есть ли сообщения для пользователя
    if user_id in active_messages:
        updated_messages = []

        for message_info in active_messages[user_id]:
            if isinstance(message_info, int):
                message_info = {'message_id': message_info, 'keyboard_active': True}

            message_id = message_info['message_id']
            is_keyboard_active = message_info['keyboard_active']

            try:
                if is_keyboard_active:
                    await bot.edit_message_reply_markup(
                        chat_id=user_id,
                        message_id=message_id,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[])  # Отключаем кнопки
                    )
                    message_info['keyboard_active'] = False
                updated_messages.append(message_info)
            except TelegramBadRequest as e:
                if "message to edit not found" in str(e):
                    print(f"Сообщение {message_id} не найдено, пропускаем.")
                else:
                    print(f"Ошибка отключения клавиатуры для сообщения {message_id}: {e}")

        active_messages[user_id] = updated_messages

    # Проверяем, является ли пользователь администратором
    if is_admin(user_id):
        new_message = await bot.send_message(
            chat_id=user_id,
            text="Добро пожаловать в меню администратора!",
            reply_markup=admin_main_menu_keyboard()
        )
    else:
        new_message = await bot.send_message(
            chat_id=user_id,
            text="Добро пожаловать в магазин!",
            reply_markup=user_main_menu_keyboard()
        )

    add_active_message(user_id, new_message.message_id)


# Обработчик: Отключение неактивных кнопок
async def disabled_callback(callback_query: CallbackQuery):
    await callback_query.answer("Эта кнопка больше не активна.", show_alert=True)


# Обработчик: Добавление товара в корзину
async def add_to_cart_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data.split("_")

    # Проверка формата callback_data
    if len(data) < 4 or data[0] != "add" or data[1] != "to" or data[2] != "cart":
        await callback_query.answer("Некорректные данные callback!", show_alert=True)
        return

    try:
        product_id = int(data[3])  # Здесь должно быть product_id
        quantity = int(data[4])  # Здесь должно быть quantity
    except (ValueError, IndexError):
        await callback_query.answer("Ошибка данных!", show_alert=True)
        return

    # Получаем данные о товаре из базы данных
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, price FROM delivery_product WHERE id=?", (product_id,))
        product = cursor.fetchone()

    if not product:
        await callback_query.answer("Товар не найден!", show_alert=True)
        return

    product_name, price = product

    # Инициализация корзины для пользователя, если её нет
    if user_id not in CART_STORAGE:
        CART_STORAGE[user_id] = []

    # Проверяем, есть ли уже товар в корзине
    for item in CART_STORAGE[user_id]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity  # Увеличиваем на выбранное количество
            break
    else:
        CART_STORAGE[user_id].append({
            "product_id": product_id,
            "product_name": product_name,
            "price": price,
            "quantity": quantity  # Устанавливаем выбранное количество
        })

    await callback_query.answer(f"Товар '{product_name}' добавлен в корзину!")


async def view_cart(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    cart = CART_STORAGE.get(user_id, [])

    # Отключение inline-кнопок для всех предыдущих сообщений пользователя
    if user_id in active_messages:
        updated_messages = []

        for message_info in active_messages[user_id]:
            if isinstance(message_info, int):
                message_info = {'message_id': message_info, 'keyboard_active': True}

            message_id = message_info['message_id']
            is_keyboard_active = message_info['keyboard_active']

            try:
                if is_keyboard_active:
                    await callback_query.bot.edit_message_reply_markup(
                        chat_id=user_id,
                        message_id=message_id,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[])  # Отключаем кнопки
                    )
                    message_info['keyboard_active'] = False
                updated_messages.append(message_info)
            except TelegramBadRequest as e:
                if "message to edit not found" in str(e):
                    print(f"Сообщение {message_id} не найдено, пропускаем.")
                else:
                    print(f"Ошибка отключения клавиатуры для сообщения {message_id}: {e}")

        active_messages[user_id] = updated_messages

    # Удаляем старое сообщение корзины (если возможно)
    try:
        await callback_query.message.delete()
    except Exception as e:
        print(f"Ошибка удаления сообщения: {e}")

    # Если корзина пуста
    if not cart:
        try:
            new_message = await callback_query.message.answer(
                "Ваша корзина пуста.",
                reply_markup=cart_actions_keyboard()
            )
            # Добавляем сообщение в active_messages
            if user_id not in active_messages:
                active_messages[user_id] = []
            active_messages[user_id].append({'message_id': new_message.message_id, 'keyboard_active': True})
        except Exception as e:
            await callback_query.answer(f"Ошибка обновления корзины: {str(e)}", show_alert=True)
        return

    # Формируем текст корзины
    text = "Содержимое вашей корзины:\n\n"
    total = 0

    for item in cart:
        text += f"- {item['product_name']} (x{item['quantity']}) - {item['quantity'] * item['price']} руб.\n"
        total += item['quantity'] * item['price']

    text += f"\nОбщая сумма: {total} руб."

    # Отправляем новое сообщение с корзиной
    try:
        new_message = await callback_query.message.answer(
            text, reply_markup=cart_actions_keyboard(cart)
        )
        if user_id not in active_messages:
            active_messages[user_id] = []
        active_messages[user_id].append({'message_id': new_message.message_id, 'keyboard_active': True})
    except Exception as e:
        await callback_query.answer(f"Ошибка обновления корзины: {str(e)}", show_alert=True)

# Обработчик: Удаление товара из корзины
async def remove_item(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    product_id = int(callback_query.data.split("_")[2])

    cart = CART_STORAGE.get(user_id, [])
    CART_STORAGE[user_id] = [item for item in cart if item['product_id'] != product_id]

    await callback_query.answer("Товар удалён из корзины.")
    await view_cart(callback_query)  # view_cart уже добавляет сообщение в active_messages


# Обработчик: Подтверждение заказа
async def confirm_order(callback_query: types.CallbackQuery):
    print(f"Обработчик confirm_order вызван для пользователя {callback_query.from_user.id}")
    user_id = callback_query.from_user.id
    cart = CART_STORAGE.get(user_id, [])

    if not cart:
        await callback_query.message.edit_text("Ваша корзина пуста.",
                                               reply_markup=InlineKeyboardBuilder().row(
                                                   InlineKeyboardButton(text="Назад", callback_data="main_menu")
                                               ).as_markup())
        return

    CART_STORAGE[user_id] = []  # Очищаем корзину
    await callback_query.message.edit_text("Ваш заказ подтверждён! Спасибо за покупку.",
                                           reply_markup=InlineKeyboardBuilder().row(
                                               InlineKeyboardButton(text="Назад", callback_data="main_menu")
                                           ).as_markup())


def add_active_message(user_id, message_id):
    if user_id not in active_messages:
        active_messages[user_id] = []
    active_messages[user_id].append({'message_id': message_id, 'keyboard_active': True})


# Удаление устаревших сообщений из active_messages
def remove_inactive_messages(user_id):
    if user_id in active_messages:
        active_messages[user_id] = [msg for msg in active_messages[user_id] if msg.get('keyboard_active', False)]


# Проверка актуальности сообщения
async def check_message_validity(callback_query: CallbackQuery) -> bool:
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id

    # Лог для отладки
    print(f"Проверка валидности сообщения: {message_id} для пользователя {user_id}")

    # Проверяем наличие активных сообщений для пользователя
    if user_id not in active_messages or not any(
            isinstance(msg, dict) and msg.get('message_id') == message_id
            for msg in active_messages[user_id]
    ):
        print(f"Сообщение {message_id} устарело для пользователя {user_id}")

        # Обновляем текст для пользователя, если сообщение устарело
        await callback_query.message.edit_text(
            "Сообщение устарело. Пожалуйста, обновите экран.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="main_menu")]]
            )
        )
        return False

    print(f"Сообщение {message_id} актуально для пользователя {user_id}")
    return True


# Обработчик увеличения количества товара
async def increase_quantity(callback_query: CallbackQuery):
    if not await check_message_validity(callback_query):
        return

    try:
        data = callback_query.data.split("_")
        product_id = int(data[2])
        quantity = int(data[3])

        quantity += 1

        await callback_query.message.edit_reply_markup(
            reply_markup=quantity_keyboard(product_id, quantity)
        )
        await callback_query.answer()
    except Exception as e:
        await callback_query.answer(f"Ошибка: {str(e)}", show_alert=True)


# Обработчик уменьшения количества товара
async def decrease_quantity(callback_query: CallbackQuery):
    if not await check_message_validity(callback_query):
        return

    try:
        data = callback_query.data.split("_")
        product_id = int(data[2])
        quantity = int(data[3])

        if quantity > 1:
            quantity -= 1

        await callback_query.message.edit_reply_markup(
            reply_markup=quantity_keyboard(product_id, quantity)
        )
        await callback_query.answer()
    except Exception as e:
        await callback_query.answer(f"Ошибка: {str(e)}", show_alert=True)
