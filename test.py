from advanced_camera.SC_detectors import *
from advanced_camera.test_mod import get_img_and_res
from SC_API_tcp import *
from SC_advenced_movement import ram
from SC_INS import *
from advanced_camera.SC_CS import show_sm_point


tch = TopCameraHandler(2, framework=CamFrameWorks.cv2_man, fake_img_update_period=2, use_undist=True,
                       robot_color=RobotColors.GREEN, stable_delay=0.1)
# # while True:
# #     # print(tch.results, tch.timestamp)
# #     ...

# init_clients()
set_green_light()
tch.start_camera_handling()
ins = INS(ram=ram, update_source=tch.update_sink)
ins.start_updater()

# print('NIGGERS0')
# Инициализация клиентов
# init_clients()
# IR_G, IR_R, IR_B, ULTRASONIC = get_constants()

# import keyboard

# def update_speeds():
#     global left_speed, right_speed
    
#     # Обнуляем скорости
#     v = 0
#     w = 0
    
#     # Проверяем нажатие клавиш и обновляем скорости
#     if keyboard.is_pressed('w'):  # Вперед
#         v += 36
#     if keyboard.is_pressed('s'):  # Назад
#         v -= 36
#     if keyboard.is_pressed('a'):  # Влево
#         w -= 60
#     if keyboard.is_pressed('d'):  # Вправо
#         w += 60
        
#     # print(left_speed, right_speed)
    
#     if keyboard.is_pressed('q'):  # Вправо
#         perform_action_throw_to_basket()
    
#     if keyboard.is_pressed('e'):  # Вправо
#         perform_action_capture()
    
#     if keyboard.is_pressed('q'):  # Вправо
#         perform_action_throw_to_basket()

#     if keyboard.is_pressed('e'):  # Вправо
#         perform_action_capture()
        
#     if keyboard.is_pressed('g'):  # Вправо
#         set_green_light()
    
#     if keyboard.is_pressed('r'):  # Вправо
#         set_red_light()

#     # Устанавливаем скорости моторов
#     ram.set_speeds(v, w)

print('NIGGER')
# ram.move_by_points(v=20, points=[(50,150),(150,150),(150,230),(200,230),(200,270)])
if not tch.read_yolo()[0]:
    time.sleep(1)
time.sleep(1)
# ram.move_by_points(v=20, points=[(50,150),(150,150),(150,230),(200,230),(200,270)])
# ram.move_by_points(v=20, points=[(50,150), (175,20),(175,70)])
# ram.move_by_points(v=20, points=[(50,150),(130,150),(130,230),(200,230),(200,270)])
# ram.move_to_point(v=10, p=(50,150))

# ram.move_by_points(v=20, points=[(150,150),(150,230),(200,230),(200,270)])

# ram.move_by_points(v=5, points=[(120, 100), (60, 100)])
ram.move_by_points(v=10, points=[(350, 400), (650, 400), (650, 700), (350, 700), (350, 500)])
while True:
    
    ret, frame_in = tch.read_yolo()
    # print('NIGGERS', frame)
    if not ret:
        continue

    frame = frame_in.copy()
    
    # # res = model.predict(frame)
    # # frame = undistort_img3(frame)[:, 300:-300]
    # phase4 = (int(time.time()) % 4)
    # if phase4 == 0:
    #     tch.continue_yolo()
    # if phase4 == 2:
    #     tch.pause_yolo()
    # # print(tch.get_results())
    # print(phase4, tch.is_yolo_running, tch.timestamp_yolo)
    
    # results, timestamp = tch.get_results()
    # if results is not None:
    #     frame, vec = get_img_and_res(frame_in.copy(), results)
    #     # print(vec)
    
    # ram.w = 10
    
    # update_speeds()
    # ram.set_speeds(20, 20)
    # print(ins.get_pos(), ins.get_yaw())
    # res = get_our_robot_pos_4(frame, results, 'red')
    # if res is not None:
    #     x1, y1, x2, y2 = res
    #     p = ((x1 + x2) // 2, (y1 + y2) // 2)
    #     cv2.circle(frame, list(map(int,p)), 5, (0, 255, 255), 5)
    res, _ = tch.get_our_raw_position()
    p = ins.get_pos()
    print(p, res, frame.shape)
    # print(p)
    if res is not None:
        p = res
        show_sm_point(frame, tch.koefs, p, color=(0,0,255))

    # try:
    #     # print(p)
    #     show_px_point(frame, p, color=(0,0,255))
    # except Exception as ex:
    #     print(ex)

    # print(tch.koefs)
    # show_sm_point(frame, tch.koefs, (100, 45))
    # show_sm_point(frame, tch.koefs, (100+55, 45))
    # show_sm_point(frame, tch.koefs, (100, 45+70*3))
    # show_sm_point(frame, tch.koefs, (0,0))
    # show_sm_point(frame, tch.koefs, (100+55+70+55+15, 45))
    
    # show_sm_point(frame, tch.koefs, (100+55+70+55+15, 45+70*3))
    # show_sm_point(frame, tch.koefs, (400, 310))
    
    # points = [(i*10, 45) for i in range(10)]
    # for p in points:
    #     show_sm_point(frame, tch.koefs, p)
    cv2.imshow('Video Stream', frame)
    # #cv2.imshow('Video Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # time.sleep(1)
    time.sleep(0.03)