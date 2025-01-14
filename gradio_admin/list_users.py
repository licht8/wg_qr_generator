#!/usr/bin/env python3
# list_users.py
## Скрипт для отображения списка пользователей с информацией о сроке действия и IP-адресе.

import os
import json
from datetime import datetime
from modules.utils import read_json

USER_RECORDS_PATH = os.path.join("user", "data", "user_records.json")

def list_users():
    """
    Чтение списка пользователей и отображение информации о них.
    :return: Список пользователей или сообщение об ошибке.
    """
    if not os.path.exists(USER_RECORDS_PATH):
        return "❌ Файл user_records.json не найден."

    try:
        user_data = read_json(USER_RECORDS_PATH)
        if not user_data:
            return "❌ Нет зарегистрированных пользователей."

        users_list = []
        for username, details in user_data.items():
            created_at = details.get("created_at", "N/A")
            expires_at = details.get("expires_at", "N/A")
            address = details.get("address", "N/A")

            # Рассчитаем оставшееся время
            try:
                expires_datetime = datetime.fromisoformat(expires_at)
                remaining_time = expires_datetime - datetime.now()
                remaining_days = remaining_time.days
                remaining_str = f"{remaining_days} дней" if remaining_days > 0 else "Истек"
            except Exception:
                remaining_str = "Ошибка в данных срока действия"

            user_info = (
                f"👤 Пользователь: {username}\n"
                f"   📅 Создан: {created_at}\n"
                f"   ⏳ Истекает: {expires_at}\n"
                f"   ⏳ Осталось: {remaining_str}\n"
                f"   🌐 Адрес: {address}"
            )
            users_list.append(user_info)

        return "\n\n".join(users_list)

    except json.JSONDecodeError:
        return "❌ Ошибка чтения файла user_records.json. Проверьте его формат."
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"
