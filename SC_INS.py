# from simulator.SC_sim import *
from SC_API_tcp import *
# import simulator.SC_sim
from SC_advenced_movement import *
import time
import math

import numpy as np


def time_ns_to_s(t):
    return t*10^(-9)

class Integrator:
    '''
    Класс, что находит интеграл 
    integral from last_true_sample_time to current_time of dx_dt*dt
    '''
    # eps_time = 0.01 # Если данные получены в пределах eps_time, то 
    eps_differential = 0.0001 # Погрешность снятия производной. Если все значения в буфере меньше этой погрешности, сумму нужно обнулить
    def __init__(self):
        self.fifo_dS_data = [] # data, timestamp_s
        self.S = 0
        self.last_time = 0
        # self.zero_streak_count  = 0 # Длинна нулей, идущих в буфере подряд, начиная с нуля
        
    def update(self,
                dx_dt,
                current_time,         # Текущее время, во время которого снята производная dx/dt
                last_true_sample_time=None # Последнее время, когда была снята переменная x
              ):
        if self.last_time==0:
            self.last_time = current_time
            return None
        dt = current_time-self.last_time
        dx = dx_dt * dt
        
        self.S += dx
        self.fifo_dS_data.append((dx, current_time))
        
        # # Проверка на обнуление S
        # if Integrator.is_zero_differantial(dx):
        #     self.zero_streak_count += 1
        # else:
        #     self.zero_streak_count == 0
        
        # print(self.zero_streak_count, len(self.fifo_dS_data))
        # if self.zero_streak_count == len(self.fifo_dS_data):
        #     self.clear()
        
        # Очищаем старые данные
        # self.clear_old_data(last_true_sample_time)
        # if abs(old_time-last_true_sample_time)<Integrator.eps_time:
        #     self.fifo_dS_data = []
        #     self.S = 0
        #     # delta_S += dx
        #     # update_fl = True
        
        self.last_time = current_time
    
    @staticmethod
    def is_zero_differantial(a):
        # Функция проверки на ноль
        if type(a)==np.ndarray:
            is_zero_fl = True
            for el in a:
                is_zero_fl = is_zero_fl and (abs(el)<Integrator.eps_differential)
            return is_zero_fl
        else:
            return abs(a)<Integrator.eps_differential
    
    def clear_old_data(self,last_true_sample_time):
        if len(self.fifo_dS_data)>0:
            old_time = self.fifo_dS_data[0][1]
            dx       = self.fifo_dS_data[0][0]
            delta_S  = dx
            update_fl = False
            # if old_time<last_true_sample_time:
            #     if type(dx)==np.ndarray:
            #         print(old_time-last_true_sample_time, last_true_sample_time, len(self.fifo_dS_data))
            while old_time<last_true_sample_time:
                # print(time.time()-old_time,old_time-last_true_sample_time)
                # Вычитаем старые данные
                dx  = self.fifo_dS_data[0][0]
                del self.fifo_dS_data[0]
                
                if len(self.fifo_dS_data)==0:
                    update_fl=True
                    break
                # Повторяем проверку
                old_time = self.fifo_dS_data[0][1]
                delta_S += dx
                update_fl = True
                # if type(dx)==np.ndarray:
                #     print('AAA', old_time-last_true_sample_time, len(self.fifo_dS_data))
                # print(' ',old_time)
                # print(delta_S, self.S)
                
                # if Integrator.is_zero_differantial(dx):
                #     self.zero_streak_count = max(self.zero_streak_count-1,0)
            if update_fl:
                # print('od, ltst', type(self.S), old_time, last_true_sample_time)
                self.S -= delta_S
        self.clear_if_zero()
    
    def clear_if_zero(self):
        is_buffer_zero_fl = True
        for el in self.fifo_dS_data:
            dx, ts = el
            is_buffer_zero_fl = is_buffer_zero_fl and Integrator.is_zero_differantial(dx)
        if is_buffer_zero_fl:
            self.clear()
    
    def get_closest_timestamp_value(self, timestamp_s):
        #!!! UNSAFE if value is too far beyond in future from predicted
        i = 0
        if len(self.fifo_dS_data)==0:
            return 0, timestamp_s
        old_time = self.fifo_dS_data[0][1]
        dx       = self.fifo_dS_data[0][0]
        delta_S = 0
        while timestamp_s<old_time:
            i += 1
            if i+1>len(self.fifo_dS_data):
                break
            dx  = self.fifo_dS_data[i][0]
            # Повторяем проверку
            old_time = self.fifo_dS_data[i][1]
            delta_S += dx
        return delta_S, old_time
    
    def clear(self):
        self.fifo_dS_data = [] # data, timestamp_s
        self.S = 0
        self.last_time = 0

