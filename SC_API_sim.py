from simulator.SC_sim import *
import threading

def init_clients():
    sim_th = threading.Thread(target=main)
    sim_th.start()

# def get_constants():
#     global IR_G, IR_R, IR_B, ULTRASONIC
#     return IR_G, IR_R, IR_B, ULTRASONIC

class RobotDirection:
    def __init__(self):
        self.left_cms = 0
        self.right_cms = 0
    
    def set_speed_cms_left(self, speed):
        self.left_cms = speed
        self._update_tank_speed()
    
    def set_speed_cms_right(self, speed):
        self.right_cms = speed
        self._update_tank_speed()
    
    def _update_tank_speed(self):
        # global tank
        tank = get_tank()
        if tank is not None:
            tank.set_speeds(self.left_cms, self.right_cms)

global rb
rb = RobotDirection()