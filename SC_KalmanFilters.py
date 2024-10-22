import numpy as np
from filterpy.kalman import KalmanFilter
import math

class KalmanFilter_PosYaw:
    def __init__(self, update_rate=30):
        # Глобальные переменные
        self.pos_filter = KalmanFilter(dim_x=4, dim_z=2)  # Для pos и v
        self.yaw_filter = KalmanFilter(dim_x=2, dim_z=2)  # Для yaw и w
        
        self.pos = np.array([0.0, 0.0])  # Начальная позиция (x, y)
        self.v = np.array([0.0, 0.0])    # Начальная скорость (vx, vy)
        self.yaw = 0.0                   # Начальный курс в градусах
        self.w = 0.0                     # Угловая скорость
        self.update_rate = update_rate
        
        self._initialize_filters()

    def _initialize_filters(self):
        dt = 1 / self.update_rate  # Временной шаг

        # Инициализация фильтра для позиции и скорости
        self.pos_filter.x = np.zeros(4)  # Начальное состояние [pos_x, pos_y, v_x, v_y]
        self.pos_filter.P = np.eye(4) * 1000  # Начальная ковариационная матрица
        self.pos_filter.F = np.array([[1, 0, dt, 0],
                                       [0, 1, 0, dt],
                                       [0, 0, 1, 0],
                                       [0, 0, 0, 1]])
        
        self.pos_filter.H = np.array([[1, 0, 0, 0],
                                       [0, 1, 0, 0]])
        
        self.pos_filter.R = np.eye(2) * 5   # Ковариационная матрица измерений (шум)
        self.pos_filter.Q = np.eye(4) * 1    # Ковариационная матрица процесса (шум)

        # Инициализация фильтра для yaw и w
        self.yaw_filter.x = np.zeros(2)      # Начальное состояние [yaw, w]
        self.yaw_filter.P = np.eye(2) * 1000 # Начальная ковариационная матрица
        self.yaw_filter.F = np.array([[1, dt],
                                       [0, 1]])
        
        self.yaw_filter.H = np.array([[1, 0],
                                       [0, 1]])
        
        self.yaw_filter.R = np.eye(2) * 5   # Ковариационная матрица измерений (шум)
        self.yaw_filter.Q = np.eye(2) * 1    # Ковариационная матрица процесса (шум)

    def update_current_state(self, pos, v, yaw, w):
        # Обновление состояния для фильтра позиции и скорости
        self.pos = pos
        self.v = v
        
        # Прогнозирование следующего состояния для позиции и скорости
        self.pos_filter.predict()
        
        # Измерения (положение)
        z_pos = self.pos.copy() 

        # Обновление состояния с новыми измерениями
        self.pos_filter.update(z_pos)

        updated_pos_state = self.pos_filter.x.copy()
        
        updated_pos = updated_pos_state[:2]   # [pos_x, pos_y]

        # Обновление состояния для фильтра yaw и угловой скорости
        self.yaw = yaw
        self.w = w
        
        # Прогнозирование следующего состояния для yaw и угловой скорости
        self.yaw_filter.predict()
        
        z_yaw = np.array([self.yaw, self.w]) 

        # Обновление состояния с новыми измерениями
        self.yaw_filter.update(z_yaw)

        updated_yaw_state = self.yaw_filter.x.copy()
        
        # Обновляем yaw из состояния фильтра yaw
        updated_yaw = updated_yaw_state[0] % 360  

        return updated_pos, updated_yaw

# Пример использования класса KalmanFilter_PosYaw:
if __name__ == "__main__":
    kf = KalmanFilter_PosYaw(update_rate=30)

    # Пример входных данных (положение, скорость, курс и угловая скорость)
    pos_input = np.array([1.5, 2.5])
    velocity_input = np.array([1.2, -0.8])
    yaw_input = 30.0   # Курс в градусах
    angular_velocity_input = 5.0   # Угловая скорость в градусах/сек

    updated_position, updated_yaw_angle = kf.update_current_state(pos_input, velocity_input, yaw_input, angular_velocity_input)

    print("Обновленная позиция:", updated_position)
    print("Обновленный курс (yaw):", updated_yaw_angle)
