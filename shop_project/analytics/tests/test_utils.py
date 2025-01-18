from django.test import TestCase
from datetime import datetime
from django.utils import timezone
from delivery.models import Order, Product, OrderProduct
from delivery.models import CustomUser
from analytics.utils import read_orders_from_csv, count_orders_by_date


class TestUtils(TestCase):

    def setUp(self):
        """
        Создание тестовых данных.
        """
        user = CustomUser.objects.create_user(username='testuser', password='password123')
        product = Product.objects.create(name="Test Product", price=10.0, quantity=50, category="Test Category")

        order1 = Order.objects.create(
            user=user, status="pending", recipient_name="Test Name", phone="123456789", address="Test Address",
            date_created=timezone.make_aware(datetime(2025, 1, 1, 10, 42, 52))
        )
        OrderProduct.objects.create(order=order1, product=product, quantity=1)

        order2 = Order.objects.create(
            user=user, status="completed", recipient_name="Test Name", phone="123456789", address="Test Address",
            date_created=timezone.make_aware(datetime(2025, 1, 1, 15, 58, 54))
        )
        OrderProduct.objects.create(order=order2, product=product, quantity=1)

        order3 = Order.objects.create(
            user=user, status="processing", recipient_name="Test Name", phone="123456789", address="Test Address",
            date_created=timezone.make_aware(datetime(2025, 1, 2, 9, 0, 0))
        )
        OrderProduct.objects.create(order=order3, product=product, quantity=1)

    def test_count_orders_by_date(self):
        orders = read_orders_from_csv()

        # Убедимся, что строки дат совпадают с форматом, который ожидает функция
        for order in orders:
            if isinstance(order["Date_Created"], str):
                order["Date_Created"] = order["Date_Created"].strip()  # Убираем лишние пробелы

        # Подсчёт распределения
        distribution = count_orders_by_date(orders)

        # Печать для отладки
        print("Distribution:", distribution)  # Печатает словарь распределения

        # Преобразуем ожидаемые значения в UTC
        date_1_utc = "2025-01-01 07:42:52"
        date_2_utc = "2025-01-01 12:58:54"
        date_3_utc = "2025-01-02 06:00:00"

        # Проверяем, что данные соответствуют ожиданиям
        self.assertEqual(distribution.get(date_1_utc), 1)
        self.assertEqual(distribution.get(date_2_utc), 1)
        self.assertEqual(distribution.get(date_3_utc), 1)

