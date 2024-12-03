#!/usr/bin/env python3
# wg_qr_generator/modules/uninstall.py
# ===========================================
# Скрипт для удаления WireGuard
# ===========================================

import os
import shutil
import subprocess
import platform
import logging
from pathlib import Path

# Import project settings
try:
    from settings import (
        SERVER_CONFIG_FILE,
        PARAMS_FILE,
        WG_CONFIG_DIR,
        LOG_FILE_PATH,
        LOG_LEVEL,
        LOG_DIR,
    )
except ImportError:
    print("❌ Could not import settings. Ensure this script is run from the project root.")
    exit(1)

# Setup logging
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=getattr(logging, LOG_LEVEL, "INFO"),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def confirm_action(prompt="Are you sure? (yes/no): "):
    """Запрашивает у пользователя подтверждение действия."""
    while True:
        choice = input(prompt).strip().lower()
        if choice in {"yes", "no"}:
            return choice == "yes"
        print("⚠️  Некорректный ввод. Введите 'yes' или 'no'.")

def is_wireguard_installed():
    """Check if WireGuard is installed."""
    return shutil.which("wg") is not None

def detect_package_manager():
    """Detect the package manager based on the operating system."""
    distro = platform.system()
    if distro == "Linux":
        with open("/etc/os-release", "r") as f:
            os_release = f.read()
            if "Ubuntu" in os_release:
                return "apt"
            elif "CentOS" in os_release or "Stream" in os_release:
                return "dnf"
    print("❌ Unsupported OS or distribution. Exiting.")
    logger.error("Unsupported OS or distribution.")
    exit(1)

def stop_wireguard():
    """Stop WireGuard service."""
    try:
        logger.info("Stopping WireGuard service...")
        result = subprocess.run(["systemctl", "is-active", "--quiet", "wg-quick@wg0"])
        if result.returncode == 0:  # Service is active
            subprocess.run(["systemctl", "stop", "wg-quick@wg0"], check=True)
            logger.info("WireGuard service stopped.")
            print("✅ WireGuard service stopped.")
        else:
            logger.info("WireGuard service is not active or already stopped.")
            print("⚠️ WireGuard service is not active or already stopped.")
    except subprocess.CalledProcessError as e:
        logger.error("Failed to stop WireGuard service: %s", e)
        print("❌ Failed to stop WireGuard service. Check logs for details.")
        return False
    return True

def remove_config_files():
    """Remove WireGuard configuration files."""
    try:
        if SERVER_CONFIG_FILE.exists():
            SERVER_CONFIG_FILE.unlink()
            logger.info(f"Removed server config file: {SERVER_CONFIG_FILE}")
        else:
            print("⚠️ Server config file not found.")
        if PARAMS_FILE.exists():
            PARAMS_FILE.unlink()
            logger.info(f"Removed params file: {PARAMS_FILE}")
        else:
            print("⚠️ Params file not found.")
        if WG_CONFIG_DIR.exists():
            shutil.rmtree(WG_CONFIG_DIR)
            logger.info(f"Removed WireGuard user config directory: {WG_CONFIG_DIR}")
        else:
            print("⚠️ WireGuard config directory not found.")
        print("✅ Configuration files removed.")
    except Exception as e:
        logger.error("Failed to remove configuration files: %s", e)
        print("❌ Failed to remove configuration files. Check logs for details.")

def remove_firewall_rules():
    """Remove firewall rules associated with WireGuard."""
    try:
        logger.info("Removing WireGuard firewall rules...")
        if subprocess.run(["firewall-cmd", "--zone=public", "--remove-interface=wg0"], check=False).returncode != 0:
            print("⚠️ Firewall interface 'wg0' not found or already removed.")
            logger.warning("Firewall interface 'wg0' not found or already removed.")
        if subprocess.run(["firewall-cmd", "--remove-port=51820/udp"], check=False).returncode != 0:
            print("⚠️ Firewall port 51820/udp not found or already removed.")
           
