import numpy as np
import pygame
import random
import time
import math
import math as m

from .SC_physics import vector_collision_on_lines
from .SC_logic import Collider

# Функция для поворота изображения с сохранением центра
def rot_center(image, angle):
    """Rotate an image while keeping its center and size."""
    orig_rect = image.get_rect(center=(image.get_width() // 2, image.get_height() // 2))
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=orig_rect.center)
    return rot_image


def mul(s, A):
    if   type(A) in (float, int):
        return s*A
    elif type(A) in (list, tuple):
        b = []
        for a in A:
           b.append(s*a) 
        return b

def add(A, B):
    assert len(A)==len(B), "Длины веткоров должны совпадать"
    n = len(A)
    C = [0 for i in range(n)]
    for i in range(n):
        C[i] = A[i] + B[i]
    return C

def Int(A):
    return list(map(int, A))

# Класс для перегородок
class Border:
    def __init__(self, p1, p2, off_x=0, off_y=0, s=200):
        self.p1 = p1
        self.p2 = p2
        self.off_x = off_x
        self.off_y = off_y
        self.s = s
        # self.collider = Collider((add((-0.01,-0.01),self.p1), add((-0.01,-0.01),self.p2), add((0.01,0.01),self.p2), add((0.01,0.01),self.p1)))
        self.collider = Collider((add((-0.01,-0.01),self.p1), add((-0.01,-0.01),self.p2), add((0.01,0.01),self.p2), add((0.01,0.01),self.p1)))
    
    def get_collider(self):
        return self.collider
    
    def to_primitive(self):
        return (self.p1, self.p2)

    def draw(self, screen):
        # v1 = mul(self.s, add(self.p1, (self.off_x, self.off_y)))
        # v2 = mul(self.s, add(self.p2, (self.off_x, self.off_y)))
        # # print(v1, v2)
        # pygame.draw.line(screen, (255, 0, 0), v1, v2, 2)
        pointes = (add((-0.01,-0.01),self.p1), add((-0.01,-0.01),self.p2), add((0.01,0.01),self.p2), add((0.01,0.01),self.p1))
        vertices = []
        for p in pointes:
            vertices.append(mul(self.s, add(p, (self.off_x, self.off_y))))
        pygame.draw.polygon(screen, (255, 0, 0), vertices)

# Класс для танка
import pygame
import math

def draw_line(screen, p1, p2, off_x, off_y, s, color=(255, 0, 0)):
    v1 = mul(s, add(p1, (off_x, off_y)))
    v2 = mul(s, add(p2, (off_x, off_y)))
    pygame.draw.line(screen, color, v1, v2, 2)

global line_ps
line_ps = ((0,0),(0,0))

def draw_line1(p1, p2):
    global line_ps
    line_ps = (p1, p2)

def draw_line1_advanced(color=(255, 0, 0)):
    global screen
    global field_offset_x
    global field_offset_y
    global s
    global line_ps
    if screen is None:
        return
    off_x, off_y = field_offset_x, field_offset_y
    v1 = mul(s, add(line_ps[0], (off_x, off_y)))
    v2 = mul(s, add(line_ps[1], (off_x, off_y)))
    pygame.draw.line(screen, color, v1, v2, 2)

class Tank:
    def __init__(self, x, y, width=0.25, height=0.29, max_speed=1, track_width=0.21,
                 mu=1, p=0, #p=0.2,
                 s=200,
                 off_x=0, off_y=0):
        self.x = x
        self.y = y
        self.off_x = off_x
        self.off_y = off_y
        
        self.width = width
        self.height = height
        self.max_speed = max_speed  # максимальная скорость каждой гусеницы
        self.track_width = track_width  # расстояние между гусеницами
        self.angle = math.radians(90)  # угол поворота в радианах (90 градусов)
        self.v_left = 0  # скорость левой гусеницы
        self.v_right = 0  # скорость правой гусеницы
        self.mu = mu
        self.p = p
        
        self.collider = Collider(poly=(
            (0, 0),
            (0, self.width),
            (self.height, self.width),
            (self.height, 0),
            ),
            # off_x = -self.height/2,
            # off_y = -self.width/2,
            )

        # size scales
        self.s = s
        # Создаем поверхность для танка
        self.tank_surface = pygame.Surface((self.width * self.s, self.height * self.s), pygame.SRCALPHA)

        # Рисуем зеленый квадрат (корпус танка)
        pygame.draw.rect(self.tank_surface, (0, 255, 0), (0, 0, self.width * self.s, self.height * self.s))

        # Рисуем гусеницы по бокам
        track_height = (self.height * self.s) / 2
        # pygame.draw.rect(self.tank_surface, (0, 0, 0), 
        #                  (self.width * 50, (self.height * 50) / 2 - track_height / 2, 
        #                   10, track_height))  # Правая гусеница
        ts = 0.1
        pygame.draw.rect(self.tank_surface, (0, 0, 0), 
                         (0, 0, 
                          self.s * ts, self.height * self.s))  # Левая гусеница
        pygame.draw.rect(self.tank_surface, (0, 0, 0), 
                         (self.s * (self.width-ts), 0, 
                          self.s * ts, self.height * self.s))  # Левая гусеница

        # Рисуем палку спереди танка
        stick_length = 20
        stick_width = 5
        pygame.draw.rect(self.tank_surface, (255, 255, 0), 
                         (self.width * 50 / 2 - stick_width / 2,
                          -stick_length / 2 + (self.height * 50 / 2), 
                          stick_width,
                          stick_length))
    
    def get_collider(self):
        self.collider.x     = self.x - self.width/2
        self.collider.y     = self.y - self.height/2
        self.collider.angle = self.angle - m.radians(90)
        return self.collider

    def set_speeds(self, v_left, v_right):
        """Устанавливает скорости для левой и правой гусениц."""
        # cms to ms
        v_left  = v_left/100
        v_right = v_right/100
        self.v_left = max(min(v_left, self.max_speed), -self.max_speed)
        self.v_right = max(min(v_right, self.max_speed), -self.max_speed)
    
    def get_direction_normal(self):
        direction = (math.sin(self.angle), -math.cos(self.angle))
        normal    = (-math.cos(self.angle),  -math.sin(self.angle))
        return direction, normal

    def update(self, dt, physics_bounds_function=lambda p, a, v, o, c: (v, o)):
        """Обновляет положение и угол танка на основе скоростей гусениц."""
        v_abs = (self.v_left + self.v_right) / 2
        direction, normal = self.get_direction_normal()
        v = mul(v_abs, direction)
        omega = - self.mu * (self.v_right - self.v_left) / self.track_width * max(1, abs(v_abs*100)**self.p)
        # print(max(1, abs(v_abs*100)**self.p))
        #!!!
        # print(self.v_left, self.v_right)
        # print(self.v_right, self.v_left)
        # / max(1, abs(v)**self.p)
        # off = add(mul(self.height/2, direction), mul(-self.width/2, normal))
        # off = (self.width, self.height)
        # off = (self.width/2,self.height)
        off = (0,0)
        pos_off = add((self.x, self.y), off)
        # print(pos_off)
        v, omega = physics_bounds_function(pos_off, self.angle, v, omega, self.get_collider())
    
        # Обновляем угол и координаты
        self.angle = (self.angle + omega * dt) % (m.pi*2)
        self.x += v[0] * dt
        self.y += v[1] * dt
        # print(self.x, self.y, self.angle)

    def draw(self, screen):
        """Рисует танк на экране."""
        
        # Поворачиваем танк
        rotated_tank_image = pygame.transform.rotate(self.tank_surface.copy(), -math.degrees(self.angle))
        
        # Получаем новый прямоугольник после поворота для центрирования
        new_rect = rotated_tank_image.get_rect(center=((self.x + self.off_x)*self.s, (self.y + self.off_y)*self.s))
        
        screen.blit(rotated_tank_image, new_rect.topleft)



# Класс для инфракрасного датчика
class ScInfrared:
    def __init__(self, id=''):
        self.rawValue = random.randint(0, 100)
        self.filteredValue = 0
        self.id = id
        self.distance = 10
        self.timestamp = 0

    def update(self, timestamp):
        self.timestamp = timestamp
        # Имитация получения новых значений
        self.rawValue = random.randint(0, 100)
        self.filteredValue = (self.filteredValue + self.rawValue) / 2

    def serialize(self):
        return {
            'rawValue': self.rawValue,
            'filteredValue': self.filteredValue,
            'timestamp': time.time_ns()
        }
    
    def __repr__(self):
        return f'ScInfrared({self.id},distance={self.distance},rawValue={self.rawValue},filteredValue={self.filteredValue},timestamp={self.timestamp})'

    def __str__(self):
        return self.__repr__()

# Класс для ультразвукового датчика
class ScUltrasonic:
    def __init__(self, id=''):
        self.rawValue = random.randint(0, 100)
        self.id = id
        self.filteredValue = 0
        self.distance = 10
        self.timestamp = 0

    def update(self, timestamp):
        self.timestamp = timestamp
        # Имитация получения новых значений
        self.rawValue = random.randint(0, 100)
        self.rawValue = self.filteredValue

    def serialize(self):
        return {
            'rawValue': self.rawValue,
            'filteredValue': self.filteredValue,
            'timestamp': time.time_ns()
        }
        
    def __repr__(self):
        return f'ScUltrasonic({self.id},distance={self.distance},rawValue={self.rawValue},filteredValue={self.filteredValue},timestamp={self.timestamp})'

    def __str__(self):
        return self.__repr__()


IR_G, IR_R, IR_B = ScInfrared(), ScInfrared(), ScInfrared()
ULTRASONIC = ScUltrasonic()
def get_constants():
    global IR_G, IR_R, IR_B, ULTRASONIC
    return IR_G, IR_R, IR_B, ULTRASONIC
global tank
tank = None

def get_tank():
    global tank
    return tank

def get_our_position_rotation():
    global tank
    if tank is None:
        return 0, 0, 0
    return tank.x, tank.y, (m.degrees(tank.angle)-90) % 360

def perform_action_throw_to_basket():
    ...

def perform_action_capture():
    ...

global s
s = 150 # s = 150 # Коэффициент перевода метра в пиксели: px/m
field_height = 5 # Размер полигона
field_width  = 5
field_offset_x = 0.5 # Смещение СК полигона относительно его угла
field_offset_y = 0.5
mu_borders = 0.5 # Условный коэффициент трения стенок 
def get_click_position():
    if pygame.mouse.get_pressed()[0]:
        return add(mul(1/s, pygame.mouse.get_pos()), (-field_offset_x, -field_offset_y))
    else:
        return None





class UpdateSourceModified:
    def __init__(self, get_measured_pos=..., get_measured_yaw=...):
        self.get_measured_pos = get_measured_pos
        self.get_measured_yaw = get_measured_yaw
        
class TopCameraHandler:
    # Handles actions of top camera
    cam1_url = "rtsp://Admin:rtf123@192.168.2.250/251:554/1/1"
    cam2_url = "rtsp://Admin:rtf123@192.168.2.251/251:554/1/1"
    def __init__(self, cam=None, framework=0, fps_cam=30, fps_yolo=30, use_undist=True, fake_img_update_period=5,
                 cam_uncontrolled_delay=0.250, cam_controlled_delay=0.100,
                 controlled_delay=0.3, # Величина задержки, что у нас суммарно известно есть
                 delay_std=0.025,      # Составляющая неизвестности в ней
                 pos_std=0.05,
                 yaw_std=10
                 ):
        ...
        self.posiiton_data_buffer = [{'data':(0,0),'timestamp':0}]
        self.yaw_data_buffer      = [{'data':(0,0),'timestamp':0}]
        self.update_sink = UpdateSourceModified()
        
        self.controlled_delay = controlled_delay
        
        self.update_sink.get_measured_pos = self._get_measured_pos
        self.update_sink.get_measured_yaw = self._get_measured_yaw
        self.delayed_p = [0,0]
        self.delayed_yaw = 0
        self.delay_std = delay_std
        
        self.pos_std = pos_std
        self.yaw_std = yaw_std
        
    def _get_measured_pos(self):
        pos, ts = self.get_our_raw_position()
        pos = pos+random.uniform(-self.pos_std,+self.pos_std)
        rnd_delay = random.uniform(-self.delay_std, +self.delay_std)
        time.sleep(self.controlled_delay+rnd_delay)
        self.delayed_p = pos
        return pos, ts+rnd_delay
    
    def _get_measured_yaw(self):
        yaw, ts = self._get_our_raw_rotation()
        yaw = yaw+random.uniform(-self.yaw_std,+self.yaw_std)
        rnd_delay = random.uniform(-self.delay_std, +self.delay_std)
        time.sleep(self.controlled_delay+rnd_delay)
        self.delayed_yaw = yaw
        return yaw, ts+rnd_delay
        
    def get_our_raw_position(self):
        # Возвращает
        # - позицию нашего робота в см на основании CV
        # - timestamp с которого их получили
        # global tank
        # if tank is None:
        #     return np.array((0,0)), 0
        ts = time.time()
        x, y, yaw = get_our_position_rotation()
        return np.array((x, y)), ts

    def _get_our_raw_rotation(self):
        # Возвращает
        # - курс нашего робота на основании CV в градусах
        # - timestamp с которых их получили
        # 0  градусов соответствует +Ox
        # 90 градусов соответствует +Oy
        ts = time.time()
        x, y, yaw = get_our_position_rotation()
        return yaw, ts






global dote1_pos
dote1_pos = (0,0)
def draw_dote(p):
    global dote1_pos
    dote1_pos = p

global dote2_pos
dote2_pos = (0,0)
def draw_dote2(p):
    global dote2_pos
    dote2_pos = p

def _draw_dote(which=1):
    global dote1_pos
    global dote2_pos
    global s
    global screen
    p = dote1_pos
    color = (255, 0, 0)
    if which==2:
        p = dote2_pos
        color = (0, 255, 0)
    if screen is not None:
        draw_line(screen, add(p, (-0.1,0)), add(p, (0.1,0)), off_x=field_offset_x, off_y=field_offset_y, s=s, color=color)
        draw_line(screen, add(p, (0,-0.1)), add(p, (0,0.1)), off_x=field_offset_x, off_y=field_offset_y, s=s, color=color)

global screen
screen = None

tank = None


# Основной игровой цикл
def main():
    global tank
    global IR_G, IR_R, IR_B, ULTRASONIC
    global screen
    pygame.init()
    
    # Настройки окна игры
    screen_width = field_height*s
    screen_height = field_width*s
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("2D Tank Game")

    # Создание объектов
    tank = Tank(0, 0, off_x=field_offset_x, off_y=field_offset_y, s=s)
    # borders = [
    # borders = [Border((i * 1, 0), (i * 1, 5), off_x=field_offset_x, off_y=field_offset_y, s=s) for i in range(1)]
    # borders.append(Border((1, 0), (5, 0), off_x=field_offset_x, off_y=field_offset_y, s=s))
    
    IR_G, IR_R, IR_B = ScInfrared(), ScInfrared(), ScInfrared()
    ULTRASONIC = ScUltrasonic()

    clock = pygame.time.Clock()
    
    running = True
    
    border_lines = [
        ((0  ,0  ), (400,0  )),
        ((400,0  ), (400,310)),
        ((400,310), (0  ,310)),
        ((0  ,310), (0  ,0  )),
        
        ((100,45), (100+55,45   )),
        ((100,45), (100   ,45+70)),
        
        ((100   ,45+70+70+70), (100+55,45+70+70+70)),
        ((100   ,45+70+70+70), (100   ,45+70+70)),
    ]
    borders = []
    for bl in border_lines:
        p1, p2 = mul(1/100, bl[0]), mul(1/100, bl[1])
        borders.append(Border(p1, p2, off_x=field_offset_x, off_y=field_offset_y, s=s))
        
    
    while running:
        dt = clock.tick(60) / 1000.0  # Время в секундах с последнего кадра
        timestamp = int(clock.get_time() * 1000)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        
        # lms, rms = 0, 0
        # # Управление танком с помощью клавиш стрелок и W/S для ускорения/замедления
        # if keys[pygame.K_LEFT]:
        #     # Поворот налево 
        #     lms += -10
        #     rms += 10
        # elif keys[pygame.K_RIGHT]:
        #     lms += 10
        #     rms += -10

        # if keys[pygame.K_UP]:
        #     lms += 20
        #     rms += 20
        # if keys[pygame.K_DOWN]:
        #     lms -= 20
        #     rms -= 20
        
        # # print(lms, rms)
        # tank.set_speeds(lms, rms)

        # lambda p, a, v, o: (v, o)
        def line_bounds_physics(p, a, v, o, c):
            lines = []
            for b in borders:
                if Collider.are_collided(b.get_collider(), c):
                    lines.append(b.to_primitive())
            v = vector_collision_on_lines(p, v, lines, mu_borders)
            return v, o
        
        # Обновление положения танка и значений датчиков 
        tank.update(dt, physics_bounds_function=line_bounds_physics)
        
        # ir_sensor.update()
        # ultrasonic_sensor.update()
        IR_G.update(timestamp), IR_R.update(timestamp), IR_B.update(timestamp)
        ULTRASONIC.update(timestamp)

        # Отрисовка объектов на экране 
        screen.fill((255 ,255 ,255))   # Очистка экрана белым цветом 
        
        t, n = tank.get_direction_normal()
        # p1 = (tank.x, tank.y)
        # p2 = add(p1, mul(1*s, t))
        # draw_line(screen, p1, p2, field_offset_x, field_offset_y, s)
        
        for border in borders:
            border.draw(screen)
        
        tank.draw(screen)
        
        _draw_dote()
        _draw_dote(2)
        draw_line1_advanced()

        # Отображение данных с датчиков (для примера) 
        font=pygame.font.Font(None ,36)
        # ir_text=font.render(f'IR Raw: {ir_sensor.rawValue}, Filtered: {ir_sensor.filteredValue}', True,(0 ,0 ,0))
        # ultrasonic_text=font.render(f'Ultrasonic Raw: {ultrasonic_sensor.rawValue}', True,(0 ,0 ,0))
        
        # screen.blit(ir_text,(10 ,10))
        # screen.blit(ultrasonic_text,(10 ,50))

        pygame.display.flip() 

    pygame.quit()

if __name__ == "__main__":
    main()
