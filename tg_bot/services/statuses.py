

STATUS_TRANSLATIONS = {
    'pending': 'В ожидании',
    'processing': 'В обработке',
    'completed': 'Завершён',
    'cancelled': 'Отменён',
}

def translate_status(status_key):
    """
    Переводит ключ статуса в читаемый формат.
    :param status_key: Строка с ключом статуса.
    :return: Читаемое значение статуса.
    """
    if not isinstance(status_key, str):  # Проверка типа данных
        return 'Неизвестный статус'

    # Убираем пробелы и приводим к нижнему регистру
    clean_status = status_key.strip().lower()
    return STATUS_TRANSLATIONS.get(clean_status, 'Неизвестный статус')