def get_unit_vector(alpha):
    # Преобразуем угол из градусов в радианы
    radians = math.radians(alpha)
    
    # Вычисляем координаты единичного вектора
    x = math.cos(radians)
    y = math.sin(radians)
    
    return np.array((x, y))

class UpdateSource:
    def get_measured_pos(self):
        # Функция, что блокируется до тех пор, пока не пуступят новые данные о позиции
        p = np.array((0,0))
        timestamp_s = 0
        return p, timestamp_s
    def get_measured_yaw(self):
        yaw = 0
        timestamp_s = 0
        return yaw, timestamp_s



from SC_KalmanFilters import KalmanFilter_PosYaw

# TODO - реализовать фильтрацию по STD по последним 2-3 значениям. Если находит не того робота (val>mean+-STD), то вернуть None, и оставить только предикт
class INS:
    def __init__(self,
             predicted_delay=0.2,       # Оценочное время задержки по данным
             pos_Integrator = Integrator, # Интегратор по позиции
             yaw_Integrator = Integrator, # Интегратор по yaw
             update_source: UpdateSource = None, # Источник обновления данных
             ram=None,                   # RobotDirection
             speed_update_rate=30,
             clear_v_eps=0.1,            # Скорость, которая считается незначительной для ИНС. Используются для обнуления накопительной ошибки, когда робот стоит
             clear_wait_time=1           # 
             ):
        self.pos_integrator = pos_Integrator()
        self.yaw_integrator = yaw_Integrator()
        
        self.last_position_update_time = 0
        self.last_yaw_update_time      = 0
        
        self._position = np.array((0,0))
        self._yaw      = 0
        
        self.summary_position = np.array((0,0))
        self.summary_yaw      = 0
        
        # Update sources
        self.update_source = update_source
        if ram is None:
            self.ram = RobotAdvencedMovement()
        self.ram = ram
        self.ram.ins = self
        self.tr_speed = ThreadRate(speed_update_rate)
        self.tr_pos   = ThreadRate(speed_update_rate)
        self.tr_yaw   = ThreadRate(speed_update_rate)
                    
        # # Wheights of sources
        # self.P_of_pos_predict = 0.5
        # self.P_of_yaw_predict = 0.5
        self.kalman_filter = KalmanFilter_PosYaw(update_rate=speed_update_rate)
    
    def start_updater(self):
        self.th_pos = threading.Thread(target=self._update_pos)
        self.th_yaw = threading.Thread(target=self._update_yaw)
        self.th_vel = threading.Thread(target=self._update_vel)
        
        self.th_pos.start()
        self.th_yaw.start()
        self.th_vel.start()
        
    def _update_vel(self):
        print('STARTED UPDATING VEL')
        while True:
            v = self.ram.v/100
            w = math.degrees(self.ram.w)
            # print(v, w)
            #!!!
            timestamp_s = time.time()
            self._update_speeds(v, w, timestamp_s)
            self.tr_speed.sleep()

    def _update_pos(self):
        while True:
            pos, ts = self.update_source.get_measured_pos()
            if pos is not None:
                self.update_pos(pos, ts)
            # print(ts)
            self.tr_pos.sleep()
    
    def _update_yaw(self):
        while True:
            yaw, ts = self.update_source.get_measured_yaw()
            if yaw is not None:
                self.update_yaw(yaw, ts)
            self.tr_yaw.sleep()
    
    def get_past_pos(self, timestamp):
        return self._position + self.pos_integrator.get_closest_timestamp_value(timestamp)[0]
    
    def get_past_yaw(self, timestamp):
        return self._yaw      + self.yaw_integrator.get_closest_timestamp_value(timestamp)[0]
      
    # Обновляет интеграторы-предсказатели в соответствии с текущими скоростями
    def _update_speeds(self, v, w, current_time):
        V = get_unit_vector(self.get_yaw())*v # Получаем вектор направления
        # print(get_unit_vector(self.get_yaw()), v, self.get_yaw())
        self.pos_integrator.update(V, current_time)
        self.yaw_integrator.update(w, current_time)
        
        summary_position = self._position + self.pos_integrator.S
        summary_yaw      = self._yaw      + self.yaw_integrator.S
        
        summary_position, summary_yaw = self.kalman_filter.update_current_state(summary_position, V, summary_yaw, w)
        
        self.summary_position, self.summary_yaw = summary_position, float(summary_yaw)
        
        self.speeds_are_updated = True
    
    # Обнровляет текущую позицию
    def update_pos(self, p, measured_time):
        # Get available predictions of position
        # predicted_pos = self.get_past_pos(measured_time)
        measured_pos  = np.array(p)
        
        # Calculate real position
        # real_pos = predicted_pos*self.P_of_pos_predict + measured_pos*(1-self.P_of_pos_predict)
        real_pos = measured_pos
        
        # print(time.time()-measured_time)
        # Update position
        self.last_position_update_time = measured_time
        self.pos_integrator.clear_old_data(self.last_position_update_time)
        self._position = real_pos
    
    def update_yaw(self, yaw, measured_time):
        # Get available predictions of position
        # predicted_yaw = self.get_past_yaw(measured_time)
        measured_yaw  = yaw
        
        # Calculate real position
        # real_yaw = predicted_yaw*self.P_of_yaw_predict + measured_yaw*(1-self.P_of_yaw_predict)
        real_yaw = measured_yaw
        
        # print('measured_time', measured_time)
        # Update position
        self.last_yaw_update_time = measured_time
        # try:
        #     print('times',time.time()-self.yaw_integrator.fifo_dS_data[-5][1], self.yaw_integrator.fifo_dS_data[-5][1]-self.last_yaw_update_time, )
        # except:
        #     pass
        self.yaw_integrator.clear_old_data(self.last_yaw_update_time)
        self._yaw = real_yaw
        
    
    def clear(self):
        # Сбрасывает текущее состояние ИНС
        self.pos_integrator.clear()
        self.yaw_integrator.clear()
    
    def get_pos(self):
        return self.summary_position
    
    def get_yaw(self):
        return self.summary_yaw
        
        

