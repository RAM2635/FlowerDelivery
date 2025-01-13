from django.test import TestCase
from delivery.models import CustomUser  # Используем CustomUser вместо User

class AnalyticsViewsTestCase(TestCase):
    def setUp(self):
        # Создаем тестового пользователя с правами staff
        self.staff_user = CustomUser.objects.create_user(
            username="test_staff", password="password123", is_staff=True
        )
        self.client.login(username="test_staff", password="password123")

    def test_orders_by_date_view(self):
        response = self.client.get('/analytics/orders-by-date/')
        self.assertEqual(response.status_code, 200)

    def test_status_distribution_view(self):
        response = self.client.get('/analytics/status-distribution/')
        self.assertEqual(response.status_code, 200)
