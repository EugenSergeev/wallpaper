import tkinter as tk
from tkinter import filedialog
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image
import winreg
import time
import threading
from loguru import logger

CONFIG_FILE = "default_wallpaper.txt"
KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"


def save_default_wallpaper(path):
    with open(CONFIG_FILE, 'w') as file:
        file.write(path)
    logger.info(f"Saved default wallpaper: {path}")


def get_default_wallpaper_from_file():
    try:
        with open(CONFIG_FILE, 'r') as file:
            path = file.readline().strip()
            logger.info(f"Got default wallpaper from file: {path}")
            return path
    except FileNotFoundError:
        logger.warning("Config file not found.")
        return None


def set_default_wallpaper(default_wallpaper):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, "Wallpaper", 0, winreg.REG_SZ, default_wallpaper)
    logger.info(f"Set default wallpaper in registry: {default_wallpaper}")


def get_current_wallpaper():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY_PATH, 0, winreg.KEY_READ) as key:
            value, reg_type = winreg.QueryValueEx(key, "Wallpaper")
            return value
    except Exception as e:
        logger.error(f"Error reading current wallpaper from registry: {e}")
        return None


def monitor_wallpaper_change():
    while True:
        default_wallpaper = get_default_wallpaper_from_file()
        if not default_wallpaper:
            logger.info("Default wallpaper not found, prompting user to choose.")
            default_wallpaper = choose_wallpaper(None, None)
        if get_current_wallpaper() != default_wallpaper:
            logger.info("Wallpaper change detected.")
            set_default_wallpaper(default_wallpaper)
        time.sleep(600)


def choose_wallpaper(icon, item):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if file_path:
        save_default_wallpaper(file_path)
    root.destroy()
    return file_path


def create_tray_icon():
    image = Image.open("icon.png")
    tray_icon = icon("name", image, "Wallpaper Chooser", menu=menu(
        item('Выбрать обои', choose_wallpaper),
        item('Выход', lambda icon, item: icon.stop())
    ))
    tray_icon.run()


if __name__ == "__main__":
    logger.add("app.log", rotation="10 MB")
    logger.info("Application started.")
    # Запускаем поток для отслеживания изменений обоев
    threading.Thread(target=monitor_wallpaper_change, daemon=True).start()
    create_tray_icon()
