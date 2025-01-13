from django.test import TestCase
from analytics.utils import read_orders_from_csv, count_orders_by_date

class TestUtils(TestCase):
    def test_read_orders_from_csv(self):
        # Проверить, что файл считывается без ошибок
        orders = read_orders_from_csv()
        self.assertGreater(len(orders), 0)

    def test_count_orders_by_date(self):
        orders = [
            {'Date_Created': '2025-01-01 10:42:52'},
            {'Date_Created': '2025-01-01 15:58:54'},
            {'Date_Created': '2025-01-02 09:00:00'}
        ]
        distribution = count_orders_by_date(orders)
        self.assertEqual(distribution['2025-01-01 10:42:52'], 1)
        self.assertEqual(distribution['2025-01-01 15:58:54'], 1)
        self.assertEqual(distribution['2025-01-02 09:00:00'], 1)

