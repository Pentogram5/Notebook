from SC_capture import G
from SC_frontCamera import cap
import time

from SC_API_tcp import *
init_clients()

# myColor = input('Введите цвет команды: ')
# print('Цвет команды: ', myColor)

# Определяем координаты кубов

# Определяем координаты своей базы

# Определяем точно цвет робота 

# while input() != 'start':
#     pass
# START

# едем к точке, откуда видно КУБИК, но которая будет достаточно далеко от него
beginTime = time.time()
while time.time() - beginTime < 3:
    G.ram.set_speeds(0, 20)

beginTime = time.time()
while time.time() - beginTime < 4:
    G.ram.set_speeds(10, 0)

# захватываем кубик
G.mainProcess('cube')

# едем к точке, откуда видно КОРЗИНУ, но которая будет достаточно далеко от неё

# кладём в корзину
