# gradio_admin/tabs/statistics_tab.py
# Вкладка "Statistics" для Gradio-интерфейса проекта wg_qr_generator

import gradio as gr # type: ignore
import pandas as pd # type: ignore
from gradio_admin.functions.user_records import load_user_records
from gradio_admin.functions.format_helpers import format_time
from gradio_admin.functions.table_helpers import update_table
from gradio_admin.functions.format_helpers import format_user_info
from gradio_admin.functions.user_records import load_user_records
from gradio_admin.functions.show_user_info import show_user_info
from modules.traffic_updater import update_traffic_data
from settings import USER_DB_PATH

def statistics_tab():
    """Создает вкладку статистики пользователей WireGuard."""
    # Получение начальных данных
    def get_initial_data():
        update_traffic_data(USER_DB_PATH)
        table = update_table(True)
        user_list = ["Choose user"] + table["👤 User"].tolist() if not table.empty else ["Choose user"]
        return table, user_list

    initial_table, initial_user_list = get_initial_data()

    with gr.Row():
        gr.Markdown("## Statistics")

    # Чекбокс Show inactive и кнопка Refresh
    with gr.Row():
        show_inactive = gr.Checkbox(label="Show inactive", value=True)
        refresh_button = gr.Button("Refresh")

    # Поле поиска
    with gr.Row():
        search_input = gr.Textbox(label="Search", placeholder="Enter data to filter...", interactive=True)

    # Выбор пользователя
    with gr.Row():
        user_selector = gr.Dropdown(label="Select User", choices=initial_user_list, value="Choose user", interactive=True)
        user_info_display = gr.Textbox(label="User Details", value="", lines=10, interactive=False)

    # Таблица с данными
    with gr.Row():
        stats_table = gr.Dataframe(
            headers=["👤 User", "📊 Used", "📦 Limit", "🌐 IP Address", "⚡ St.", "💳 $", "UID"],
            value=initial_table,
            interactive=False,
            wrap=True
        )

    # Функция для обновления таблицы и списка пользователей
    def refresh_table(show_inactive):
        update_traffic_data(USER_DB_PATH)
        table = update_table(show_inactive)
        if table.empty:
            print("[DEBUG] Table is empty after update.")
        else:
            print(f"[DEBUG] Updated table:\n{table}")
        user_list = ["Choose user"] + table["👤 User"].tolist() if not table.empty else ["Choose user"]
        print(f"[DEBUG] User list: {user_list}")
        # Сбрасываем user_info_display
        return "", table, user_list, ""

    # Обновление таблицы при нажатии Refresh
    refresh_button.click(
        fn=refresh_table,
        inputs=[show_inactive],
        outputs=[search_input, stats_table, user_selector, user_info_display]
    )

    # Поиск
    def search_and_update_table(query, show_inactive):
        table = update_table(show_inactive)
        if query:
            table = table.loc[table.apply(lambda row: query.lower() in " ".join(map(str, row)).lower(), axis=1)]
        user_list = ["Choose user"] + table["👤 User"].tolist() if not table.empty else ["Choose user"]
        print(f"[DEBUG] Filtered user list: {user_list}")
        return table, user_list

    search_input.change(
        fn=search_and_update_table,
        inputs=[search_input, show_inactive],
        outputs=[stats_table, user_selector]
    )

    # Показ информации о пользователе
    def display_user_info(selected_user):
        if not selected_user or selected_user == "Choose user":
            return ""
        # Получение информации о пользователе
        user_info = show_user_info(selected_user)
        print(f"[DEBUG] User info:\n{user_info}")
        return user_info

    user_selector.change(
        fn=display_user_info,
        inputs=[user_selector],
        outputs=[user_info_display]
    )