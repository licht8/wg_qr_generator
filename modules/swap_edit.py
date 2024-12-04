#!/usr/bin/env python3

"""
swap_edit.py - Утилита для управления файлом подкачки (swap) в Linux

Особенности:
- Проверка и оптимизация swap.
- Поддержка параметров для гибкой настройки:
  * `--memory_required` или `--mr`: Назначает swap до 10% от объема диска.
  * `--min_swap` или `--ms`: Создает минимальный фиксированный swap (64 MB).
  * `--eco_swap`: Создает swap размером 2% от объема диска.
  * `--erase_swap`: Полностью удаляет swap.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from argparse import ArgumentParser
from prettytable import PrettyTable

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
sys.path.append(str(PROJECT_DIR))

from settings import PRINT_SPEED
from ai_diagnostics.ai_diagnostics import display_message_slowly


def run_command(command, check=True):
    """Выполнить команду в терминале и вернуть вывод."""
    try:
        result = subprocess.run(
            command, shell=True, text=True, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Ошибка: {e.stderr.strip()}")
        return None


def check_root():
    """Проверить, запущен ли скрипт от имени root."""
    if os.geteuid() != 0:
        display_message_slowly("🚨 Этот скрипт должен быть запущен от имени суперпользователя (root).", indent=False)
        exit(1)


def display_table(data, headers):
    """Показать таблицу с данными."""
    table = PrettyTable(headers)
    for row in data:
        table.add_row(row)
    return table


def get_swap_info():
    """Получить информацию о swap и памяти."""
    output = run_command("free -h")
    if not output:
        return None

    headers = ["Тип", "Общий", "Использовано", "Свободно"]
    rows = []
    for line in output.split("\n"):
        parts = line.split()
        if len(parts) >= 4 and parts[0] in ("Mem:", "Swap:"):
            rows.append(parts[:4])

    return display_table(rows, headers)


def disable_existing_swap(swap_file="/swap"):
    """Отключить и удалить существующий файл подкачки, если он используется."""
    if os.path.exists(swap_file):
        display_message_slowly(f"\n   🔍 Обнаружен существующий swap-файл: {swap_file}")
        run_command(f"swapoff {swap_file}", check=False)
        try:
            os.remove(swap_file)
            display_message_slowly(f"   🗑️ Удален существующий swap-файл: {swap_file}")
        except Exception as e:
            display_message_slowly(f"   ❌ Не удалось удалить файл: {e}")


def create_swap_file(size_mb, reason=None):
    """Создать и активировать файл подкачки."""
    try:
        swap_file = "/swap"
        disable_existing_swap(swap_file)

        display_message_slowly(f"   🛠️ Создаю файл подкачки размером {size_mb} MB...")
        run_command(f"dd if=/dev/zero of={swap_file} bs=1M count={size_mb}", check=True)

        display_message_slowly("   🎨 Форматирую файл подкачки...")
        run_command(f"mkswap {swap_file}", check=True)

        display_message_slowly("   ⚡ Активирую файл подкачки...")
        run_command(f"swapon {swap_file}", check=True)

        display_message_slowly(f"\n   ✅ Swap создан. Размер: {size_mb} MB")
        if reason:
            display_message_slowly(f"   🔍 Запрошен {reason}")

    except Exception as e:
        display_message_slowly(f"   ❌ Произошла ошибка: {e}")


import logging
from settings import LOG_LEVEL, LOG_FILE_PATH

# Настраиваем логирование
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=getattr(logging, LOG_LEVEL.upper(), logging.DEBUG),
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

def check_swap_edit(size_mb, action=None, silent=True, tolerance=2):
    """
    Проверяет состояние swap и вызывает swap_edit только при необходимости.

    :param size_mb: Требуемый размер swap (в MB).
    :param action: Действие (например, "micro", "min").
    :param silent: Если True, работает в тихом режиме.
    :param tolerance: Допустимая разница между текущим и требуемым swap (в MB).
    """
    try:
        # Проверяем текущий swap
        current_swap = run_command("free -m | awk '/^Swap:/ {print $2}'")
        current_swap = int(current_swap) if current_swap and current_swap.isdigit() else 0

        # Логирование текущего swap
        logger.debug(f"Текущий swap: {current_swap} MB")
        logger.debug(f"Требуемый swap: {size_mb} MB")

        # Проверяем условие с учетом допуска
        if current_swap >= size_mb - tolerance:
            if not silent:
                display_message_slowly(f"✅ Текущий swap ({current_swap} MB) уже оптимален. Никаких изменений не требуется.")
            logger.info(f"Swap ({current_swap} MB) уже оптимален или соответствует допустимому пределу ({tolerance} MB).")
            return

        # Если swap меньше требуемого с учетом допуска
        logger.info(f"Swap ({current_swap} MB) меньше требуемого ({size_mb} MB). Вызываем настройку swap.")
        swap_edit(size_mb=size_mb, action=action, silent=silent)

    except Exception as e:
        # Логирование ошибок
        logger.error(f"Ошибка при проверке или настройке swap: {e}")
        if not silent:
            display_message_slowly(f"❌ Ошибка: {e}")



def swap_edit(size_mb=None, action=None, silent=False):
    """Основная функция настройки swap."""
    check_root()

    # Проверка текущего состояния swap
    current_swap = run_command("free -m | awk '/^Swap:/ {print $2}'")
    current_swap = int(current_swap) if current_swap and current_swap.isdigit() else 0

    # Установить значение по умолчанию для size_mb, если не передано
    if size_mb is None:
        if action == "micro":
            size_mb = 64  # Размер swap для микрорежима
            silent = True
        elif action == "min":
            size_mb = 64
        elif action == "eco":
            total_disk = int(run_command("df --total | tail -1 | awk '{print $2}'")) // 1024
            size_mb = total_disk // 50  # 2% от объема диска
        elif action == "memory_required":
            total_disk = int(run_command("df --total | tail -1 | awk '{print $2}'")) // 1024
            size_mb = min(size_mb, total_disk // 10) if size_mb else total_disk // 10
        else:
            size_mb = 64  # Значение по умолчанию

    # Проверка: swap уже существует и соответствует требованиям
    if current_swap >= size_mb:
        if not silent:
            display_message_slowly(f"✅ Текущий swap ({current_swap} MB) уже оптимален. Ничего не изменено.")
        return

    # Если swap меньше требуемого, пересоздаем
    if current_swap < size_mb:
        if not silent:
            display_message_slowly(f"🔍 Текущий swap ({current_swap} MB) меньше запрашиваемого ({size_mb} MB). Обновляю swap.")
        disable_existing_swap()
        create_swap_file(size_mb, reason=action)

    # Итоговое состояние памяти (только если не silent)
    if not silent:
        display_message_slowly("📊 Итоговое состояние памяти:")
        final_swap_info = get_swap_info()
        if final_swap_info:
            print(final_swap_info)




if __name__ == "__main__":
    parser = ArgumentParser(description="Утилита для управления swap-файлом.")
    parser.add_argument("--memory_required", "--mr", type=int, help="Указать минимальный объем swap в MB (например, 1024).")
    parser.add_argument("--min_swap", "--ms", action="store_true", help="Создать минимальный swap (64 MB).")
    parser.add_argument("--eco_swap", action="store_true", help="Создать swap размером 2%% от объема диска.")
    parser.add_argument("--micro_swap", action="store_true", help="Создать swap размером 64 MB в тихом режиме.")
    parser.add_argument("--erase_swap", action="store_true", help="Удалить swap.")
    
    args = parser.parse_args()  # Убедитесь, что отступы соответствуют остальному коду
    
    if args.erase_swap:
        swap_edit(action="erase")
    elif args.eco_swap:
        swap_edit(action="eco")
    elif args.min_swap:
        swap_edit(action="min")
    elif args.micro_swap:
        swap_edit(action="micro", silent=True)
    elif args.memory_required:
        swap_edit(size_mb=args.memory_required, action="memory_required")
    else:
        swap_edit()

"""
### Полное описание скрипта `swap_edit.py` можно найти в docs/


"""