def main_test_zero_point():
    integrator = Integrator()
    last_true_sample_time = 0
    last_true_val = 0
    while True:
        t = time.time()
        dx_dt = math.sin(t)
        
        x = -math.cos(t)
        
        integrator.update(dx_dt, t, 0)
        print(integrator.S - x)
        # print(last_true_val, len(integrator.fifo_dS_data))

def main_test_delta():
    integrator = Integrator()
    last_true_sample_time = 0
    last_true_val = 0
    while True:
        t = time.time()
        dx_dt = math.sin(t)
        
        x = -math.cos(t)
        phase4 = t%0.2
        # Момент, когда мы узнаём реальные значения в точке
        if phase4<0.1:
            last_true_val = x
            last_true_sample_time = t
            
        integrator.update(dx_dt, t, last_true_sample_time)
        print(last_true_val+integrator.S-x, x, len(integrator.fifo_dS_data), integrator.S)
        # 1/20 or 1/30 is bad
        time.sleep(1/100)
        # print(last_true_val, len(integrator.fifo_dS_data))

def main_test_simulator():
    import keyboard
    import SC_API_sim
    
    # ram = SC_API_sim.ram

    # Инициализация клиентов
    SC_API_sim.init_clients()
    IR_G, IR_R, IR_B, ULTRASONIC = get_constants()

    def update_speeds():
        global left_speed, right_speed
        
        # Обнуляем скорости
        v = 0
        w = 0
        
        # Проверяем нажатие клавиш и обновляем скорости
        if keyboard.is_pressed('w'):  # Вперед
            v += 30
        if keyboard.is_pressed('s'):  # Назад
            v -= 30
        if keyboard.is_pressed('a'):  # Влево
            w -= 90
        if keyboard.is_pressed('d'):  # Вправо
            w += 90
            
        # print(left_speed, right_speed)
        
        if keyboard.is_pressed('q'):  # Вправо
            perform_action_throw_to_basket()
        
        if keyboard.is_pressed('e'):  # Вправо
            perform_action_capture()

        # print(v,w)
        # Устанавливаем скорости моторов
        ram.set_speeds(v, w)
    
    tch = simulator.SC_sim.TopCameraHandler(controlled_delay=0.4, delay_std=0.25, pos_std=0.05, yaw_std=5)
    ins = INS(update_source=tch.update_sink, ram=ram, speed_update_rate=60)
    ins.start_updater()
    
    # Основной цикл управления
    try:
        while True:
            # IR_G, IR_R, IR_B, ULTRASONIC = get_constants()
            # print(Sensors.IR_G)
            del_pos = tch.delayed_p
            # del_yaw = tch.delayed_yaw
            draw_dote(del_pos)
            x, y = ins.get_pos()
            draw_dote2((x, y))
            
            draw_line1((x, y), add((x, y),get_unit_vector(ins.get_yaw())))
            
            # print(len(ins.pos_integrator.fifo_dS_data))
            # update_speeds()
            # print(IR_R)
            # print(get_our_position_rotation())
            time.sleep(0.03)
    except KeyboardInterrupt:
        # Остановка моторов при завершении программы
        rb.set_speed_cms_left(0)
        rb.set_speed_cms_right(0)
        
