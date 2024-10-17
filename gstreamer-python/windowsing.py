import pygetwindow as gw
import pyautogui

def position_window(name, width, height):
    try:
        # Получаем окно по названию
        window = gw.getWindowsWithTitle(name)[0]  # Берем первое найденное окно

        # Устанавливаем новое положение и размер окна
        window.moveTo(0, 0)  # Перемещаем в верхний левый угол
        window.resizeTo(width, height)  # Устанавливаем размеры

        print(f"Окно '{name}' перемещено и изменено на {width}x{height}.")
    except IndexError:
        print(f"Окно с названием '{name}' не найдено.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def bring_window_to_front(name):
    try:
        # Получаем окно по названию
        window = gw.getWindowsWithTitle(name)[0]  # Берем первое найденное окно
        
        # Выдвигаем окно на передний план
        window.activate()  # Активируем окно
        print(f"Окно '{name}' выдвинуто на передний план.")
    except IndexError:
        print(f"Окно с названием '{name}' не найдено.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def main():
    # Пример использования функции
    position_window("Direct3D11 renderer", 1600, 1000)  # Замените на нужное название и размеры
    bring_window_to_front("Direct3D11 renderer")