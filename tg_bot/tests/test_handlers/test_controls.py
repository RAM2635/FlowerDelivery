from tg_bot.handlers.controls import add_active_message


def test_add_active_message():
    # Очистка глобальной переменной active_messages
    from tg_bot.handlers.controls import active_messages
    active_messages.clear()

    # Тестовые данные
    user_id = 12345
    message_id = 67890

    # Вызов функции
    add_active_message(user_id, message_id)

    # Проверка результата
    assert user_id in active_messages
    assert len(active_messages[user_id]) == 1
    assert active_messages[user_id][0]['message_id'] == message_id
    assert active_messages[user_id][0]['keyboard_active'] is True


def test_remove_inactive_messages():
    # Очистка глобальной переменной active_messages
    from tg_bot.handlers.controls import active_messages
    active_messages.clear()

    # Тестовые данные
    user_id = 12345
    active_messages[user_id] = [
        {'message_id': 1, 'keyboard_active': True},
        {'message_id': 2, 'keyboard_active': False},
    ]

    # Вызов функции
    from tg_bot.handlers.controls import remove_inactive_messages
    remove_inactive_messages(user_id)

    # Проверка результата
    assert user_id in active_messages
    assert len(active_messages[user_id]) == 1
    assert active_messages[user_id][0]['message_id'] == 1
    assert active_messages[user_id][0]['keyboard_active'] is True
