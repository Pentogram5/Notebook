from SC_advenced_movement import ram
from SC_API_tcp import *
from SC_API_tcp import perform_action_capture, perform_action_throw_to_basket
from SC_frontCamera import *

from pid import PID


def getXofObject(obj_class):
    x, y, conf = WebCamera.center(obj_class)
    return x, conf

class Average:
    _arr = []
    _ind = 0
    average = 0.0
    windowSize = 0

    def __init__(self, windowSize):
        self.windowSize = windowSize
        
    
    def __call__(self, newValue):
        if not self._arr:
            self._arr = [newValue] * self.windowSize
            self.average = newValue
        if self._ind >= self.windowSize:
            self._ind = 0
        self.average -= self._arr[self._ind] / self.windowSize
        self.average += newValue / self.windowSize
        self._arr[self._ind] = newValue
        self._ind += 1
        return self.average

    


class Grabber:
    image_w = 640
    image_h = 480
    image_aim = 10  # %
    states = {
        1: 'search',
        2: 'sneak',
        3: 'aim',
        4: 'grab',
        5: 'check',
        6: 'error',
    }
    pids = {
        1: PID(-0.1, 0, 0, setpoint=image_w//2, output_limits=(-40, 40)),
        2: PID(-0.1, 0, 0, setpoint=image_w//2, output_limits=(-40, 40)),
    }
    currentState = None

    def __init__(self, ram):
        init_clients()
        self.ram = ram
        self.currentState = 1
    
    def getCurrentState(self):
        return 'Current state: ' + self.states[self.currentState]

    
    def search(self, objClass):
        A = Average(5)
        beginTime = time.time()
        while time.time() - beginTime < 30:
            _, conf = getXofObject(objClass)
            averageConf = A(conf)
            print('search', averageConf)
            if averageConf < 0.4:
                self.ram.set_speeds(0, 50)
            elif averageConf < 0.8:
                self.ram.set_speeds(0, 0)
            else:
                return True
        return False
    
    def aim(self, objClass):
        A = Average(10)
        pid = self.pids[1]
        count = 0
        beginTime = time.time()
        while time.time() - beginTime < 30:
            x, _ = getXofObject(objClass)
            if x:
                count = 20
                w = pid(x)
                self.ram.set_speeds(0, w)
                averageX = A(x)
                print('aim', x, w, abs(2 * averageX - self.image_w) * 100 / self.image_w)
                if abs(2 * averageX - self.image_w) * 100 / self.image_w < self.image_aim:
                    self.stop()
                    return True
            elif count < 20:
                count += 1
            else:
                break
        self.stop()
        return False

    def sneakCube(self, objClass):
        pid = self.pids[2]
        count = 20
        beginTime = time.time()
        while time.time() - beginTime < 30:
            x, conf = getXofObject(objClass)
            if x:
                w = pid(x)
                self.ram.set_speeds(6, w)
                print('sneak Cube', x, w)
                print(Sensors.IR_R.filteredValue)
                if Sensors.IR_R.filteredValue < 0.2:
                    self.stop()
                    return True
            elif count > 0:
                count -= 1
            else:
                break
        self.stop()
        return False
    
    def sneakSphere(self, objClass):
        pid = self.pids[2]
        count = 20
        beginTime = time.time()
        while time.time() - beginTime < 30:
            x, conf = getXofObject(objClass)
            if x:
                w = pid(x)
                self.ram.set_speeds(6, w)
                print('sneak Cube', x, w)
                print(Sensors.IR_R.filteredValue)
                if Sensors.IR_R.filteredValue < 0.2:
                    self.stop()
                    return True
            elif count > 0:
                count -= 1
            else:
                break
        self.stop()
        return False
    
    def sneakBasket(self, objClass):
        pid = self.pids[2]
        count = 20
        beginTime = time.time()
        while time.time() - beginTime < 30:
            x, conf = getXofObject(objClass)
            if x:
                w = pid(x)
                self.ram.set_speeds(6, w)
                print('sneak Base', x, w)
                print(Sensors.ULTRASONIC.rawValue)
                if Sensors.ULTRASONIC.rawValue < 14:
                    self.stop()
                    return True
            elif count > 0:
                count -= 1
            else:
                break
        self.stop()
        return False
        
    def capture(self):
        perform_action_capture()
        self.stop()
        return True
    
    def put(self):
        perform_action_throw_to_basket()
        self.stop()
        return True
    
    def mainProcess(self, objClass):
        result = True

        if result:
            getXofObject(objClass)
            getXofObject(objClass)
            getXofObject(objClass)
            self.currentState = 1
            print(self.getCurrentState())
            result = self.search(objClass)

        if result:
            getXofObject(objClass)
            getXofObject(objClass)
            getXofObject(objClass)
            self.currentState = 2
            print(self.getCurrentState())
            result = self.aim(objClass)
        
        if result:
            getXofObject(objClass)
            getXofObject(objClass)
            getXofObject(objClass)
            self.currentState = 3
            print(self.getCurrentState())
            if objClass == 'cube':
                result = self.sneakCube(objClass)
            elif objClass == 'sphere':
                result = self.sneakSphere(objClass)
            elif objClass == 'basket':
                result = self.sneakBasket(objClass)
            else:
                result = False
        
        if result:
            getXofObject(objClass)
            getXofObject(objClass)
            getXofObject(objClass)
            self.currentState = 4
            print(self.getCurrentState())
            if objClass in ['cube', 'sphere']:
                result = self.capture()
            else:
                result = self.put()

        
        # if result:
        #     getXofObject(objClass)
        #     getXofObject(objClass)
        #     getXofObject(objClass)
        #     self.currentState = 5
        #     print(self.getCurrentState())
        #     result = not self.sneak()
        
        if not result:
            self.currentState = 6
            print(self.getCurrentState())
        
        self.stop()

        return result
    
    def stop(self):
        self.ram.set_speeds(0, 0)



G = Grabber(ram)