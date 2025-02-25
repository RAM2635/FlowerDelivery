from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.html import mark_safe
from django.conf import settings
from django.utils.timezone import now
from datetime import datetime


class CustomUser(AbstractUser):
    # Дополнительные поля для пользователя
    email = models.EmailField(unique=True, blank=False, null=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    telegram_id = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return self.username


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    balance = models.PositiveIntegerField(default=0)  # Поле для остатка товара
    category = models.CharField(max_length=100)  # Поле для категории
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # Поле для изображения

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Если товар создаётся впервые, устанавливаем balance = quantity
        if not self.pk:
            self.balance = self.quantity
        super().save(*args, **kwargs)

    # Метод для отображения изображения в админке
    def image_tag(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" style="max-height: 100px;"/>')
        return "Нет изображения"

    image_tag.short_description = 'Изображение'  # Подпись для поля в админке

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('processing', 'В обработке'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    status_changed = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=now)
    recipient_name = models.CharField(max_length=255, default="Не указано")  # Имя получателя
    phone = models.CharField(max_length=20, default="Не указано")  # Телефон
    address = models.CharField(max_length=255, default="Не указано")  # Адрес доставки
    comments = models.TextField(blank=True, null=True)  # Комментарии
    completed_date = models.DateTimeField(blank=True, null=True)  # Дата завершения заказа
    products = models.ManyToManyField('Product', through='OrderProduct')

    def save(self, *args, **kwargs):
        # Убираем миллисекунды из date_created
        if not self.pk:  # Только при создании объекта
            formatted_date = now().replace(microsecond=0)
            self.date_created = datetime.strptime(
                formatted_date.strftime('%Y-%m-%d %H:%M:%S'),
                '%Y-%m-%d %H:%M:%S'
            ).replace(tzinfo=formatted_date.tzinfo)

        # Проверяем, изменился ли статус
        if self.pk:
            original_status = Order.objects.get(pk=self.pk).status
            if original_status != self.status:
                self.status_changed = True

        # Если статус "Завершён" и дата завершения не установлена
        if self.status == 'completed' and not self.completed_date:
            formatted_date = now().replace(microsecond=0)
            self.completed_date = datetime.strptime(
                formatted_date.strftime('%Y-%m-%d %H:%M:%S'),
                '%Y-%m-%d %H:%M:%S'
            ).replace(tzinfo=formatted_date.tzinfo)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Продукт в заказе"
        verbose_name_plural = "Продукты в заказах"

    def __str__(self):
        return f"{self.product.name} в заказе {self.order.id}"


# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"{self.user} - {self.product.name} ({self.quantity})"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)  # Оценка от 1 до 5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['product', 'user']  # Один отзыв на товар от одного пользователя

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.product.name}"
