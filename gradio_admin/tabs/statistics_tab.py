#!/usr/bin/env python3
# statistics_tab.py
# Вкладка "Statistics" с контейнерами для пользователей

import gradio as gr
import json
import os
from settings import USER_DB_PATH  # Путь к JSON с данными пользователей


def load_user_records():
    """Загружает данные пользователей из JSON."""
    if not os.path.exists(USER_DB_PATH):
        return {}
    with open(USER_DB_PATH, "r") as f:
        return json.load(f)


def filter_users(search_query, show_inactive):
    """Фильтрует список пользователей на основе ввода."""
    user_records = load_user_records()
    filtered_users = []
    for user in user_records.values():
        if not show_inactive and user.get("status") != "active":
            continue
        if search_query.lower() in user.get("username", "").lower():
            filtered_users.append(user)
    return filtered_users


def user_container(user):
    """Создает контейнер для отображения информации о пользователе."""
    return gr.Accordion(
        f"{user['username']} ({user['user_id']})",
        open=False,
        children=[
            gr.Markdown(
                f"""
                **Статус:** {user.get('status', 'N/A')}  
                **Использование данных:** {user.get('data_used', '0.0 KiB')} / {user.get('data_limit', '100.0 GB')}  
                **План подписки:** {user.get('subscription_plan', 'N/A')}  
                **Цена:** {user.get('subscription_price', '0.00 USD')}  
                **Последнее обновление:** {user.get('last_config_update', 'N/A')}
                """
            ),
            gr.Row([
                gr.Button("Block"),
                gr.Button("Delete"),
                gr.Button("Archive"),
            ])
        ]
    )


def update_user_list(search_query, show_inactive):
    """Обновляет список пользователей на основе фильтров."""
    users = filter_users(search_query, show_inactive)
    if not users:
        return [gr.Markdown("### Нет пользователей, соответствующих поиску.")]
    return [user_container(user) for user in users]


def statistics_tab():
    """Создает вкладку 'Statistics'."""
    with gr.Tab("🔍 Statistics"):
        gr.Markdown("## Управление пользователями WireGuard")

        # Верхний блок: фильтры и кнопка обновления
        with gr.Row():
            show_inactive_checkbox = gr.Checkbox(label="Show inactive users", value=True)
            refresh_button = gr.Button("Refresh")

        # Поисковая строка
        search_box = gr.Textbox(
            label="Поиск пользователей",
            placeholder="Введите имя пользователя для фильтрации...",
            interactive=True,
        )

        # Контейнер для динамического списка пользователей
        user_list = gr.Column()

        # Логика обновления списка пользователей
        def refresh_list():
            return update_user_list("", show_inactive_checkbox.value)

        search_box.change(
            fn=update_user_list,
            inputs=[search_box, show_inactive_checkbox],
            outputs=user_list
        )

        refresh_button.click(
            fn=refresh_list,
            inputs=[],
            outputs=user_list
        )

        # Инициализация списка пользователей при загрузке
        refresh_button.click(
            fn=refresh_list,
            inputs=[],
            outputs=user_list,
            queue=False
        )