def main_move_to_point_simulator():
    import SC_API_sim
    
    # ram = SC_API_sim.ram

    # Инициализация клиентов
    SC_API_sim.init_clients()
    IR_G, IR_R, IR_B, ULTRASONIC = get_constants()
    
    tch = simulator.SC_sim.TopCameraHandler(controlled_delay=0.4, delay_std=0.25, pos_std=0.05, yaw_std=5)
    ins = INS(update_source=tch.update_sink, ram=ram, speed_update_rate=60)
    ins.start_updater()
    
    # Основной цикл управления
    try:
        while True:
            # IR_G, IR_R, IR_B, ULTRASONIC = get_constants()
            # print(Sensors.IR_G)
            del_pos = tch.delayed_p
            # del_yaw = tch.delayed_yaw
            draw_dote(del_pos)
            x, y = ins.get_pos()
            draw_dote2((x, y))
            
            draw_line1((x, y), add((x, y),get_unit_vector(ins.get_yaw())))
            
            mouse_pos = get_click_position()
            if mouse_pos is not None:
                print(mouse_pos)
            if mouse_pos is not None:
                p = mouse_pos
                ram.move_to_point(p, look_at=(0,0), on_done=OnDoneActions.LOOK)
            
            # print(ram.rb.left_cms, ram.rb.right_cms)
            
            # print(len(ins.pos_integrator.fifo_dS_data))
            # update_speeds()
            # print(IR_R)
            # print(get_our_position_rotation())
            time.sleep(0.03)
    except KeyboardInterrupt:
        # Остановка моторов при завершении программы
        rb.set_speed_cms_left(0)
        rb.set_speed_cms_right(0)


def main_move_to_point_simulator():
    import SC_API_sim
    
    # ram = SC_API_sim.ram

    # Инициализация клиентов
    SC_API_sim.init_clients()
    IR_G, IR_R, IR_B, ULTRASONIC = get_constants()
    
    tch = simulator.SC_sim.TopCameraHandler(controlled_delay=0.4, delay_std=0.25, pos_std=0.05, yaw_std=5)
    ins = INS(update_source=tch.update_sink, ram=ram, speed_update_rate=60)
    ins.start_updater()
    
    ram.move_by_points(points=[(0.5,1.5),(1.3,1.5),(1.3,2.3),(2.0,2.3),(2.0,2.7)])
    # Основной цикл управления
    try:
        while True:
            # IR_G, IR_R, IR_B, ULTRASONIC = get_constants()
            # print(Sensors.IR_G)
            del_pos = tch.delayed_p
            # del_yaw = tch.delayed_yaw
            draw_dote(del_pos)
            x, y = ins.get_pos()
            draw_dote2((x, y))
            
            draw_line1((x, y), add((x, y),get_unit_vector(ins.get_yaw())))
            
            # time.sleep(2)
            # mouse_pos = get_click_position()
            # if mouse_pos is not None:
            #     p = mouse_pos
            #     ram.move_to_point(p, look_at=(0,0), on_done=OnDoneActions.LOOK)
            
            # print(ram.rb.left_cms, ram.rb.right_cms)
            
            # print(len(ins.pos_integrator.fifo_dS_data))
            # update_speeds()
            # print(IR_R)
            # print(get_our_position_rotation())
            time.sleep(0.03)
    except KeyboardInterrupt:
        # Остановка моторов при завершении программы
        rb.set_speed_cms_left(0)
        rb.set_speed_cms_right(0)
    

if __name__=='__main__':
    main_move_to_point_simulator()