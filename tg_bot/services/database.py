import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env
load_dotenv()

# Получение пути к базе данных из .env
DATABASE_PATH = os.getenv("DATABASE_PATH")
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID")

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


def is_admin(telegram_id):
    """
    Проверить, является ли пользователь администратором через переменные окружения.

    :param telegram_id: Telegram ID пользователя.
    :return: True, если пользователь администратор, иначе False.
    """
    return str(telegram_id) == ADMIN_TELEGRAM_ID

def update_order_status(order_id, new_status, admin_telegram_id, database_path):
    """
    Обновить статус заказа.

    :param order_id: ID заказа для обновления.
    :param new_status: Новый статус для заказа.
    :param admin_telegram_id: Telegram ID администратора, выполняющего операцию.
    :param database_path: Путь к базе данных.
    """
    if not is_admin(admin_telegram_id):
        raise PermissionError("Пользователь не имеет прав администратора.")

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()

        # Обновить статус и дату завершения заказа, если необходимо
        cursor.execute(
            "UPDATE delivery_order SET status=?, completed_date=? WHERE id=?",
            (
                new_status,
                datetime.now() if new_status == 'completed' else None,
                order_id
            )
        )

        conn.commit()

        # Получить Telegram ID пользователя для уведомления
        cursor.execute(
            "SELECT c.telegram_id FROM delivery_order o JOIN delivery_customuser c ON o.user_id = c.id WHERE o.id = ?",
            (order_id,)
        )
        result = cursor.fetchone()
        if result:
            return result[0]  # Возвращаем Telegram ID пользователя

        return None
