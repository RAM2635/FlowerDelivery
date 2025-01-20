from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .utils import (
    read_orders_from_csv,
    count_status_distribution,
    count_orders_by_user,
    calculate_average_completion_time,
    count_popular_products,
    count_orders_by_date,
)
from datetime import datetime


@staff_member_required
def orders_by_date(request):
    try:
        orders = read_orders_from_csv()

        # Получение параметров фильтра
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Преобразование параметров в объекты даты
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Фильтрация заказов по диапазону дат
        filtered_orders = [
            order for order in orders
            if
            ((not start_date or datetime.strptime(order['Date_Created'], "%Y-%m-%d %H:%M:%S").date() >= start_date) and
             (not end_date or datetime.strptime(order['Date_Created'], "%Y-%m-%d %H:%M:%S").date() <= end_date))
        ]

        # Распределение заказов по датам
        distribution = count_orders_by_date(filtered_orders)

    except FileNotFoundError as e:
        return render(request, "analytics/error.html", {"message": str(e)})

    # Передача данных в шаблон
    return render(request, 'analytics/orders_by_date.html', {'distribution': distribution})

@staff_member_required
def orders_report_view(request):
    """
    Отображает отчёт по заказам в виде таблицы.
    """
    try:
        orders = read_orders_from_csv()
    except FileNotFoundError as e:
        return render(request, "analytics/error.html", {"message": str(e)})

    context = {"orders": orders}
    return render(request, "analytics/orders_report.html", context)


@staff_member_required
def analytics_home(request):
    """
    Отображает домашнюю страницу аналитики.
    """
    return render(request, "analytics/home.html")


def index(request):
    # Здесь вы можете добавлять обработку данных аналитики
    context = {
        'message': 'Добро пожаловать в аналитику!',
    }
    return render(request, 'analytics/index.html', context)


@staff_member_required
def status_distribution(request):
    try:
        orders = read_orders_from_csv()
        distribution = count_status_distribution(orders)
    except FileNotFoundError as e:
        return render(request, "analytics/error.html", {"message": str(e)})
    return render(request, 'analytics/status_distribution.html', {'distribution': distribution})


@staff_member_required
def user_distribution(request):
    try:
        orders = read_orders_from_csv()
        distribution = count_orders_by_user(orders)
    except FileNotFoundError as e:
        return render(request, "analytics/error.html", {"message": str(e)})
    return render(request, 'analytics/user_distribution.html', {'distribution': distribution})


def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours} ч {minutes} мин {seconds} сек"

@staff_member_required
def average_completion_time(request):
    try:
        orders = read_orders_from_csv()
        avg_time_seconds = calculate_average_completion_time(orders)
        avg_time_formatted = format_time(avg_time_seconds)
    except FileNotFoundError as e:
        return render(request, "analytics/error.html", {"message": str(e)})
    return render(
        request,
        "analytics/average_completion_time.html",
        {'average_time': avg_time_formatted}
    )


@staff_member_required
def popular_products(request):
    try:
        orders = read_orders_from_csv()
        distribution = count_popular_products(orders)
    except FileNotFoundError as e:
        return render(request, "analytics/error.html", {"message": str(e)})
    return render(request, 'analytics/popular_products.html', {'distribution': distribution})


@staff_member_required
def orders_by_date(request):
    try:
        orders = read_orders_from_csv()

        # Получение параметров фильтра
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Преобразование параметров в объекты даты
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Фильтрация заказов по диапазону дат
        filtered_orders = [
            order for order in orders
            if
            ((not start_date or datetime.strptime(order['Date_Created'], "%Y-%m-%d %H:%M:%S").date() >= start_date) and
             (not end_date or datetime.strptime(order['Date_Created'], "%Y-%m-%d %H:%M:%S").date() <= end_date))
        ]

        # Распределение заказов по датам
        distribution = count_orders_by_date(filtered_orders)

    except FileNotFoundError as e:
        return render(request, "analytics/error.html", {"message": str(e)})

    # Передача данных в шаблон
    return render(request, 'analytics/orders_by_date.html', {'distribution': distribution})
