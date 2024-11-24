#!/usr/bin/env python3
# modules/manage_expiry.py
# Скрипт для управления сроком действия VPN аккаунтов WireGuard

import argparse
import os
import sys
import json
from datetime import datetime
from modules.account_expiry import check_expiry, extend_expiry, reset_expiry

# Добавляем путь для импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Пути к данным
WG_USERS_JSON = os.path.join("logs", "wg_users.json")
USER_RECORDS_JSON = os.path.join("user", "data", "user_records.json")


def load_json_data(filepath):
    """Загружает данные из JSON-файла."""
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_wg_show_data():
    """Имитация данных команды 'wg show'. Здесь нужно использовать реальный вызов."""
    return {
        "npQbtI10aPl+SMUCsGunbTh7P/qhzEkXaTsL/twfQ14=": {
            "allowed_ips": "10.66.66.5/32",
            "latest_handshake": "2 minutes, 41 seconds ago",
            "transfer": "504.86 MiB received, 5.96 GiB sent",
            "status": "active",
        },
        # Дополнительные записи
    }


def format_user_info(nickname, records, wg_data):
    """Форматирует информацию о пользователе."""
    info = records.get(nickname, {})
    wg_info = wg_data.get(info.get("peer"), {})

    return f"""
👤 User: {nickname}
🌐 Internal IP: {info.get('allowed_ips', 'N/A')}
🌎 External IP: {wg_info.get('endpoint', 'N/A')}
⬆️ Uploaded: {wg_info.get('transfer', 'N/A').split('received, ')[1]}
⬇️ Downloaded: {wg_info.get('transfer', 'N/A').split(' received, ')[0]}
📅 Last handshake: {wg_info.get('latest_handshake', 'N/A')}
🔥 Status: {wg_info.get('status', 'inactive')}
✅ Expiry: {info.get('expiry', 'N/A')}
"""


def main():
    parser = argparse.ArgumentParser(
        description="Скрипт для управления сроком действия VPN аккаунтов WireGuard"
    )

    subparsers = parser.add_subparsers(dest="action", help="Доступные команды")

    # Подкоманда check
    check_parser = subparsers.add_parser("check", help="Проверить, истек ли срок действия аккаунта")
    check_parser.add_argument("nickname", type=str, help="Имя пользователя для проверки")

    # Подкоманда extend
    extend_parser = subparsers.add_parser("extend", help="Продлить срок действия аккаунта")
    extend_parser.add_argument("nickname", type=str, help="Имя пользователя для продления")
    extend_parser.add_argument("days", type=int, help="Количество дней для продления срока действия")

    # Подкоманда reset
    reset_parser = subparsers.add_parser("reset", help="Сбросить срок действия аккаунта")
    reset_parser.add_argument("nickname", type=str, help="Имя пользователя для сброса срока")
    reset_parser.add_argument(
        "--days", type=int, default=30,
        help="Новый срок действия в днях (по умолчанию 30 дней)"
    )

    args = parser.parse_args()

    # Загружаем данные
    wg_users = load_json_data(WG_USERS_JSON)
    user_records = load_json_data(USER_RECORDS_JSON)
    wg_show = get_wg_show_data()

    try:
        if args.action == "check":
            if args.nickname in user_records:
                print(format_user_info(args.nickname, user_records, wg_show))
            else:
                print(f"❌ Пользователь {args.nickname} не найден.")

        elif args.action == "extend":
            extend_expiry(args.nickname, args.days)
            print(f"✅ Срок действия аккаунта {args.nickname} продлен на {args.days} дней.")

        elif args.action == "reset":
            reset_expiry(args.nickname, args.days)
            print(f"✅ Срок действия аккаунта {args.nickname} сброшен на {args.days} дней.")

        else:
            parser.print_help()

    except ValueError as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")


if __name__ == "__main__":
    main()