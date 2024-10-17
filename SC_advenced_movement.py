from SC_API_tcp import *
import math as m
from SC_utils import *

class RobotActions:
    IDLE = 0
    MOVING_TO_POINT = 1
    OTHER_ACTIONS = 2

class OnDoneActions:
    STOP = 0
    WAIT = 1

class RobotAdvencedMovement:
    def __init__(self, rb=rb,
                 L=0.3, # Расстояние между центрами гусениц
                 R_of_success=0.15, # В пределах какого радиуса считаем, что мы достигли заданной точки
                 fps = 20
                 ):
        self.rb = rb
        self.L = L
        self.R = R_of_success
        self.v = 0
        self.w = 0
        
        # Параметры регулятора
        self.max_angle_speed = 20
        self.max_speed = self.rb.max_speed
        self.tau = 0.1 # Rate tau
        self.tr = ThreadRate(fps) # Частота обновления регулятора
        
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
        self.rb.set_speed_cms_left(lms)
        self.rb.set_speed_cms_right(rms)
    
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
        while self.current_action == RobotActions.MOVING_TO_POINT:
            # print(get_distance((x,y), self.current_point))
            x, y, angle = self.get_pos_rot()
            v = self.desired_speed
            desired_angle = -get_angle((x,y), self.current_point)
            
            # Поиск требуемового yaw rate
            delta_angle = get_shortest_angle_path(angle, desired_angle)
            print(delta_angle)
            yaw_rate = delta_angle / self.tau
            if abs(yaw_rate) > self.max_angle_speed:
                v = 0
            
            w = yaw_rate
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

if __name__=='__main__':
    main_test_move_to_target()