from django import forms


class CheckoutForm(forms.Form):
    recipient_name = forms.CharField(
        label="Имя получателя",
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя получателя'
        })
    )

    phone = forms.CharField(
        label="Телефон",
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите номер телефона'
        })
    )
    address = forms.CharField(
        label="Адрес доставки",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Введите адрес доставки',
            'rows': 3
        })
    )
    comments = forms.CharField(
        label="Комментарий (необязательно)",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Добавьте комментарий к заказу',
            'rows': 2
        })
    )
