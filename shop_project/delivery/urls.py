from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_catalog, name='product_catalog'),  # Каталог
    path('orders/', views.order_list, name='order_list'),
    path('cart/', views.cart_detail, name='cart_detail'),  # Просмотр корзины
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),  # Добавление товара в корзину
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),  # Удаление товара из корзины
    path('checkout/', views.checkout, name='checkout'),  # Оформление заказа
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('about/', views.about, name='about'),  # Страница "О нас"
    path('contacts/', views.contacts, name='contacts'),  # Страница "Контакты"
    path('profile/', views.profile, name='profile'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/repeat/', views.repeat_order, name='repeat_order'),
    path('product/<int:product_id>/reviews/', views.product_reviews, name='product_reviews'),
    path('product/<int:product_id>/review/add/', views.add_review, name='add_review'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('order/<int:order_id>/repeat/', views.repeat_order, name='repeat_order'),

]
