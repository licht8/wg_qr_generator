#!/usr/bin/env python3
# main_interface.py
## Главный интерфейс Gradio для управления проектом wg_qr_generator

import sys
import os
import gradio as gr

# Добавляем путь к корневой директории проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Импортируем функции для работы с пользователями
from gradio_admin.create_user import create_user
from gradio_admin.delete_user import delete_user
from gradio_admin.search_user import search_user
from gradio_admin.wg_users_stats import load_data  # Импорт статистики пользователей


# Функция для обновления таблицы
def update_table(show_inactive):
    """Форматирует данные таблицы с тремя строками на пользователя."""
    table = load_data(show_inactive)
    print(f"[DEBUG] Загружены данные: {table}")  # Отладка
    formatted_rows = []

    for row in table:
        username = row[0]
        allowed_ips = row[2]
        recent = row[5]
        endpoint = row[1] or "N/A"
        up = row[4]
        down = row[3]
        status = row[6]

        # Эмодзи для состояния
        recent_emoji = "🟢" if status == "active" else "🔴"
        state_emoji = "✅" if status == "active" else "❌"

        # Формирование строк
        formatted_rows.append([f"{username}", f"Up: {up}"])
        formatted_rows.append([f"{allowed_ips} {recent_emoji}", f"Down: {down}"])
        formatted_rows.append([f"Endpoint: {endpoint}", f"State: {state_emoji}"])

    return formatted_rows


# Основной интерфейс
with gr.Blocks(css="style.css") as admin_interface:
    # Вкладка для создания пользователя
    with gr.Tab("Создание пользователя"):
        with gr.Row():
            gr.Markdown("## Создать нового пользователя")
        with gr.Column(scale=1, min_width=300):
            username_input = gr.Textbox(label="Имя пользователя", placeholder="Введите имя пользователя...")
            create_button = gr.Button("Создать пользователя")
            create_output = gr.Textbox(label="Результат создания", interactive=False)
            qr_code_image = gr.Image(label="QR-код", visible=False)

            def handle_create_user(username):
                """Обработчик для создания пользователя и отображения QR-кода."""
                result, qr_code_path = create_user(username)
                if qr_code_path:
                    return result, gr.update(visible=True, value=qr_code_path)
                return result, gr.update(visible=False)

            create_button.click(
                handle_create_user,
                inputs=username_input,
                outputs=[create_output, qr_code_image]
            )

    # Вкладка для удаления пользователей
    with gr.Tab("Удаление пользователей"):
        with gr.Row():
            gr.Markdown("## Удалить пользователя")
        with gr.Column(scale=1, min_width=300):
            delete_input = gr.Textbox(label="Имя пользователя для удаления", placeholder="Введите имя пользователя...")
            delete_button = gr.Button("Удалить пользователя")
            delete_output = gr.Textbox(label="Результат удаления", interactive=False)
            delete_button.click(delete_user, inputs=delete_input, outputs=delete_output)

    # Вкладка для поиска пользователей
    with gr.Tab("Поиск пользователей"):
        with gr.Row():
            gr.Markdown("## Поиск пользователей")
        with gr.Column(scale=1, min_width=300):
            search_input = gr.Textbox(label="Введите имя или IP", placeholder="Введите строку для поиска...")
            search_button = gr.Button("Поиск")
            search_output = gr.Textbox(label="Результат поиска", interactive=False)
            search_button.click(search_user, inputs=search_input, outputs=search_output)

    # Вкладка для статистики пользователей WireGuard
    with gr.Tab("Статистика"):
        with gr.Row():
            gr.Markdown("## Статистика")
        with gr.Column(scale=1, min_width=300):
            search_input = gr.Textbox(label="Поиск", placeholder="Введите данные для фильтрации...")
            refresh_button = gr.Button("Обновить")
            show_inactive = gr.Checkbox(label="Показать неактивных", value=True)
        with gr.Row():
            stats_table = gr.Dataframe(
                headers=["User/IPs", "Up/Down"],
                value=update_table(True),
                interactive=False,
                wrap=True
            )

            def search_and_update_table(query, show_inactive):
                """Фильтрует данные таблицы по запросу."""
                table = update_table(show_inactive)
                if query:
                    table = [row for row in table if query.lower() in " ".join(map(str, row)).lower()]
                print(f"[DEBUG] Обновленная таблица после поиска: {table}")  # Отладка
                return table

            search_input.change(
                fn=search_and_update_table,
                inputs=[search_input, show_inactive],
                outputs=[stats_table]
            )

            refresh_button.click(
                fn=update_table,
                inputs=[show_inactive],
                outputs=[stats_table]
            )

# Запуск интерфейса
if __name__ == "__main__":
    admin_interface.launch(server_name="0.0.0.0", server_port=7860, share=True)
