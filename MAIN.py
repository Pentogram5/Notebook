from SC_capture import G
from SC_frontCamera import cap
import time

from advanced_camera.SC_detectors import *
from advanced_camera.test_mod import get_img_and_res
from SC_API_tcp import *
from SC_advenced_movement import ram
from SC_INS import *
from advanced_camera.SC_CS import show_sm_point
from SC_Gird_connect import *

from SC_API_tcp import *
init_clients()

myColor = 'green'
# print('Цвет команды: ', myColor)

tch = TopCameraHandler(0, framework=CamFrameWorks.cv2, fake_img_update_period=2, use_undist=True,
                       robot_color=RobotColors.GREEN)

tch.start_camera_handling()
ins = INS(ram=ram, update_source=tch.update_sink)
ins.start_updater()

# Определяем координаты кубов

# print('NIGGER')
while True:
        
    ret, frame = tch.read_yolo()
    # print('NIGGERS', frame)
    if not ret:
        continue
    
    # # res = model.predict(frame)
    # # frame = undistort_img3(frame)[:, 300:-300]
    # phase4 = (int(time.time()) % 4)
    # if phase4 == 0:
    #     tch.continue_yolo()
    # if phase4 == 2:
    #     tch.pause_yolo()
    # # print(tch.get_results())
    # print(phase4, tch.is_yolo_running, tch.timestamp_yolo)
    
    results, timestamp = tch.get_results()
    if results is not None:
        frame, vec = get_img_and_res(frame.copy(), results)
        # print(vec)
    
    # ram.w = 10
    
    # update_speeds()
    # ram.set_speeds(20, 20)
    # res = tch.get_our_raw_position()
    # print(res)
    data = tch.get_objects()
    # print(data)

    res = get_our_robot_pos_4(frame, results, tch.robot_color) #fix

    min_path_to_cube = get_closest_PL(frame, data, res) 

    # выполнение пути до куба

    path_to_base = get_to_base(frame, data, res, tch.robot_color) # добавить определение base_coordinate

    if res is not None:
        x1, y1, x2, y2 = res
        p = ((x1 + x2) // 2, (y1 + y2) // 2)
        cv2.circle(frame, list(map(int,p)), 5, (0, 255, 255), 5)
    res, _ = tch.get_our_raw_position()
    if res is not None:
        p = res
        show_sm_point(frame, tch.koefs, p, color=(0,0,255))
    print(tch.koefs)
    show_sm_point(frame, tch.koefs, (100, 45))
    show_sm_point(frame, tch.koefs, (100+55, 45))
    show_sm_point(frame, tch.koefs, (100, 45+70*3))
    show_sm_point(frame, tch.koefs, (0,0))
    show_sm_point(frame, tch.koefs, (100+55+70+55+15, 45))
    
    show_sm_point(frame, tch.koefs, (100+55+70+55+15, 45+70*3))
    show_sm_point(frame, tch.koefs, (400, 310))
    
    points = [(i*10, 45) for i in range(10)]
    for p in points:
        show_sm_point(frame, tch.koefs, p)
    cv2.imshow('Video Stream', frame)
    # #cv2.imshow('Video Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(5)
    # time.sleep(0.03)

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
