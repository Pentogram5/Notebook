from SC_advenced_movement import ram
from SC_API_tcp import *

from pid import PID
pid = PID(0.01, 0, 0)

import cv2
from ultralytics import YOLO
import numpy as npwsssw

cap = cv2.VideoCapture('http://192.168.2.12:8080/?action=stream')
model = YOLO('yolo_for_camera_robot.pt')


def center(obj_class, results):

    xc = 0
    yc = 0
    max_conf = 0
    fl = False
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls = result.names[box.cls.int().item()]
            score = box.conf.item()
            if cls == obj_class and score > max_conf:
                x1, y1, x2, y2 = map(int, box.xyxy.flatten().cpu().numpy())  # Convert to integers
                xc = (x1 + x2) // 2
                yc = (y1 + y2) // 2
                max_conf = score
                fl = True
    if fl:
        return xc, yc
    else:
        return None, None


def getXofObject():
    ret, frame = cap.read()
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #out.write(frame)
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    res = model(frame)

    # time.sleep(1)

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

    cv2.imshow('video feed', frame)
    #cv2.imshow('gray feed', gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return
    xc, yc = center('cube', res)
    # print(xc, yc)
    return xc

class Grabber:
    image_w = 640
    image_h = 480
    speed = 0

    def __init__(self, ram, pid):
        self.tau = 1
        self.ram = ram
        self.pid = pid
        self.pid.setpoint = self.image_w // 2
        self.pid.output_limits = (-60, 60)
        pid.tunings = (-1.0, -0.1, 0)

    def capture(self):
        while True:
            err = getXofObject()
            if err is None:
                err = self.pid.setpoint
            rate = err/self.tau
            w = self.pid(rate)
            print(rate, w)
            self.ram.set_speeds(self.speed, w)
            print(self.speed, w)
            last_err = err


init_clients()
# ram.set_speeds(0,0)
G = Grabber(ram, pid)
G.capture()