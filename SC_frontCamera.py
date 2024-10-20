from SC_utils import *
import threading

import cv2
from ultralytics import YOLO
import numpy as npwsssw


class WebCamera:
    def __init__(self, max_fps=30):
        self.frame = None
        self.res = None
        self.th = None
        # ЗДЕСЬ ИНИЦИАЛИЗИРУЙ КАМЕРУ
        self.cam = cv2.VideoCapture('http://192.168.2.12:8080/?action=stream')
        self.model = YOLO('yolo_for_camera_robot.pt')
        self.tr = ThreadRate(max_fps)
    
    def start_capturing_image(self):
        self.th = threading.Thread(target=self._start_capturing_image)
        self.th.start()
    
    def read_image(self):
        # СЮДА ПИШИ СВОЙ КОД ПО ПОЛУЧЕНИЮ КАРТИНКИ
        ret, frame = self.cam.read()
        if not ret:
            return False, None
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        print('===================')
        res = self.model(frame)
        print('===================')
        return frame, res

    def show_image(self, frame, res):
        if not res:
            return
        for result in res:
            boxes = result.boxes  # Get bounding box outputs
            for box in boxes:
                # Extract coordinates and class information
                x1, y1, x2, y2 = map(int, box.xyxy.flatten().cpu().numpy())  # Convert to integers
                score = box.conf.item()  # Confidence score
                cls = result.names[box.cls.int().item()]  # Class name

                # Draw the bounding box and label on the image
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green rectangle
                cv2.putText(frame, f'{cls} {score:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        print('===================')
        cv2.imshow('video feed', frame)
        #cv2.imshow('gray feed', gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return
        
    def _start_capturing_image(self):
        while True:
            self.frame, self.res = self.read_image()
            self.show_image(self.frame, self.res)
            self.tr.sleep()
    
    def read(self):
        return self.img is not None, self.img
    
    @staticmethod
    def VideoCapture(*args):
        obj = WebCamera()
        obj.start_capturing_image()
        return obj

WebCamera.VideoCapture()