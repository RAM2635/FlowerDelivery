from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from delivery import views as delivery_views

urlpatterns = [
    path('admin/', admin.site.urls),  # Используем стандартную админку
    path('', delivery_views.index, name='index'),  # Главная страница
    path('catalog/', include('delivery.urls')),  # Подключение всех маршрутов приложения delivery
    path('users/', include('users.urls')),  # Маршруты для управления пользователями
    path('analytics/', include('analytics.urls')),  # Подключение аналитических маршрутов
]

# Добавляем маршруты для медиафайлов
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
