from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.database import get_user_by_telegram_id, register_user
from aiogram.fsm.state import State, StatesGroup
from tg_bot.keyboards.inline import user_main_menu_keyboard, admin_main_menu_keyboard
from services.database import is_admin

# Состояния FSM для регистрации
class RegistrationState(StatesGroup):
    waiting_for_name = State()
    waiting_for_email = State()


async def start_handler(message: types.Message, state: FSMContext):
    user = get_user_by_telegram_id(message.from_user.id)
    if user:
        if is_admin(message.from_user.id):
            keyboard = admin_main_menu_keyboard()
        else:
            keyboard = user_main_menu_keyboard()

        await message.answer(
            "Добро пожаловать в меню администратора!",
            reply_markup=keyboard
        )


    else:
        await state.update_data(attempts=3)
        await message.answer("Введите ваше имя, как на flowershop:")
        await state.set_state(RegistrationState.waiting_for_name)

async def handle_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    attempts = data.get("attempts", 3)

    await state.update_data(name=message.text, attempts=attempts)
    await message.answer("Введите ваш email, как на flowershop:")
    await state.set_state(RegistrationState.waiting_for_email)


async def handle_email(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    email = message.text
    attempts = data.get("attempts", 3)

    if register_user(message.from_user.id, name, email):
        keyboard = InlineKeyboardBuilder().row(
            types.InlineKeyboardButton(text="Мои заказы", callback_data="my_orders"),
            types.InlineKeyboardButton(text="Сделать заказ", callback_data="make_order"),
        )
        await message.answer("Регистрация завершена. Добро пожаловать в магазин!", reply_markup=keyboard.as_markup())
        await state.clear()
    else:
        attempts -= 1
        if attempts > 0:
            await state.update_data(attempts=attempts)
            await message.answer(
                f"Имя и email не найдены в базе данных. У вас осталось {attempts} попыток.\nВведите ваше имя:")
            await state.set_state(RegistrationState.waiting_for_name)
        else:
            await message.answer(
                "Вы исчерпали все попытки. Пожалуйста, перейдите на сайт для регистрации: "
                "http://flowershop.hom/register/"
            )
            await state.clear()


def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, CommandStart())
    dp.message.register(handle_name, RegistrationState.waiting_for_name)
    dp.message.register(handle_email, RegistrationState.waiting_for_email)
