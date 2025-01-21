from django.test import TestCase
from users.forms import CustomUserCreationForm


class CustomUserCreationFormTest(TestCase):
    def test_form_valid_data(self):
        form = CustomUserCreationForm(data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'securePassword123',
            'password2': 'securePassword123',
        })
        print("Ошибки формы:", form.errors)
        self.assertTrue(form.is_valid())

    def test_form_invalid_password_mismatch(self):
        form = CustomUserCreationForm(data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'securePassword123',
            'password2': 'differentPassword123',
        })
        self.assertFalse(form.is_valid())
