from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from delivery.models import Product, Cart
from django.urls import reverse

User = get_user_model()

class DeliveryViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.product = Product.objects.create(
            name='Test Product',
            price=100.0,
            quantity=10  # Указать значение для поля quantity
        )
        self.cart_url = reverse('cart_detail')
        self.checkout_url = reverse('checkout')

    def test_cart_add(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(f'/catalog/cart/add/{self.product.id}/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Cart.objects.filter(user=self.user, product=self.product).exists())




