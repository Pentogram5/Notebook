from SC_API_sim import *
import math as m
from SC_utils import *

class RobotActions:
    IDLE = 0
    MOVING_TO_POINT = 1
    OTHER_ACTIONS = 2

class OnDoneActions:
    STOP = 0
    WAIT = 1
    
import numpy as np


import numpy as np
from collections import deque

class Filter:
    def cast(self, arr):
        if not (type(arr) in (list, tuple)):
            arr = (arr,)
        assert all([type(a) in (int, float) for a in arr]), "Unsupported data type"
        return arr

class MEAN_STD(Filter):
    def __init__(self, fifo_n=5, T=1.0):
        self.fifo = deque()  # Используем deque для более эффективного удаления старых данных
        self.fifo_n = fifo_n
        self.T = T  # Параметр времени окна
        self.last_time = None  # Время последней фильтрации

    def filter(self, arr, dt):
        # Casting
        arr = self.cast(arr)
        np_arr = np.array(arr)

        # Устанавливаем текущее время
        current_time = 0 if self.last_time is None else self.last_time + dt

        # Добавляем новые данные в fifo с текущим временем
        self.fifo.append((current_time, np_arr))

        # Удаляем старые данные
        while self.fifo and (current_time - self.fifo[0][0]) > self.T:
            self.fifo.popleft()

        # Проверяем количество элементов в fifo
        if len(self.fifo) == 0:
            return type(arr)(np_arr)  # Если fifo пустой, возвращаем исходные данные

        # Преобразуем fifo в массив numpy для вычислений
        fifo_values = np.array([value for _, value in self.fifo])

        # Проверяем, есть ли данные для вычисления
        if len(fifo_values) == 0:
            return type(arr)(np_arr)  # Если нет данных, возвращаем исходные данные

        # Создаем массив весов
        weights = np.array([dt] * len(fifo_values))

        # Проверка на ненулевую сумму весов
        if np.sum(weights) == 0:
            # print(np_arr)
            return type(arr)(np_arr)[0]  # Если сумма весов равна нулю, возвращаем исходные данные

        # Вычисляем среднее и стандартное отклонение с учетом dt
        mean = np.average(fifo_values, axis=0, weights=weights)
        std = np.sqrt(np.average((fifo_values - mean) ** 2, axis=0, weights=weights))

        # Находим неподходящие значения
        replace_mask = abs(np_arr - mean) > std

        # Фильтруем данные
        np_arr[replace_mask] = mean[replace_mask]

        # Обновляем время последней фильтрации
        self.last_time = current_time
        # print(np_arr)
        
        return type(arr)(np_arr)[0]


    def clear(self):
        self.fifo.clear()


# Robustness filter
# class MEAN_STD(Filter):
#     def __init__(self, fifo_n=5):
#         self.fifo = []
#         self.fifo_n = fifo_n

#     def filter(self, arr):
#         # Casting
#         arr = self.cast(arr)
#         np_arr = np.array(arr)
#         self.fifo.append(arr)
#         # Finding array parameters
#         mean = np.mean(self.fifo, axis=0)
#         std = np.std(self.fifo, axis=0)
#         # Finding inappropriate values
#         replace_mask = abs(np_arr - mean) > std
#         # Filtering
#         np_arr[replace_mask] = mean[replace_mask]
#         # Append to array

#         # Check for data trust
#         if len(self.fifo) > self.fifo_n:
#             # print(self.fifo,'DEL')
#             del self.fifo[0]
#             # We can trust the datas
#             return type(arr)(np_arr)
#         else:
#             # We can't, return at least mean
#             return type(arr)(mean)

#     def clear(self):
#         del self.fifo
#         self.fifo = []

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


def min_sgn(a, min_val):
    a_abs = abs(a)
    a_sgn = sgn(a)
    
    a_abs = min(a_abs, min_val)
    return a_abs * a_sgn

def max_sgn(a, max_val):
    a_abs = abs(a)
    a_sgn = sgn(a)
    
    a_abs = max(a_abs, max_val)
    return a_abs * a_sgn


