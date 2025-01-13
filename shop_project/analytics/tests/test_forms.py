from django.test import TestCase
from analytics.forms import DateRangeForm
from datetime import date, timedelta


class DateRangeFormTest(TestCase):
    def test_valid_data(self):
        today = date.today()
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')  # Приведение к строке
        end_date = today.strftime('%Y-%m-%d')  # Приведение к строке

        form_data = {
            "start_date": start_date,
            "end_date": end_date,
        }
        form = DateRangeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form_data = {
            "start_date": "invalid-date",  # Неверный формат
            "end_date": date.today().strftime('%Y-%m-%d'),
        }
        form = DateRangeForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("start_date", form.errors)
        self.assertIn("Введите правильную дату.", form.errors["start_date"])
        print(f"Ошибки формы: {form.errors}")

