import time
import pygetwindow as gw
import pyautogui

def position_window(name, width, height):
    try:
        # Получаем окно по названию
        window = gw.getWindowsWithTitle(name)[0]  # Берем первое найденное окно

        # Устанавливаем новое положение и размер окна
        window.moveTo(0, 0)  # Перемещаем в верхний левый угол
        window.resizeTo(width, height)  # Устанавливаем размеры

        # print(f"Окно '{name}' перемещено и изменено на {width}x{height}.")
    except IndexError:
        print(f"Окно с названием '{name}' не найдено.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

import win32gui
import win32con
import time

def bring_window_to_front(window_title):
    # Функция для поиска окна по заголовку
    def find_window(hwnd, param):
        if win32gui.IsWindowVisible(hwnd) and window_title in win32gui.GetWindowText(hwnd):
            param.append(hwnd)

    # Список для хранения найденных окон
    window_handles = []
    win32gui.EnumWindows(find_window, window_handles)  # Передаем список как параметр

    if not window_handles:
        print(f"Окно с названием '{window_title}' не найдено.")
        return

    # Берем первое найденное окно
    hwnd = window_handles[0]

    # Восстанавливаем окно, если оно свернуто
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    
    # Устанавливаем фокус на окно и выдвигаем его на передний план
    # win32gui.SetForegroundWindow(hwnd)
    
    # Дополнительная команда для обеспечения того, чтобы окно было сверху
    win32gui.BringWindowToTop(hwnd)

    # print(f"Окно '{window_title}' выдвинуто на передний план.")

def main():
    # Пример использования функции
    position_window("Direct3D11 renderer", 1600, 1000)  # Замените на нужное название и размеры
    bring_window_to_front("Direct3D11 renderer")