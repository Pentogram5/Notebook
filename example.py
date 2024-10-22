import keyboard
from SC_API_tcp import *
# from SC_API_sim import *

# Инициализация клиентов
init_clients()
IR_G, IR_R, IR_B, ULTRASONIC = get_constants()

# Начальные скорости для моторов
left_speed = 0
right_speed = 0

def update_speeds():
    global left_speed, right_speed
    
    # Обнуляем скорости
    left_speed = 0
    right_speed = 0
    
    # Проверяем нажатие клавиш и обновляем скорости
    if keyboard.is_pressed('w'):  # Вперед
        left_speed += 80
        right_speed += 80
    if keyboard.is_pressed('s'):  # Назад
        left_speed -= 80
        right_speed -= 80
    if keyboard.is_pressed('a'):  # Влево
        left_speed -= 20
        right_speed += 20
    if keyboard.is_pressed('d'):  # Вправо
        left_speed += 20
        right_speed -= 20
    
    if keyboard.is_pressed('q'):  # Вправо
        perform_action_throw_to_basket()
    
    if keyboard.is_pressed('e'):  # Вправо
        perform_action_capture()

    # Устанавливаем скорости моторов
    rb.set_speed_cms_left(left_speed)
    rb.set_speed_cms_right(right_speed)
    

# Основной цикл управления
try:
    while True:
        IR_G, IR_R, IR_B, ULTRASONIC = get_constants()
        update_speeds()
        print(IR_R)
        time.sleep(0.03)
except KeyboardInterrupt:
    # Остановка моторов при завершении программы
    rb.set_speed_cms_left(0)
    rb.set_speed_cms_right(0)
