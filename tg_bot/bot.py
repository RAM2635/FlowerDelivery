import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import sqlite3
from os import getenv
from dotenv import load_dotenv
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from handlers.start import register_handlers
from handlers.controls import register_handlers as register_controls_handlers, check_message_validity, \
    add_active_message, remove_inactive_messages, CART_STORAGE
from keyboards.inline import product_keyboard, cart_keyboard, quantity_keyboard
from datetime import datetime

# Загрузка переменных окружения
load_dotenv(".env")

BOT_TOKEN = getenv("BOT_TOKEN")
DATABASE_PATH = os.getenv("DATABASE_PATH")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрируем обработчики
register_handlers(dp)
register_controls_handlers(dp, bot)

# Хранилище для отслеживания активных сообщений пользователей
active_messages = {}


# Состояния FSM для регистрации
class RegistrationState(StatesGroup):
    waiting_for_name = State()
    waiting_for_email = State()

    # Состояния FSM для оформления заказа


@dp.callback_query(F.data == "make_order")
async def make_order(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    # Убедимся, что active_messages инициализирован для пользователя
    if user_id not in active_messages:
        active_messages[user_id] = []

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, image FROM delivery_product")
        products = cursor.fetchall()

    if products:
        await callback_query.message.delete()
        for product in products:
            product_id, name, price, image_path = product
            file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../shop_project/media", image_path))

            if os.path.exists(file_path):
                photo = FSInputFile(file_path)
                new_message = await bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=f"{name}\nЦена: {price} руб.",
                    reply_markup=quantity_keyboard(product_id, 1)
                )
                add_active_message(user_id, new_message.message_id)  # Добавляем новое сообщение в active_messages

        # Добавляем сообщение с действиями
        actions_message = await bot.send_message(
            user_id, "Доступные действия:", reply_markup=cart_keyboard()
        )
        add_active_message(user_id, actions_message.message_id)
    else:
        await callback_query.message.edit_text(
            "В магазине пока нет доступных товаров.",
            reply_markup=cart_keyboard()
        )


@dp.callback_query(F.data.startswith("product_"))
async def choose_product(callback_query: CallbackQuery):
    product_id = int(callback_query.data.split("_")[1])

    # Отправляем клавиатуру выбора количества
    await callback_query.message.answer(
        "Выберите количество:",
        reply_markup=quantity_keyboard(product_id, 1)
    )


@dp.callback_query(F.data.startswith("confirm_quantity_"))
async def confirm_quantity(callback_query: CallbackQuery):
    # Проверяем актуальность сообщения
    if not await check_message_validity(callback_query):
        return

    data = callback_query.data.split("_")
    product_id = int(data[2])
    quantity = int(data[3])

    # Получение названия товара из базы данных
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM delivery_product WHERE id=?", (product_id,))
        product_name = cursor.fetchone()
        product_name = product_name[0] if product_name else "Неизвестный товар"

    # Отправка сообщения с подтверждением
    await callback_query.message.answer(
        f"Вы выбрали товар '{product_name}' в количестве {quantity}.\nВведите данные доставки."
    )


# Состояния FSM для оформления заказа
class OrderState(StatesGroup):
    waiting_for_address = State()
    waiting_for_phone = State()
    waiting_for_name = State()
    order_complete = State()


@dp.callback_query(F.data == "start_delivery_process")
async def start_delivery_process(callback_query: types.CallbackQuery, state: FSMContext):
    print(f"Обработчик start_delivery_process вызван для пользователя {callback_query.from_user.id}")
    await callback_query.message.edit_text(
        "\U0001F4E6 Введите адрес доставки:",
    )
    await state.set_state(OrderState.waiting_for_address)
    print("FSM: State set to waiting_for_address")


@dp.message(OrderState.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Введите номер телефона:")
    await state.set_state(OrderState.waiting_for_phone)
    print(f"Адрес сохранён: {message.text}")


@dp.message(OrderState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Введите имя получателя:")
    await state.set_state(OrderState.waiting_for_name)
    print(f"Телефон сохранён: {message.text}")


@dp.message(OrderState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    telegram_id = message.from_user.id
    address = user_data.get("address")
    phone = user_data.get("phone")
    recipient_name = message.text

    # Получение user_id из таблицы delivery_customuser
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM delivery_customuser WHERE telegram_id = ?",
            (telegram_id,)
        )
        result = cursor.fetchone()
        if result is None:
            await message.answer("Ошибка: пользователь не найден в базе данных.")
            return

        user_id = result[0]

        # Добавляем заказ с текущей датой
        date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO delivery_order (user_id, address, phone, recipient_name, status, date_created) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, address, phone, recipient_name, "pending", date_created)
        )
        order_id = cursor.lastrowid

        # Добавляем товары заказа
        cart = CART_STORAGE.get(telegram_id, [])
        for item in cart:
            cursor.execute(
                "INSERT INTO delivery_orderproduct (order_id, product_id, quantity) VALUES (?, ?, ?)",
                (order_id, item["product_id"], item["quantity"])
            )

        conn.commit()

    # Очищаем корзину
    CART_STORAGE[telegram_id] = []

    await message.answer(
        f"Ваш заказ подтверждён!\n\nАдрес: {address}\nТелефон: {phone}\nПолучатель: {recipient_name}\n\nСпасибо за покупку.",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Мои заказы", callback_data="my_orders")],
                [types.InlineKeyboardButton(text="Сделать заказ", callback_data="make_order")]
            ]
        )
    )
    await state.clear()
    print("Состояние очищено.")


@dp.callback_query(F.data == "my_orders")
async def view_orders(callback_query: types.CallbackQuery):
    telegram_id = callback_query.from_user.id

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM delivery_customuser WHERE telegram_id = ?",
            (telegram_id,)
        )
        result = cursor.fetchone()
        if result is None:
            await callback_query.message.edit_text("Ошибка: пользователь не найден в базе данных.")
            return

        user_id = result[0]

        cursor.execute(
            """
            SELECT date_created, status, address FROM delivery_order
            WHERE user_id = ?
            ORDER BY date_created DESC
            """,
            (user_id,)
        )
        orders = cursor.fetchall()

    if not orders:
        await callback_query.message.edit_text(
            "У вас пока нет заказов.",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text="Назад", callback_data="main_menu")]]
            )
        )
        return

    text = "Ваши заказы:\n\n"
    for order in orders:
        text += f"Дата: {order[0]}\nСтатус: {order[1]}\nАдрес: {order[2]}\n\n"

    await callback_query.message.edit_text(
        text,
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="Назад", callback_data="main_menu")]]
        )
    )


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
