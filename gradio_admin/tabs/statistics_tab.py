#!/usr/bin/env python3
# statistics_tab.py
# Вкладка "Statistics" Gradio-интерфейса wg_qr_generator

import gradio as gr
import pandas as pd
import json
import os
from settings import USER_DB_PATH  # Путь к JSON с данными пользователей


def load_user_records():
    """Загружает данные пользователей из JSON."""
    print("[DEBUG] Загрузка данных пользователей из JSON...")
    if not os.path.exists(USER_DB_PATH):
        print("[ERROR] Файл JSON с пользователями не найден!")
        return {}

    with open(USER_DB_PATH, "r") as f:
        data = json.load(f)
    print(f"[DEBUG] Загружено {len(data)} пользователей.")
    return data


def prepare_table_data(show_inactive=True):
    """Создает данные для таблицы."""
    print(f"[DEBUG] Подготовка данных для таблицы. Show inactive: {show_inactive}")
    user_records = load_user_records()
    table_data = []

    for user in user_records.values():
        if not show_inactive and user.get("status") != "active":
            continue
        table_data.append({
            "Select": False,
            "User": user.get("username", "N/A"),
            "Used": user.get("data_used", "0.0 KiB"),
            "Limit": user.get("data_limit", "100.0 GB"),
            "Status": user.get("status", "inactive"),
            "Price": user.get("subscription_price", "0.00 USD"),
            "UID": user.get("user_id", "N/A")
        })

    print(f"[DEBUG] Подготовлено {len(table_data)} записей для таблицы.")
    return pd.DataFrame(table_data)


def get_user_info(selected_rows):
    """Возвращает подробную информацию о выбранном пользователе."""
    if not selected_rows:
        print("[WARNING] Пользователь не выбран.")
        return "No user selected"
    
    selected_uid = selected_rows[0].get("UID", "N/A")
    print(f"[DEBUG] Получен UID выбранного пользователя: {selected_uid}")
    user_records = load_user_records()
    for user in user_records.values():
        if user.get("user_id") == selected_uid:
            print(f"[DEBUG] Найден пользователь: {user.get('username')}")
            return json.dumps(user, indent=4)
    print("[WARNING] Пользователь не найден.")
    return "User not found."


def block_user(selected_rows):
    """Блокирует выбранного пользователя."""
    if not selected_rows:
        print("[WARNING] Невозможно заблокировать: пользователь не выбран.")
        return "No user selected"

    selected_uid = selected_rows[0].get("UID", "N/A")
    print(f"[DEBUG] Блокировка пользователя с UID: {selected_uid}")
    user_records = load_user_records()
    for username, user in user_records.items():
        if user.get("user_id") == selected_uid:
            user["status"] = "blocked"
            with open(USER_DB_PATH, "w") as f:
                json.dump(user_records, f, indent=4)
            print(f"[DEBUG] Пользователь {username} заблокирован.")
            return f"User {username} blocked."
    print("[WARNING] Пользователь для блокировки не найден.")
    return "User not found."


def delete_user(selected_rows):
    """Удаляет выбранного пользователя."""
    if not selected_rows:
        print("[WARNING] Невозможно удалить: пользователь не выбран.")
        return "No user selected"

    selected_uid = selected_rows[0].get("UID", "N/A")
    print(f"[DEBUG] Удаление пользователя с UID: {selected_uid}")
    user_records = load_user_records()
    for username, user in list(user_records.items()):
        if user.get("user_id") == selected_uid:
            del user_records[username]
            with open(USER_DB_PATH, "w") as f:
                json.dump(user_records, f, indent=4)
            print(f"[DEBUG] Пользователь {username} удален.")
            return f"User {username} deleted."
    print("[WARNING] Пользователь для удаления не найден.")
    return "User not found."


def statistics_tab():
    """Создает интерфейс вкладки статистики."""
    with gr.Tab("🔍 Statistics"):
        gr.Markdown("## Статистика пользователей")

        # Фильтры
        with gr.Row():
            search_box = gr.Textbox(label="Search", placeholder="Search for users...")
            show_inactive_checkbox = gr.Checkbox(label="Show inactive users", value=True)
            refresh_button = gr.Button("Refresh Table")

        # Таблица данных
        user_table = gr.Dataframe(
            value=prepare_table_data(),
            interactive=True,
            label="Users Table"
        )

        # Подробная информация
        user_info_box = gr.Textbox(label="User Information", lines=10, interactive=False)

        # Управление пользователями
        with gr.Row():
            block_button = gr.Button("Block User")
            delete_button = gr.Button("Delete User")

        # Связывание компонентов
        def filter_table(search_query, show_inactive):
            print(f"[DEBUG] Фильтрация таблицы. Query: '{search_query}', Show inactive: {show_inactive}")
            df = prepare_table_data(show_inactive)
            if search_query:
                df = df[df.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)]
            print(f"[DEBUG] Фильтр применен. Найдено записей: {len(df)}.")
            return df

        refresh_button.click(lambda: prepare_table_data(), outputs=user_table)
        search_box.change(lambda q, show: filter_table(q, show), inputs=[search_box, show_inactive_checkbox], outputs=user_table)
        show_inactive_checkbox.change(lambda q, show: filter_table(q, show), inputs=[search_box, show_inactive_checkbox], outputs=user_table)
        user_table.select(get_user_info, outputs=user_info_box)
        block_button.click(block_user, inputs=user_table, outputs=user_info_box)
        delete_button.click(delete_user, inputs=user_table, outputs=user_info_box)
