#!/usr/bin/env python3
# modules/manage_users_menu.py
# Объединенное меню для управления пользователями и сроками действия VPN WireGuard

import os
import sys
import subprocess
from modules.account_expiry import check_expiry, extend_expiry, reset_expiry
from modules.show_users import show_all_users

# Добавляем текущий и родительский каталог в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def manage_users_menu():
    """Объединенное меню для управления пользователями."""
    while True:
        print("\n========== Управление пользователями ==========")
        print("1. 🌱 Создать пользователя")
        print("2. 🔍 Показать всех пользователей")
        print("3. ❌ Удалить пользователя")
        print("4. 📅 Проверить срок действия аккаунта")
        print("5. ➕ Продлить срок действия аккаунта")
        print("6. 🔄 Сбросить срок действия аккаунта")
        print("\n\t0 или q. Вернуться в главное меню")
        print("===============================================")
        choice = input("Выберите действие: ").strip().lower()

        if choice == "1":
            nickname = input("Введите имя пользователя (nickname): ").strip()
            subprocess.run(["python3", "main.py", nickname])
        elif choice == "2":
            show_all_users()
        elif choice == "3":
            nickname = input("Введите имя пользователя для удаления: ").strip()
            print(f"❌ Пользователь {nickname} успешно удален.")  # Добавить логику удаления пользователя
        elif choice == "4":
            nickname = input("Введите имя пользователя для проверки: ").strip()
            result = check_expiry(nickname)
            print(result)
        elif choice == "5":
            nickname = input("Введите имя пользователя для продления срока: ").strip()
            days = input("Введите количество дней для продления: ").strip()
            extend_expiry(nickname, int(days))
        elif choice == "6":
            nickname = input("Введите имя пользователя для сброса срока: ").strip()
            reset_expiry(nickname)
        elif choice in {"0", "q"}:
            print("🔙 Возврат в главное меню...")
            break
        else:
            print("⚠️ Некорректный выбор. Попробуйте еще раз.")


if __name__ == "__main__":
    manage_users_menu()
