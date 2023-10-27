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


class WallpaperManager:
    """Менеджер обоев, отвечающий за работу с обоями и реестром."""

    def save_default_wallpaper(self, path):
        """Сохранение указанной картинки как обои по умолчанию в файл."""
        with open(CONFIG_FILE, 'w') as file:
            file.write(path)
        logger.info(f"Saved default wallpaper: {path}")

    def get_default_wallpaper_from_file(self):
        """Получение обоев по умолчанию из файла."""
        try:
            with open(CONFIG_FILE, 'r') as file:
                path = file.readline().strip()
                return path
        except FileNotFoundError:
            logger.warning("Config file not found.")
            return None

    def set_default_wallpaper(self, default_wallpaper):
        """Установка обоев по умолчанию в реестр Windows."""
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "Wallpaper", 0, winreg.REG_SZ, default_wallpaper)
        logger.info(f"Set default wallpaper in registry: {default_wallpaper}")

    def get_current_wallpaper(self):
        """Получение текущих обоев из реестра Windows."""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY_PATH, 0, winreg.KEY_READ) as key:
                value, reg_type = winreg.QueryValueEx(key, "Wallpaper")
                return value
        except Exception as e:
            logger.error(f"Error reading current wallpaper from registry: {e}")
            return None

    def monitor_wallpaper_change(self):
        """Мониторинг изменения обоев и восстановление обоев по умолчанию при необходимости."""
        while True:
            default_wallpaper = self.get_default_wallpaper_from_file()
            if not default_wallpaper:
                logger.info("Default wallpaper not found, prompting user to choose.")
                default_wallpaper = self.choose_wallpaper()
            current_wallpaper = self.get_current_wallpaper()
            if current_wallpaper != default_wallpaper:
                logger.info("Wallpaper change detected.")
                logger.info(f"Wallpaper from Re: {current_wallpaper}")
                logger.info(f"Default wallpaper from file: {default_wallpaper}")
                self.set_default_wallpaper(default_wallpaper)
            time.sleep(600)

    def choose_wallpaper(self):
        """Отображение диалогового окна выбора обоев и сохранение выбора пользователя."""
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.save_default_wallpaper(file_path)
        root.destroy()
        return file_path

    def start_monitoring(self):
        """Запуск мониторинга изменения обоев в отдельном потоке."""
        logger.info("Starting wallpaper monitor.")
        threading.Thread(target=self.monitor_wallpaper_change, daemon=True).start()


class TrayApp:
    """Приложение для системного трея, позволяющее пользователю выбирать обои."""

    def __init__(self, manager):
        """Инициализация с передачей экземпляра менеджера обоев."""
        self.manager = manager

    def run(self):
        """Запуск иконки в системном трее."""
        image = Image.open("icon.png")
        tray_icon = icon("name", image, "Wallpaper Chooser", menu=menu(
            item('Выбрать обои', self.manager.choose_wallpaper),
            item('Выход', lambda icon, item: icon.stop())
        ))
        tray_icon.run()


class WallpaperApplication:
    """Основное приложение, объединяющее менеджер обоев и приложение для трея."""

    def __init__(self):
        self.manager = WallpaperManager()
        self.tray_app = TrayApp(self.manager)

    def run(self):
        """Запуск приложения: начинает мониторинг обоев и отображает иконку в трее."""
        logger.add("log.log", rotation="10 MB")
        logger.info("Application started.")
        self.manager.start_monitoring()
        self.tray_app.run()


if __name__ == "__main__":
    app = WallpaperApplication()
    app.run()
