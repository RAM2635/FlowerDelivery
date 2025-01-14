from django.test import TestCase
from delivery.forms import CheckoutForm

class CheckoutFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'recipient_name': 'Иван Иванов',
            'phone': '+79991234567',
            'address': 'Test Address',
            'comments': 'Test Comment',
        }
        form = CheckoutForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'recipient_name': '',  # Поле обязательно
            'phone': 'invalid-phone',  # Неверный формат
            'address': '',
        }
        form = CheckoutForm(data=form_data)
        self.assertFalse(form.is_valid())
