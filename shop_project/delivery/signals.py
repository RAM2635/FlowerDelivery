from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import OrderProduct, Product, Order

@receiver(pre_save, sender=OrderProduct)
def adjust_product_balance_on_update(sender, instance, **kwargs):
    """
    Корректирует баланс товара при обновлении OrderProduct.
    Если объект обновляется (не создаётся), вычисляем разницу между новым и старым количеством
    и корректируем баланс товара, если заказ находится в состоянии 'pending'.
    """
    if not instance.pk:
        # Если объекта еще нет, это создание – обработаем в post_save.
        return

    try:
        old_instance = OrderProduct.objects.get(pk=instance.pk)
    except OrderProduct.DoesNotExist:
        return

    if instance.order.status == 'pending':
        delta = instance.quantity - old_instance.quantity
        if delta:
            instance.product.balance -= delta
            instance.product.save()


@receiver(post_save, sender=OrderProduct)
def update_product_balance_on_create(sender, instance, created, **kwargs):
    """
    При создании нового OrderProduct уменьшаем баланс товара, если заказ в состоянии 'pending'.
    """
    if created and instance.order.status == 'pending':
        instance.product.balance -= instance.quantity
        instance.product.save()


@receiver(post_delete, sender=OrderProduct)
def update_product_balance_on_delete(sender, instance, **kwargs):
    """
    При удалении OrderProduct возвращаем товар на склад, если заказ находится в состоянии 'pending'.
    """
    if instance.order.status == 'pending':
        instance.product.balance += instance.quantity
        instance.product.save()


@receiver(pre_save, sender=Order)
def store_previous_status(sender, instance, **kwargs):
    """
    Сохраняем предыдущий статус заказа в атрибут _old_status для дальнейшей проверки.
    """
    if instance.pk:
        try:
            previous = Order.objects.get(pk=instance.pk)
            instance._old_status = previous.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def restore_balance_on_status_change(sender, instance, created, **kwargs):
    """
    Если заказ изменился на 'cancelled', возвращаем товары на склад.
    Баланс будет восстановлен только один раз при смене статуса.
    """
    # Если заказ только создан или если его статус изменился с отличного от 'cancelled'
    if instance.status == 'cancelled' and (created or getattr(instance, '_old_status', None) != 'cancelled'):
        for item in instance.orderproduct_set.all():
            item.product.balance += item.quantity
            item.product.save()
