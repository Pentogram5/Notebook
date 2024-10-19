import time
import math


def time_ns_to_s(t):
    return t*10^(-9)

class Integrator:
    '''
    Класс, что находит интеграл 
    integral from last_true_sample_time to current_time of dx_dt*dt
    '''
    def __init__(self):
        self.fifo_dS_data = [(0,0)] # data, timestamp_s
        self.S = 0
        self.last_time = 0
    def update(self,
                dx_dt,
                current_time,         # Текущее время, во время которого снята производная dx/dt
                last_true_sample_time # Последнее время, когда была снята переменная x
              ):
        if self.last_time==0:
            self.last_time = current_time
            return None
        dt = current_time-self.last_time
        dx = dx_dt * dt
        
        self.S += dx
        self.fifo_dS_data.append((dx, current_time))
        
        # Очищаем старые данные
        old_time = self.fifo_dS_data[0][1]
        dx       = self.fifo_dS_data[0][0]
        delta_S  = dx
        update_fl = False
        while old_time<last_true_sample_time:
            # Вычитаем старые данные
            dx  = self.fifo_dS_data[0][0]
            del self.fifo_dS_data[0]
            # Повторяем проверку
            old_time = self.fifo_dS_data[0][1]
            delta_S += dx
            update_fl = True
            # print(delta_S)
        # print('NIGGER', update_fl)
        if update_fl:
            self.S -= delta_S
        #     # assert ValueError("NIGGER")
        
        self.last_time = current_time
    
    def clear(self):
        self.fifo_dS_data = [(0,0)] # data, timestamp_s
        self.S = 0
        self.last_time = 0

# class INS_Integrator:
#     def init(self, T, pos_integrator=Integrator, yaw_integrator=Integrator):
#         self.delta_p = 0
#         self.delta_yaw = 0
#         if integrator==None:
#             self.integrator =  self._sample_int
#     def update(self, v, w, dt):
#         self.delta

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
        phase4 = t%1
        # Момент, когда мы узнаём реальные значения в точке
        if phase4<0.6:
            last_true_val = x
            last_true_sample_time = t
            
        integrator.update(dx_dt, t, last_true_sample_time)
        print(last_true_val+integrator.S - x, len(integrator.fifo_dS_data), integrator.S)
        # 1/20 or 1/30 is bad
        time.sleep(1/5)
        # print(last_true_val, len(integrator.fifo_dS_data))

if __name__=='__main__':
    main_test_delta()