import pytest
from tg_bot.services.statuses import translate_status


@pytest.mark.parametrize(
    "status_key, expected_translation",
    [
        ("pending", "В ожидании"),
        ("processing", "В обработке"),
        ("completed", "Завершён"),
        ("cancelled", "Отменён"),
        ("unknown", "Неизвестный статус"),  # Неизвестный ключ
        (" PENDING ", "В ожидании"),  # Пробелы и регистр
        ("PROCESSING", "В обработке"),  # Регистр
        (None, "Неизвестный статус"),  # Некорректный тип
        (123, "Неизвестный статус"),  # Некорректный тип
    ]
)
def test_translate_status(status_key, expected_translation):
    assert translate_status(status_key) == expected_translation
