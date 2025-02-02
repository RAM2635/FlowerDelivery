from django.test import TestCase
from datetime import datetime, timezone as dt_timezone
from django.utils import timezone
from delivery.models import Order, Product, OrderProduct, CustomUser
from analytics.utils import count_orders_by_date

class TestUtils(TestCase):

    def setUp(self):
        """
        Создание тестовых данных.
        """
        self.user = CustomUser.objects.create_user(username='testuser', password='password123')
        self.product = Product.objects.create(
            name="Test Product", price=10.0, quantity=50, category="Test Category"
        )

        self.order1 = Order.objects.create(
            user=self.user,
            status="pending",
            recipient_name="Test Name",
            phone="123456789",
            address="Test Address",
            date_created=timezone.make_aware(datetime(2025, 1, 1, 10, 42, 52))
        )
        OrderProduct.objects.create(order=self.order1, product=self.product, quantity=1)

        self.order2 = Order.objects.create(
            user=self.user,
            status="completed",
            recipient_name="Test Name",
            phone="123456789",
            address="Test Address",
            date_created=timezone.make_aware(datetime(2025, 1, 1, 15, 58, 54))
        )
        OrderProduct.objects.create(order=self.order2, product=self.product, quantity=1)

        self.order3 = Order.objects.create(
            user=self.user,
            status="processing",
            recipient_name="Test Name",
            phone="123456789",
            address="Test Address",
            date_created=timezone.make_aware(datetime(2025, 1, 2, 9, 0, 0))
        )
        OrderProduct.objects.create(order=self.order3, product=self.product, quantity=1)

    def test_count_orders_by_date(self):
        """
        Формируем список словарей с ключом "Date_Created", содержащим дату создания заказа в UTC-формате,
        и проверяем, что суммарное количество заказов, подсчитанное функцией, равно 3.
        """
        orders = [
            {"Date_Created": self.order1.date_created.astimezone(dt_timezone.utc).strftime('%Y-%m-%d %H:%M:%S')},
            {"Date_Created": self.order2.date_created.astimezone(dt_timezone.utc).strftime('%Y-%m-%d %H:%M:%S')},
            {"Date_Created": self.order3.date_created.astimezone(dt_timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}
        ]

        distribution = count_orders_by_date(orders)
        print("Distribution:", distribution)

        total_orders = sum(distribution.values())
        self.assertEqual(total_orders, 3)