class RobotAdvencedMovement:
    def __init__(self, rb=rb,
                 L=0.21, # Расстояние между центрами гусениц
                 R_of_success=0.15, # В пределах какого радиуса считаем, что мы достигли заданной точки
                 R_max=0.3, # Максимальный радиус поворота
                 fps = 20
                 ):
        self.rb = rb
        self.L = L
        self.R = R_of_success
        self.v = 0
        self.w = 0
        self.R_max = R_max
        
        self.eps_angles = 5
        self.eps_rate = 5
        
        self.filter = MEAN_STD()
        
        # Параметры регулятора
        self.max_angle_speed = 90
        self.max_speed = self.rb.max_speed
        self.tau = 0.1 # Rate tau
        self.tr = ThreadRate(fps) # Частота обновления регулятора
        self.ts = TimeStamper()
        
        # Параметры логики
        self.current_action = RobotActions.IDLE
        # Параметры хождения по точкам
        self.current_point = (0,0)
        self.desired_speed = 0
        self.new_command_timeout = 2 # Время ожидания поступления новой комманды. Чтобы робот двигался плавно
        self.on_done = OnDoneActions.STOP
    
    # def set_speeds
    def get_pos_rot(self):
        x, y, angle = get_our_position_rotation()
        return x, y, angle
    
    def set_speeds(self,
                   v, # cm/s
                   w  # deg/s
                   ):
        w = m.radians(w)
        dv = w*self.L*100
        v_res = v
        if (v+dv/2 < self.rb.max_speed) and (v+dv/2 > -self.rb.max_speed) and \
           (v-dv/2 < self.rb.max_speed) and (v-dv/2 > -self.rb.max_speed):
            lms = v + dv/2
            rms = v - dv/2
        else:
            if v>0:
                v_res -= dv
                lms = v + min(0, dv)
                rms = v + min(0, -dv)
            else:
                v_res += dv
                lms = v - min(0, -dv)
                rms = v - min(0, dv)
        
        self.v = v_res
        self.w = w
        
        # print(lms, rms)
        eps = 5
        if abs(lms)>eps:
            lms_abs = abs(lms)
            lms_sgn = sgn(lms)
            lms = lms_sgn * max(10, lms_abs)
        else:
            lms = 0
        if abs(rms)>eps:
            rms_abs = abs(rms)
            rms_sgn = sgn(rms)
            rms = rms_sgn * max(10, rms_abs)
            # print(rms)
        else:
            rms = 0
        self.rb.set_speed_cms_left(lms)
        self.rb.set_speed_cms_right(rms)
        
        self.ts = TimeStamper()
    
    def move_to_point(self, p, v=None, on_done=OnDoneActions.STOP):
        if v==None:
            v = self.max_speed
        # Двигаемся к заданной точке p
        if  (self.current_action == RobotActions.IDLE):
            self.current_point = p
            self.desired_speed = v
            self.current_action = RobotActions.MOVING_TO_POINT
            self.mp_thread = threading.Thread(target=self._movement_to_point)
            self.mp_thread.start()
        
        if (self.current_action == RobotActions.MOVING_TO_POINT):
            self.desired_speed = v
            self.current_point = p
            
    
    def stop_moving_to_point(self):
        # Перестаём двигаться к заданной точке
        if  (self.current_action == RobotActions.IDLE) \
            or \
            (self.current_action == RobotActions.MOVING_TO_POINT):
            self.mp_thread.stop()
            self.current_action = RobotActions.IDLE
            return True
    
    def _movement_to_point(self):
        # Обрабатываем движение к заданной точке
        x, y, angle = self.get_pos_rot()
        dt = self.ts.timestamp()
        while self.current_action == RobotActions.MOVING_TO_POINT:
            dt = self.ts.timestamp()
            # print(get_distance((x,y), self.current_point))
            x, y, angle = self.get_pos_rot()
            v = self.desired_speed
            desired_angle = -get_angle((x,y), self.current_point)
            
            # Поиск требуемового yaw rate
            delta_angle = get_shortest_angle_path(angle, desired_angle)
            # print(delta_angle)
            yaw_rate = delta_angle / self.tau
            yaw_rate = min_sgn(yaw_rate, self.max_angle_speed)
            R = 0
            if (abs(yaw_rate)>self.eps_rate) and (abs(delta_angle) > self.eps_angles):
                R_non_abs = self.filter.filter(v/yaw_rate, dt)
                R = abs(R_non_abs)
            if R > self.R_max:
                v = 0
            # if abs(yaw_rate) > self.max_angle_speed:
            #     v = 0
            
            w = yaw_rate
            print(R, v, w, delta_angle)
            self.set_speeds(v, w)
            self.tr.sleep()
            
            # Принимаем решение о выходе из цикла
            if get_distance((x,y), self.current_point) <= self.R:
                # Если достигли точки, то что делаем?
                self.current_action = RobotActions.IDLE
                if self.on_done == OnDoneActions.WAIT:
                    old_time = time.time()
                    while time.time()-old_time < self.new_command_timeout:
                        # Нам отдали команду о продолжении движения по точкам
                        if self.current_action == RobotActions.MOVING_TO_POINT:
                            break
                        # Мы решили захватить куб или ещё чего - тогда нам нужно выйти
                        if self.current_action == RobotActions.OTHER_ACTIONS:
                            break
                    # Если текущее действие - не хождение по точкам, то выходим из цикла
                    if self.current_action != RobotActions.MOVING_TO_POINT:
                        break
                else:
                    break
                    
                        
                
        
            
        
        
