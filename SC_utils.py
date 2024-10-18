import math
import time

def get_distance(p1, p2):
    """
    Вычисляет расстояние между двумя точками p1 и p2.
    
    :param p1: Кортеж (x1, y1) первой точки
    :param p2: Кортеж (x2, y2) второй точки
    :return: Расстояние между точками
    """
    x1, y1 = p1
    x2, y2 = p2
    
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance

def get_angle(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    
    # Вектор от p1 к p2
    dx = x2 - x1
    dy = y2 - y1
    
    # Угол в радианах
    angle_rad = math.atan2(dy, dx)
    
    # Преобразование в градусы
    angle_deg = 360-math.degrees(angle_rad)
    
    # Приведение к диапазону [0, 360]
    angle_final = (angle_deg + 360) % 360
    
    return angle_final

def sgn(x):
    """Return the sign of a float.
    
    Args:
        x (float): The input number.

    Returns:
        int: -1 if x is negative, 1 if x is positive, 0 if x is zero.
    """
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

# def get_shortest_angle_path(x, y):
#     """
#     Находит кратчайшую разницу между двумя углами в градусах.
    
#     :param x: Угол x в градусах
#     :param y: Угол y в градусах
#     :return: Кратчайшая разница между углами в градусах
#     """
#     diff1 = y - x
#     diff2 = diff1 + 360
#     diff3 = diff1 - 360
    
#     # Выбор кратчайшей разницы по абсолютной величине
#     if abs(diff1) < abs(diff2) and abs(diff1) < abs(diff3):
#         return diff1
#     elif abs(diff2) < abs(diff3):
#         return diff2
#     else:
#         return diff3
def get_shortest_angle_path(x, y):
    """
    Находит кратчайшую разницу между двумя углами в градусах.
    
    :param x: Угол x в градусах
    :param y: Угол y в градусах
    :return: Кратчайшая разница между углами в градусах
    """
    # Вычисляем разницу между углами
    diff = (y - x) % 360
    
    # Если разница больше 180, то выбираем обратное направление
    if diff > 180:
        diff -= 360
    
    return diff

class TimeStamper:
    def __init__(self):
        self.old_t = time.time()

    def timestamp(self):
        dt = time.time() - self.old_t
        self.old_t = time.time()
        return dt

def set_speeds(V):
    L = 1
    W = 1
    left_ms = V - min(0,W*L)
    right_ms = V - min(0,-W*L) 


class ThreadRate:
    """Утилита для сна с фиксированной частотой."""
    def __init__(self, freq=1):
        self.freq = freq
        self._period = 1 / self.freq
        self.ts = TimeStamper()

    def sleep(self):
        sleep_time = max(self._period - self.ts.timestamp(), 0)
        time.sleep(sleep_time)

# # Пример использования
# angle1 = 90
# angle2 = 0
# while True:
#     angle2 = (angle2+1) % 360
#     print(angle2, get_shortest_angle_path(angle1, angle2))
#     # print(f"Кратчайшая разница между углами: {get_shortest_angle_path(angle1, angle2)}°")
#     time.sleep(0.01)


# # Пример использования
# point1 = (0, 0)
# point2 = (0.5, 0.5)
# print(f"Угол между вектором и осью Ox: {get_angle(point1, point2)}°")