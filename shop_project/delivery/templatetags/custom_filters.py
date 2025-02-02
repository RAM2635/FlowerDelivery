from django import template
from decimal import Decimal, InvalidOperation  # Импортируем InvalidOperation

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return Decimal(value) * Decimal(arg)
    except (TypeError, ValueError, InvalidOperation):  # Теперь ошибка не будет
        return 0
