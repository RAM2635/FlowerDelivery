from django import forms
from datetime import date


class DateRangeForm(forms.Form):
    start_date = forms.DateField(required=True, widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(required=True, widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        # Проверка: начальная дата должна быть раньше или равна конечной
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Начальная дата не может быть позже конечной.")

        # Проверка: дата не может быть в будущем
        if start_date and start_date > date.today():
            self.add_error("start_date", "Начальная дата не может быть в будущем.")
        if end_date and end_date > date.today():
            self.add_error("end_date", "Конечная дата не может быть в будущем.")

        return cleaned_data
