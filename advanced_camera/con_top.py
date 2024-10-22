# ip_camera_url_left = "rtsp://Admin:rtf123@192.168.2.250/251:554/1/1"
# ip_camera_url_right = "rtsp://Admin:rtf123@192.168.2.251/251:554/1/1"
# # Создаем объект VideoCapture для захвата видео с IP-камеры
# video_capture = cv2.VideoCapture(ip_camera_url_left)
# video_capture = cv2.VideoCapture(ip_camera_url_right)


import cv2
import time

from ultralytics import YOLO
from SC_undist import *

# Замените на вашу RTSP-ссылку
# rtsp_url = "rtsp://Admin:rtf123@192.168.2.250/251:554/1/1"
# cap = cv2.VideoCapture(rtsp_url)
cap = cv2.VideoCapture(0)

model = YOLO('best_nano.pt')

t1 = time.time()
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    res = model.predict(frame)
    # frame = undistort_img3(frame)[:, 300:-300]
    cv2.imshow('Video Stream', frame)
    #cv2.imshow('Video Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()


# import cv2
# import time
# from undist import *
# import math
#
# from video_to_kadrs import output_dir
#
# # Замените на вашу RTSP-ссылку
# rtsp_url = "video.mp4"
# cap = cv2.VideoCapture(rtsp_url)
# fps = cap.get(cv2.CAP_PROP_FPS)
# frame_interval = math.floor(fps)
# index = 0
# output_dir = 'new'
#
#
# t1 = time.time()
# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break
#
#     cv2.imshow('Video Stream', undistort_img2(frame))
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
#     if index % frame_interval == 0:
#     # Сохраняем кадр в формате JPG
#         cv2.imwrite(f"{output_dir}/frame{index}.jpg", undistort_img2(frame))
#     index += 1
#
#
# cap.release()
#
# cv2.destroyAllWindows()