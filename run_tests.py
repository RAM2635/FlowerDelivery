import subprocess
import os

def main():
    # Определяем корневую директорию проекта
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Пути к manage.py и тестам Telegram-бота относительно корневой директории
    django_manage_path = os.path.join(base_dir, "shop_project", "manage.py")
    tg_bot_tests_path = os.path.join(base_dir, "tg_bot", "tests")

    try:
        # Запуск тестов Django
        django_tests_process = subprocess.Popen(
            [r".venv\\Scripts\\python", django_manage_path, "test"],
            stdout=None,
            stderr=None,
            universal_newlines=True
        )

        print("Тесты Django запущены.")

        # Запуск тестов Telegram-бота
        tg_bot_tests_process = subprocess.Popen(
            [r".venv\\Scripts\\python", "-m", "pytest", "tg_bot/tests"],
            stdout=None,
            stderr=None,
            universal_newlines=True
        )

        print("Тесты Telegram-бота запущены.")

        # Ожидание завершения обоих процессов
        django_tests_process.wait()
        tg_bot_tests_process.wait()
    except KeyboardInterrupt:
        print("\nОстановка тестов...")
        django_tests_process.terminate()
        tg_bot_tests_process.terminate()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        print("Скрипт завершён.")

if __name__ == "__main__":
    main()
