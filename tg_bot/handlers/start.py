from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from tg_bot.keyboards.inline import user_main_menu_keyboard, admin_main_menu_keyboard
from tg_bot.services.database import is_admin
from tg_bot.services.database import get_user_by_telegram_id, register_user

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
    await message.answer("📧Введите ваш email, как на flowershop:")
    await state.set_state(RegistrationState.waiting_for_email)


async def handle_email(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    email = message.text
    attempts = data.get("attempts", 3)

    if register_user(message.from_user.id, name, email):
        await message.answer(
            "Регистрация завершена🎉. Добро пожаловать в магазин!",
            reply_markup=user_main_menu_keyboard()
        )
        await state.clear()
    else:
        attempts -= 1
        if attempts > 0:
            await state.update_data(attempts=attempts)
            await message.answer(
                f"Имя и email не найдены в базе данных. У вас осталось {attempts} попыток.\nВведите ваше имя:"
            )
            await state.set_state(RegistrationState.waiting_for_name)
        else:
            await message.answer(
                "Вы исчерпали все попытки. Пожалуйста, перейдите на сайт для регистрации: "
                "http://flowershop.hom/register/"
            )
            await state.clear()


async def exit_handler(message: types.Message, state: FSMContext):
    """
    Обработчик команды /exit для выхода из бота.
    """
    await state.clear()  # Очищаем состояние пользователя
    await message.answer("Вы вышли из бота. До скорой встречи! 👋", reply_markup=types.ReplyKeyboardRemove())