import cv2
from ultralytics import YOLO
import os
import math
import numpy as np
import time
from .SC_get_direction import *
from .SC_CS import map_system_zero
from .SC_undist import *
from .SC_CS import *

# model1 = YOLO('best_nano.pt')
def get_img_and_res(frame, results):
    #model2 = YOLO('best_small.pt')
    # model3 = YOLO('best_cam.pt')

    # rtsp_url = "video.mp4"
    #rtsp_url = "rtsp://Admin:rtf123@192.168.2.250/251:554/1/1"
    # rtsp_url = "rtsp://Admin:rtf123@192.168.2.251/251:554/1/1"
    # cap = cv2.VideoCapture(rtsp_url)
    # fps = cap.get(cv2.CAP_PROP_FPS)
    # frame_interval = math.floor(fps)
    #output_dir = 'new22'


    # while cap.isOpened():
    #     ret, frame = cap.read()
    #     if not ret:
    #         break
    
    # frame = cv2.imread('new8\\frame150.jpg')
    # frame = undistort_img3(frame)
    # frame = cv2.resize(frame, (900, 500))
    # # frame = frame[:, 300: -300]
    # #results = model2(frame)
    # results = model1(frame)
    # results = model3(frame)
    for result in results:
        boxes = result.boxes  # Get bounding box outputs
        for box in boxes:
            # Extract coordinates and class information
            x1, y1, x2, y2 = map(int, box.xyxy.flatten().cpu().numpy())  # Convert to integers
            score = box.conf.item()  # Confidence score
            cls = result.names[box.cls.int().item()]  # Class name

            # Draw the bounding box and label on the image
            # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green rectangle
            # cv2.putText(frame, f'{cls} {score:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    res = get_direction(frame, results)

    for item in res:
        line,  xx, yy = item
        x1, y1, x2, y2 = line
        # cv2.line(frame, (xx + x1, yy + y1), (xx + x2, yy + y2), (0, 0, 255), thickness=4)
        # cv2.circle(frame, (xx + x2, yy + y2), radius=10, color=(0, 0, 255))
    
    # TODO - преобразование координат
    return frame, (x2-x1, y2-y1)

    # # h, w = frame.shape[:2]
    # # x_c, y_c = map_system_zero(results, h, w)
    # # print(x_c, y_c)
    # # cv2.circle(frame, (x_c, y_c), radius = 50, color = (0, 0, 255))
    # cv2.imshow('video', frame)
    # cv2.waitKey(0)

    #     #
    #     # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     #     break

    #     # if index % frame_interval == 0:
    #     # # Сохраняем кадр в формате JPG
    #     #     cv2.imwrite(f"{output_dir}/frame{index}.jpg", undistort_img3(frame))
    #     # index += 1


    # # cap.release()

    # cv2.destroyAllWindows()

