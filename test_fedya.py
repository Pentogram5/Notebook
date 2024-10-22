from advanced_camera.SC_detectors import *
from advanced_camera.test_mod import get_img_and_res
from SC_API_tcp import *
from SC_advenced_movement import ram
from SC_INS import *
from advanced_camera.SC_CS import show_sm_point
from SC_Gird_connect import *


tch = TopCameraHandler(0, framework=CamFrameWorks.cv2, fake_img_update_period=2, use_undist=True,
                       robot_color=RobotColors.RED)
# # while True:
# #     # print(tch.results, tch.timestamp)
# #     ...
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

def getBoxCenter(xyxy):
        return [xyxy[0] + (xyxy[2] - xyxy[0]) / 2, xyxy[1] + (xyxy[3] - xyxy[1]) / 2]
    
def lenght(A, B):
    print(A, B)
    return ((A[0] - B[0]) ** 2 + (A[1] - B[1])**2) ** 0.5

print('NIGGER')
while True:
        
    ret, frame_in = tch.read_yolo()
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
        frame, vec = get_img_and_res(frame_in.copy(), results)
        # print(vec)
    
    # ram.w = 10
    
    # update_speeds()
    # ram.set_speeds(20, 20)
    # res = tch.get_our_raw_position()
    # print(res)
    data = tch.get_objects()
    # print(data)
    res_sm = get_our_robot_pos_4_sm(frame, results, 'green') #fix
    print("res_sm: ", res_sm)
    res = get_our_robot_pos_4(frame, results, 'green') #fix
    res22 = get_direction(frame, results)
    barriers = find_barriers(frame, results)  
    min_path_to_cube = get_closest_PL(data, res_sm, barriers)



    # for cube
    if min_path_to_cube != 0:
        for i in range(1, len(min_path_to_cube)):
            frame = show_sm_line(frame, get_koeffs(results), min_path_to_cube[i - 1], min_path_to_cube[i])
    
    
    for result in results:
        boxes = result.boxes  # Get bounding box outputs
        for box in boxes:
            # Extract coordinates and class information
            x1, y1, x2, y2 = map(int, box.xyxy.flatten().cpu().numpy())  # Convert to integers
            score = box.conf.item()  # Confidence score
            cls = result.names[box.cls.int().item()]  # Class name

            # Draw the bounding box and label on the image
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green rectangle
            cv2.putText(frame, f'{cls} {score:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    

    robots = []
    accs = []
    averageLenghtCubeToCenter = []
    for result in results:
        boxes = result.boxes  # Get bounding box outputs
        for box in boxes:
            # Extract coordinates and class information
            score = box.conf.item()  # Confidence score
            cls = result.names[box.cls.int().item()]  # Class name

            if cls == 'cube':
                xyxy = list(map(int, box.xyxy.flatten().cpu().numpy()))  # Convert to integers
                score = box.conf.item()  # Confidence score
                cls = result.names[box.cls.int().item()]  # Class name
                print(getBoxCenter(xyxy), list(frame.shape)[:-1])
                averageLenghtCubeToCenter.append(lenght(getBoxCenter(xyxy), list(frame.shape)[:-1]))
    print('==============', averageLenghtCubeToCenter)




    for item in res22:
        line,  xx, yy = item
        x1, y1, x2, y2 = line
        cv2.line(frame, (xx + x1, yy + y1), (xx + x2, yy + y2), (0, 0, 255), thickness=4)
        cv2.circle(frame, (xx + x2, yy + y2), radius=10, color=(0, 0, 255))
    
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
    time.sleep(2)
    # time.sleep(0.03)