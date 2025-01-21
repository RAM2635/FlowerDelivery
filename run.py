import subprocess
import os

def main():
    # Определяем корневую директорию проекта
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Пути к manage.py и bot.py относительно корневой директории
    django_manage_path = os.path.join(base_dir, "shop_project", "manage.py")
    tg_bot_path = os.path.join(base_dir, "tg_bot", "bot.py")

    try:
        # Запуск Django
        django_process = subprocess.Popen(
            [r".venv\\Scripts\\python", django_manage_path, "runserver"],
            stdout=None,
            stderr=None,
            universal_newlines=True
        )

        print("Django сервер запущен.")

        # Запуск Telegram-бота
        tg_bot_process = subprocess.Popen(
            ["python", "-m", "tg_bot.bot"],  # Используем модульный импорт
            stdout=None,
            stderr=None,
            universal_newlines=True,
            cwd=os.path.dirname(os.path.abspath(__file__))  # Устанавливаем рабочую директорию
        )

        print("Telegram-бот запущен.")

        # Ожидание завершения обоих процессов
        django_process.wait()
        tg_bot_process.wait()
    except KeyboardInterrupt:
        print("\nОстановка процессов...")
        django_process.terminate()
        tg_bot_process.terminate()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        print("Скрипт завершён.")

if __name__ == "__main__":
    main()
