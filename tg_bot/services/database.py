import sqlite3
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env
load_dotenv()

# Получение пути к базе данных из .env
DATABASE_PATH = os.getenv("DATABASE_PATH")

def get_user_by_telegram_id(telegram_id):
    """
    Получить данные пользователя по Telegram ID.
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email FROM delivery_customuser WHERE telegram_id=?", (telegram_id,))
        return cursor.fetchone()


def register_user(telegram_id, name, email):
    """
    Зарегистрировать пользователя в базе данных.
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE delivery_customuser SET telegram_id=? WHERE username=? AND email=?",
            (telegram_id, name, email)
        )
        conn.commit()
        return cursor.rowcount > 0


def get_product_by_id(product_id):
    """
    Получить данные о продукте по его ID.
    """
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price FROM delivery_product WHERE id = ?", (product_id,))
        return cursor.fetchone()