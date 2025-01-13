import csv
from collections import Counter
from datetime import datetime
from django.conf import settings
import os


def read_orders_from_csv():
    file_path = os.path.join(settings.BASE_DIR, 'analytics', 'reports', 'orders.csv')
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден.")

    orders = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Преобразуем ключи заголовков
            row = {key.replace(' ', '_'): value for key, value in row.items()}
            try:
                # Проверяем корректность поля Date_Created
                if row.get('Date_Created'):
                    datetime.strptime(row['Date_Created'], '%Y-%m-%d %H:%M:%S')
                orders.append(row)
            except ValueError as e:
                print(f"Ошибка преобразования строки: {row['Date_Created']} -> {e}")
    return orders


def count_status_distribution(orders):
    statuses = [order.get('Status', 'Unknown') for order in orders]  # Обработка отсутствующего ключа
    return dict(Counter(statuses))


def count_orders_by_user(orders):
    users = [order.get('User', 'Anonymous') for order in orders]  # Обработка отсутствующего ключа
    return dict(Counter(users))


def calculate_average_completion_time(orders):
    total_time = 0
    count = 0
    for order in orders:
        if order.get('Date Completed') and order['Date Completed'] != "Не завершён":
            try:
                date_created = datetime.strptime(order.get('Date Created', ''), '%Y-%m-%d %H:%M:%S')
                date_completed = datetime.strptime(order['Date Completed'], '%Y-%m-%d %H:%M:%S')
                total_time += (date_completed - date_created).total_seconds()
                count += 1
            except (ValueError, KeyError):
                continue
    return total_time / count if count > 0 else 0


def count_popular_products(orders):
    products = [order.get('Category', 'Без категории') for order in orders]  # Обработка отсутствующего ключа
    return dict(Counter(products))


def count_orders_by_date(orders):
    if not orders:
        return {}

    date_counts = {}
    for order in orders:
        date = order.get("Date_Created")
        if date:
            date_counts[date] = date_counts.get(date, 0) + 1

    return date_counts




