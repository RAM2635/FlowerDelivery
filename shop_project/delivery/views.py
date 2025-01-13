from .models import Order, Cart, Product, Review
from django.conf import settings
from django.utils.timezone import now
from .forms import CheckoutForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def order_list(request):
    # Фильтруем заказы только для текущего пользователя
    orders = Order.objects.filter(user=request.user).prefetch_related('products')

    order_details = []
    for order in orders:
        products = []
        for product in order.products.all():
            quantity = product.orderproduct_set.get(order=order).quantity
            products.append({'name': product.name, 'quantity': quantity})
        order_details.append({
            'id': order.id,
            'user': order.user.username,
            'products': products,
            'status': order.get_status_display()
        })

    return render(request, 'delivery/order_list.html', {'orders': order_details})


def product_catalog(request):
    products = Product.objects.all()  # Получаем все продукты из базы данных
    return render(request, 'delivery/catalog.html', {'products': products})


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Добавляем товар в корзину
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_detail')


@login_required
def cart_detail(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'delivery/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })


@login_required
def cart_remove(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    cart_item.delete()
    return redirect('cart_detail')


def index(request):
    media_url = settings.MEDIA_URL
    return render(request, 'delivery/index.html', {'media_url': media_url})


from django.shortcuts import redirect


@login_required
def checkout(request):
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            messages.error(request, "Ваша корзина пуста.")
            return redirect('cart_detail')  # Редирект на корзину

        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                comments=form.cleaned_data.get('comments', ''),
                status='pending',
                date_created=now()
            )
            for item in cart_items:
                order.products.add(item.product, through_defaults={'quantity': item.quantity})
                item.delete()  # Очистка корзины после оформления заказа

            messages.success(request, "Ваш заказ успешно оформлен!")
            return redirect('order_list')  # Редирект на список заказов
    else:
        form = CheckoutForm()

    return render(request, 'delivery/checkout.html', {'form': form})


@login_required
def cart_update(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()  # Удалить товар, если количество равно нулю
    return redirect('cart_detail')


def about(request):
    return render(request, 'delivery/about.html')


def contacts(request):
    return render(request, 'delivery/contacts.html')


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-date_created')
    return render(request, 'users/profile.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    products = [
        {
            'name': item.product.name,
            'quantity': item.quantity
        }
        for item in order.orderproduct_set.all()
    ]
    return render(request, 'users/order_detail.html', {'order': order, 'products': products})


from django.db import transaction


@login_required
@transaction.atomic
def repeat_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    for item in order.orderproduct_set.all():
        Cart.objects.create(
            user=request.user,
            product=item.product,
            quantity=item.quantity
        )
    messages.success(request, "Товары из заказа добавлены в вашу корзину.")
    return redirect('cart_detail')


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()
        Review.objects.update_or_create(
            product=product, user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )
        messages.success(request, "Ваш отзыв был добавлен/обновлен.")
        return redirect('product_reviews', product_id=product.id)
    return render(request, 'delivery/add_review.html', {'product': product})


def product_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    return render(request, 'delivery/product_reviews.html', {'product': product, 'reviews': reviews})


from django.shortcuts import render, get_object_or_404


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    return render(request, 'delivery/product_detail.html', {'product': product, 'reviews': reviews})


@login_required
def repeat_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    for item in order.orderproduct_set.all():
        # Добавляем каждый продукт в корзину
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
