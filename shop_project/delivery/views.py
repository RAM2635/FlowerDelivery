from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.urls import reverse  # если потребуется
from .models import Order, Cart, Product, Review, OrderProduct
from .forms import CheckoutForm

import logging
import importlib
import django.template

# Принудительная загрузка кастомных фильтров шаблонов
importlib.import_module("delivery.templatetags.custom_filters")

logger = logging.getLogger(__name__)


@login_required
def order_list(request):
    """
    Отображает список заказов текущего пользователя.
    Оптимизировано за счёт использования prefetch_related для related-объектов.
    """
    orders = Order.objects.filter(user=request.user).prefetch_related('orderproduct_set__product')
    order_details = []
    for order in orders:
        products = []
        for op in order.orderproduct_set.all():
            products.append({'name': op.product.name, 'quantity': op.quantity})
        order_details.append({
            'id': order.id,
            'user': order.user.username,
            'products': products,
            'status': order.get_status_display()
        })
    return render(request, 'delivery/order_list.html', {'orders': order_details})


def product_catalog(request):
    """Отображает каталог продуктов."""
    products = Product.objects.all()
    return render(request, 'delivery/catalog.html', {'products': products})


@login_required
def cart_add(request, product_id):
    """Добавляет выбранный продукт в корзину текущего пользователя."""
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_detail')


@login_required
def cart_detail(request):
    """
    Отображает содержимое корзины.
    Выполняется расчет общей стоимости и флага «недостаточно товара».
    Дополнительно проверяется GET-параметр 'updated', чтобы определить,
    были ли изменения сохранены (и, соответственно, активировать кнопку оформления заказа).
    """
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    has_insufficient_stock = any(item.quantity > item.product.balance for item in cart_items)
    # Проверяем GET-параметр "updated"
    cart_updated = request.GET.get('updated') == '1'

    logger.debug("=== DEBUG: Проверка наличия товара в корзине ===")
    for item in cart_items:
        logger.debug(f"{item.product.name}: В корзине {item.quantity}, Остаток {item.product.balance}")
    logger.debug(f"has_insufficient_stock: {has_insufficient_stock}")

    return render(request, 'delivery/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'has_insufficient_stock': has_insufficient_stock,
        'cart_updated': cart_updated,
    })


@login_required
def cart_remove(request, product_id):
    """Удаляет выбранный продукт из корзины."""
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    cart_item.delete()
    return redirect('cart_detail')


def index(request):
    """Главная страница сайта."""
    media_url = settings.MEDIA_URL
    return render(request, 'delivery/index.html', {'media_url': media_url})


@login_required
def checkout(request):
    """
    Оформление заказа на отдельной странице.
    Пользователь вводит данные доставки. Количество товаров берется из корзины.
    """
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    if not cart_items.exists():
        messages.error(request, "Ваша корзина пуста.")
        return redirect('cart_detail')

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Проверяем, что в корзине нет товара с количеством, превышающим остаток
            insufficient_items = []
            for item in cart_items:
                if item.quantity > item.product.balance:
                    insufficient_items.append(
                        f"{item.product.name} (Доступно: {item.product.balance}, В корзине: {item.quantity})"
                    )
            if insufficient_items:
                logger.debug("🚨 Недостаточно товара: %s", insufficient_items)
                messages.error(request, f"❌ Недостаточно товара: {', '.join(insufficient_items)}")
                return redirect('cart_detail')

            logger.debug("✅ Все проверки пройдены, создаём заказ.")
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    recipient_name=form.cleaned_data['recipient_name'],
                    phone=form.cleaned_data['phone'],
                    address=form.cleaned_data['address'],
                    comments=form.cleaned_data.get('comments', ''),
                    status='pending',
                    date_created=now()
                )

                for item in cart_items:
                    # Блокируем продукт для предотвращения гонок
                    product = Product.objects.select_for_update().get(id=item.product.id)
                    if item.quantity > product.balance:
                        messages.error(request, f"Ошибка: {product.name} уже недоступен.")
                        return redirect('cart_detail')
                    OrderProduct.objects.create(
                        order=order,
                        product=product,
                        quantity=item.quantity
                    )
                    # Удаляем запись из корзины. Баланс обновится через сигнал.
                    item.delete()

                messages.success(request, "Ваш заказ успешно оформлен!")
                return redirect('order_list')
        else:
            logger.debug("❌ Форма не прошла валидацию! Ошибки: %s", form.errors)
            messages.error(request, "Ошибка в данных формы. Проверьте введённые данные.")
    else:
        form = CheckoutForm()

    return render(request, 'delivery/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price
    })


@login_required
def cart_update(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    product = cart_item.product

    if request.method == 'POST':
        quantity_str = request.POST.get('quantity', '1')
        try:
            quantity = int(quantity_str)
        except ValueError:
            messages.error(request, "Некорректное количество.")
            return redirect('cart_detail')

        product.refresh_from_db()
        logger.debug(
            f"DEBUG: {product.name} - В корзине: {cart_item.quantity}, Остаток перед обновлением: {product.balance}")

        if quantity > product.balance:
            messages.error(request,
                           f"❌ Недостаточно товара: {product.name}. Доступно: {product.balance}, Запрошено: {quantity}")
            return redirect('cart_detail')

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            logger.debug(f"✅ Обновлено: {product.name} - Новое количество: {quantity}, Остаток: {product.balance}")
        else:
            cart_item.delete()
            logger.debug(f"🗑 Удалён из корзины: {product.name}")

    # Перенаправляем с параметром ?updated=1
    return redirect(f"{reverse('cart_detail')}?updated=1")


def about(request):
    """Страница «О нас»."""
    return render(request, 'delivery/about.html')


def contacts(request):
    """Страница контактов."""
    return render(request, 'delivery/contacts.html')


@login_required
def profile(request):
    """Профиль пользователя с историей заказов."""
    orders = Order.objects.filter(user=request.user).order_by('-date_created')
    return render(request, 'users/profile.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Детали конкретного заказа."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    products = [
        {
            'name': item.product.name,
            'quantity': item.quantity
        }
        for item in order.orderproduct_set.select_related('product')
    ]
    return render(request, 'users/order_detail.html', {'order': order, 'products': products})


@login_required
@transaction.atomic
def repeat_order(request, order_id):
    """
    Повторяет заказ, добавляя товары из выбранного заказа в корзину.
    Функция теперь определена только один раз и использует атомарную транзакцию.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    for item in order.orderproduct_set.all():
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=item.product,
            defaults={'quantity': item.quantity}
        )
        if not created:
            cart_item.quantity += item.quantity
            cart_item.save()
    messages.success(request, "Все товары из заказа добавлены в корзину.")
    return redirect('cart_detail')


@login_required
def add_review(request, product_id):
    """Добавляет или обновляет отзыв на продукт."""
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        rating_str = request.POST.get('rating', '5')
        try:
            rating = int(rating_str)
        except ValueError:
            messages.error(request, "Некорректный рейтинг.")
            return redirect('product_reviews', product_id=product.id)
        comment = request.POST.get('comment', '').strip()
        Review.objects.update_or_create(
            product=product, user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        messages.success(request, "Ваш отзыв был добавлен/обновлен.")
        return redirect('product_reviews', product_id=product.id)
    return render(request, 'delivery/add_review.html', {'product': product})


def product_reviews(request, product_id):
    """Отображает отзывы к продукту."""
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    return render(request, 'delivery/product_reviews.html', {'product': product, 'reviews': reviews})


def product_detail(request, product_id):
    """Детальная информация о продукте."""
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    return render(request, 'delivery/product_detail.html', {'product': product, 'reviews': reviews})
