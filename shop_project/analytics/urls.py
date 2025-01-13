from django.urls import path
from . import views



urlpatterns = [
    path('', views.analytics_home, name='analytics_home'),
    path('orders-report/', views.orders_report_view, name='orders_report'),
    path('status-distribution/', views.status_distribution, name='status_distribution'),
    path('user-distribution/', views.user_distribution, name='user_distribution'),
    path('average-completion-time/', views.average_completion_time, name='average_completion_time'),
    path('popular-products/', views.popular_products, name='popular_products'),
    path('orders-by-date/', views.orders_by_date, name='orders_by_date'),
]


