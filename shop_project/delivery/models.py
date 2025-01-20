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
    category = models.CharField(max_length=100)  # Поле для категории
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # Поле для изображения

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return self.name

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
    date_created = models.DateTimeField(default=now)
    recipient_name = models.CharField(max_length=255, default="Не указано")  # Имя получателя
    phone = models.CharField(max_length=20, default="Не указано")  # Телефон
    address = models.CharField(max_length=255, default="Не указано")  # Адрес доставки
    comments = models.TextField(blank=True, null=True)  # Комментарии
    completed_date = models.DateTimeField(blank=True, null=True)  # Дата завершения заказа
    products = models.ManyToManyField('Product', through='OrderProduct')

    def save(self, *args, **kwargs):
        # Если статус "Завершён" и дата завершения не установлена
        if self.status == 'completed' and not self.completed_date:
            # Устанавливаем дату завершения с точностью до секунд
            self.completed_date = datetime.now().replace(microsecond=0)
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