ram = RobotAdvencedMovement()


def main_test_wasd():
    import keyboard

    # Инициализация клиентов
    init_clients()
    IR_G, IR_R, IR_B, ULTRASONIC = get_constants()

    def update_speeds():
        global left_speed, right_speed
        
        # Обнуляем скорости
        v = 0
        w = 0
        
        # Проверяем нажатие клавиш и обновляем скорости
        if keyboard.is_pressed('w'):  # Вперед
            v += 36
        if keyboard.is_pressed('s'):  # Назад
            v -= 36
        if keyboard.is_pressed('a'):  # Влево
            w -= 60
        if keyboard.is_pressed('d'):  # Вправо
            w += 60
            
        # print(left_speed, right_speed)
        
        if keyboard.is_pressed('q'):  # Вправо
            perform_action_throw_to_basket()
        
        if keyboard.is_pressed('e'):  # Вправо
            perform_action_capture()

        # Устанавливаем скорости моторов
        ram.set_speeds(v, w)

    # Основной цикл управления
    try:
        while True:
            IR_G, IR_R, IR_B, ULTRASONIC = get_constants()
            update_speeds()
            # print(IR_R)
            # print(get_our_position_rotation())
            time.sleep(0.03)
    except KeyboardInterrupt:
        # Остановка моторов при завершении программы
        rb.set_speed_cms_left(0)
        rb.set_speed_cms_right(0)

def main_test_move_to_target():
    import keyboard

    # Инициализация клиентов
    init_clients()
    IR_G, IR_R, IR_B, ULTRASONIC = get_constants()

    # Основной цикл управления
    try:
        while True:
            IR_G, IR_R, IR_B, ULTRASONIC = get_constants()
            mouse_pos = get_click_position()
            if mouse_pos is not None:
                p = mouse_pos
                ram.move_to_point(p)
            time.sleep(0.03)
    except KeyboardInterrupt:
        # Остановка моторов при завершении программы
        rb.set_speed_cms_left(0)
        rb.set_speed_cms_right(0)

def main_test_input():
    import keyboard

    # Инициализация клиентов
    init_clients()
    IR_G, IR_R, IR_B, ULTRASONIC = get_constants()

    def update_speeds():
        v, w = list(map(float, input().split(' ')))
        # Устанавливаем скорости моторов
        ram.set_speeds(v, w)

    # Основной цикл управления
    try:
        while True:
            IR_G, IR_R, IR_B, ULTRASONIC = get_constants()
            update_speeds()
            # print(IR_R)
            # print(get_our_position_rotation())
            time.sleep(0.03)
    except KeyboardInterrupt:
        # Остановка моторов при завершении программы
        rb.set_speed_cms_left(0)
        rb.set_speed_cms_right(0)

if __name__=='__main__':
    main_test_move_to_target()
    # main_test_wasd()
    # main_test_input()