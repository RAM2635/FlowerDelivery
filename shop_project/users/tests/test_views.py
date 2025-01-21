from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',  # Добавлено обязательное поле email
            'password1': 'securePassword123',
            'password2': 'securePassword123',
        }

    def test_register_view(self):
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'securePassword123',
            'password2': 'securePassword123',
        })

        # Проверка на редирект
        if response.status_code == 200:
            print("Ошибки формы:", response.context['form'].errors)  # Отладка

        self.assertEqual(response.status_code, 302)  # Ожидается редирект
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_login_view(self):
        User.objects.create_user(username='testuser', password='securePassword123')
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'securePassword123'})
        self.assertEqual(response.status_code, 302)  # Редирект после успешного входа

    def test_logout_view(self):
        user = User.objects.create_user(username='testuser', password='securePassword123')
        self.client.login(username='testuser', password='securePassword123')

        # Отправляем POST-запрос на logout
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Редирект после выхода
