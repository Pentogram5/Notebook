from SC_capture import G, getXofObject, getXofObject_complex
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
# beginTime = time.time()
# while time.time() - beginTime < 3:
# set_green_light()

# print('Я ГОТОВ В ЛЮБОЙ МОМЕНТ')
# a = input()

# angle = 20
# w = 10
# t = angle/w
# # # beginTime = time.time()
# # # while time.time() - beginTime < 4:
# G.ram.set_speeds(0, w)
# time.sleep(t)

# l = 70
# v = 15
# t = l/v
# G.ram.set_speeds(v, 0)
# time.sleep(t)

# # захватываем кубик
# G.mainProcess('cube')

# time.sleep(1)

# # l = 1
# v = 20
# # t = l/v
# G.ram.set_speeds(v, 0)
# time.sleep(0.75)

# print('NIGGER')

# # l = 0.4
# # v = 20
# # t = l/v
# # G.ram.set_speeds(v, 0)
# # time.sleep(t)

# G.mainProcess('basket')

# # едем к точке, откуда видно КОРЗИНУ, но которая будет достаточно далеко от неё

# # кладём в корзину

while True:
    print()
    print()
    print()
    print(getXofObject_complex('cube'))
    print()
    print()
    print()