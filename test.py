from advanced_camera.SC_detectors import *
from advanced_camera.test_mod import get_img_and_res
from advanced_camera.SC_get_direction import *


tch = TopCameraHandler(1, framework=CamFrameWorks.gst, fake_img_update_period=2, use_undist=True)
# while True:
#     # print(tch.results, tch.timestamp)
#     ...
tch.start_camera_handling()

print('NIGGERS0')
while tch.isOpened():
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
        frame, vec = get_img_and_res(frame, results)
        # print(vec)
    
    # print(frame.shape)

    print(tch.get_our_raw_position())
    res = get_our_robot_pos_3(frame, results, 'red')
    if res != None:
        x1, y1, x2, y2 = res
        cv2.circle(frame, ((x1 + x2) // 2, (y1 + y2) // 2), 5, (0, 255, 255), 5)
    cv2.imshow('Video Stream', frame)
    #cv2.imshow('Video Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # time.sleep(1)