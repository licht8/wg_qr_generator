#!/usr/bin/env python3
# gradio_admin/functions/table_helpers.py
# Утилита для обработки и отображения данных в таблице Gradio

import os
import json
import pandas as pd
from settings import USER_DB_PATH  # Путь к JSON с данными пользователей

def load_data(show_inactive=True):
    """Загружает данные пользователей из JSON."""
    if not os.path.exists(USER_DB_PATH):
        return []

    with open(USER_DB_PATH, "r") as f:
        users = json.load(f)

    table = []
    for username, user_info in users.items():
        if not show_inactive and user_info.get("status", "") != "active":
            continue
        table.append({
            "username": user_info.get("username", "N/A"),
            "email": user_info.get("email", "N/A"),
            "telegram_id": user_info.get("telegram_id", "N/A"),
            "allowed_ips": user_info.get("allowed_ips", "N/A"),
            "data_used": user_info.get("data_used", "0.0 KiB"),
            "data_limit": user_info.get("data_limit", "100.0 GB"),
            "status": user_info.get("status", "inactive"),
            "subscription_plan": user_info.get("subscription_plan", "free"),
        })
    return table

def update_table(show_inactive):
    """Создает таблицу для отображения в Gradio."""
    users = load_data(show_inactive)
    formatted_rows = []

    for user in users:
        formatted_rows.append([
            user["username"],
            user["email"],
            user["telegram_id"],
            user["allowed_ips"],
            user["data_used"],
            user["data_limit"],
            user["status"],
            user["subscription_plan"],
        ])

    return pd.DataFrame(
        formatted_rows,
        columns=[
            "👤 Username",
            "📧 Email",
            "📱 Telegram",
            "🔗 Allowed IPs",
            "📊 Data Used",
            "📦 Data Limit",
            "⚡ Status",
            "💳 Plan",
        ]
    )
