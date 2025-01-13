import csv
import os
import logging
from django.conf import settings
from django.contrib.admin import TabularInline
from django.contrib import admin
from .models import CustomUser, Product, Order, OrderProduct, Cart
from django.contrib.auth.admin import UserAdmin


logger = logging.getLogger('custom')


# Функция экспорта заказов в CSV
def export_orders_csv(modeladmin, request, queryset):
    logger.debug(f"Exporting orders: {queryset}")

    # Создаем директорию для хранения отчетов, если её нет
    reports_dir = os.path.join(settings.BASE_DIR, 'analytics', 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    # Определяем путь для сохранения файла
    file_path = os.path.join(reports_dir, 'orders.csv')

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            ['ID', 'User', 'Status', 'Date Created', 'Date Completed', 'Recipient Name', 'Phone', 'Address', 'Category',
             'Price'])
        for order in queryset:
            for product in order.products.all():
                writer.writerow([
                    order.id,
                    order.user.username,
                    order.get_status_display(),
                    order.date_created.strftime('%Y-%m-%d %H:%M:%S') if order.date_created else "Не указано",
                    order.completed_date.strftime('%Y-%m-%d %H:%M:%S') if order.completed_date else "Не завершён",
                    order.recipient_name,
                    order.phone,
                    order.address,
                    product.category,  # Категория продукта
                    product.price  # Цена продукта
                ])

    logger.info(f"CSV report saved at: {file_path}")
    modeladmin.message_user(request, f"Отчет сохранён: {file_path}")


class OrderProductInline(TabularInline):
    model = Order.products.through  # Используем промежуточную модель
    extra = 1  # Количество пустых строк для добавления новых записей

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'date_created')  # Поля, отображаемые в списке
    list_filter = ('status', 'date_created')  # Фильтры
    search_fields = ('user__username', 'status')  # Поля для поиска
    actions = [export_orders_csv]  # Действия
    list_editable = ('status',)  # Поле, доступное для редактирования
    fields = ('user', 'status', 'date_created', 'recipient_name', 'phone', 'address', 'comments')  # Поля на странице редактирования
    readonly_fields = ('date_created',)



@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    search_fields = ('order__id', 'product__name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'category', 'image_tag')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    readonly_fields = ('image_tag',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    search_fields = ('user__username', 'product__name')


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = (
        *(UserAdmin.fieldsets or []),
        (None, {'fields': ('phone', 'address', 'telegram_id')}),
    )
    list_display = ['username', 'email', 'phone', 'address', 'telegram_id']
    search_fields = ['username', 'email', 'phone']




