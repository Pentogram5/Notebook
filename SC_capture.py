from SC_advenced_movement import ram
from SC_API_tcp import *
from SC_API_tcp import perform_action_capture

from pid import PID

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
        return xc, yc, max_conf
    else:
        return None, None, max_conf


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
    xc, yc, conf = center('cube', res)
    # print(xc, yc)
    return xc, conf

class Grabber:
    image_w = 640
    image_h = 480
    image_aim = 20  # %
    states = {
        1: 'search',
        2: 'sneak',
        3: 'aim',
        4: 'grab',
        5: 'check',
        6: 'error',
    }
    pids = {
        1: PID(-0.005, 0, 0, setpoint=image_w//2, output_limits=(-40, 40)),
        2: PID(-0.005, 0, 0, setpoint=image_w//2, output_limits=(-40, 40)),
    }
    currentState = None

    averageParamConf = {
        'windowSize': 5,
        'arr': [],
        'average': 0.0,
        'ind': 0,
    }

    averageParamX = {
        'windowSize': 10,
        'arr': [],
        'average': 0.0,
        'ind': 0,
    }

    def __init__(self, ram):
        self.ram = ram
        self.currentState = 1
    
    def currentState(self):
        return 'Current state: ' + self.states(self.currentState)
    
    def average(self, param, newData):
        if not param['arr']:
            param['arr'] = [newData] * param['windowSize']
            param['average'] = newData
        if param['ind'] >= param['windowSize']:
            param['ind'] = 0
        param['average'] -= param['arr'][param['ind']] / param['windowSize']
        param['average'] += newData / param['windowSize']
        param['arr'][param['ind']] = newData
        param['ind'] += 1
        return param['average']
    
    def search(self):
        beginTime = time.time()
        while time.time() - beginTime < 30:
            _, conf = getXofObject()
            averageConf = self.average(self.averageParamConf, conf)
            print('search', averageConf)
            if averageConf < 0.4:
                self.ram.set_speeds(0, 5)
            elif averageConf < 0.8:
                self.ram.set_speeds(0, 0)
            else:
                return True
        return False
    
    def aim(self):
        pid = self.pids[1]
        beginTime = time.time()
        while time.time() - beginTime < 30:
            x, conf = getXofObject()
            w = pid(x)
            self.ram.set_speeds(0, w)
            print('aim', x, w)
            averageX = self.average(self.averageParamX, x)
            if abs(2 * averageX - self.image_w) // self.image_w * 100 < self.averageParamX:
                return True
        return False

    def sneak(self):
        pid = self.pids[2]
        beginTime = time.time()
        while time.time() - beginTime < 30:
            x, conf = getXofObject()
            w = pid(x)
            self.ram.set_speeds(25, w)
            print('sneak', x, w)

        return False
        
    def capture(self):
        perform_action_capture()
    
    def mainProcess(self):
        result = True

        if result:
            self.currentState = 1
            print(self.currentState())
            result = self.search()

        if result:
            self.currentState = 2
            print(self.currentState())
            result = self.aim()
        
        if result:
            self.currentState = 3
            print(self.currentState())
            result = self.sneak()
        
        if result:
            self.currentState = 4
            print(self.currentState())
            result = self.capture()
        
        if result:
            self.currentState = 5
            print(self.currentState())
            result = not self.sneak()
        
        if not result:
            self.currentState = 6
            print(self.currentState())
        
        return result
    
    def stop(self):
        self.ram.set_speeds(0, 0)



#init_clients()
#ram.set_speeds(0,0)
G = Grabber(ram)
G.capture()