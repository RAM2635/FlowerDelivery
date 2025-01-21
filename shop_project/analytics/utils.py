from collections import Counter
from datetime import datetime
from delivery.models import Order


def read_orders_from_csv():
    """
    Читает заказы из базы данных и преобразует их в формат, совместимый с предыдущей реализацией.
    """
    orders = []

    # Извлекаем все заказы из базы данных
    all_orders = Order.objects.prefetch_related('products')

    for order in all_orders:
        for product in order.products.all():
            orders.append({
                'ID': order.id,
                'User': order.user.username,
                'Status': order.get_status_display(),
                'Date_Created': order.date_created.strftime(
                    '%Y-%m-%d %H:%M:%S') if order.date_created else "Не указано",
                'Date_Completed': order.completed_date.strftime(
                    '%Y-%m-%d %H:%M:%S') if order.completed_date else "Не завершён",
                'Recipient_Name': order.recipient_name,
                'Phone': order.phone,
                'Address': order.address,
                'Category': product.category,
                'Price': str(product.price),
            })

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
        if order.get('Date_Completed') and order['Date_Completed'] != "Не завершён":
            try:
                date_created = datetime.strptime(order.get('Date_Created', ''), '%Y-%m-%d %H:%M:%S')
                date_completed = datetime.strptime(order['Date_Completed'], '%Y-%m-%d %H:%M:%S')
                total_time += (date_completed - date_created).total_seconds()
                count += 1
            except (ValueError, KeyError) as e:
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
