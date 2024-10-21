from SC_utils import *
import threading

import cv2
from ultralytics import YOLO
import numpy as np


class WebCamera:
    def __init__(self, max_fps=30):
        self.frame = None
        self.res = None
        self.th = None
        # ЗДЕСЬ ИНИЦИАЛИЗИРУЙ КАМЕРУ
        self.cam = cv2.VideoCapture('http://192.168.245.178:8080/?action=stream')
        self.tr = ThreadRate(max_fps)
    
    def start_capturing_image(self):
        self.th = threading.Thread(target=self._start_capturing_image)
        self.th.start()
    
    def read_image(self):
        # СЮДА ПИШИ СВОЙ КОД ПО ПОЛУЧЕНИЮ КАРТИНКИ
        ret, frame = self.cam.read()
        if not ret:
            return False, None
        # frame = cv2.rotate(frame, cv2.ROTATE_180)
        return frame, self.res

    def show_image(self, frame, res):
        cv2.imshow('video feed', frame)
        #cv2.imshow('gray feed', gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return
    
    def _start_capturing_image(self):
        while True:
            self.frame, self.res = self.read_image()
            # self.show_image(self.frame, self.res)
            self.tr.sleep()
    
    def read(self):
        return self.frame is not None, self.frame
    
    @staticmethod
    def VideoCapture(*args):
        obj = WebCamera()
        obj.start_capturing_image()
        return obj

cap = WebCamera.VideoCapture()