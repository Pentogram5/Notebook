from SC_INS import INS
from advanced_camera.SC_detectors import TopCameraHandler
from SC_advenced_movement import ram, OnDoneActions


def main():
    path = [(0.5,1.5),(1.3,1.5),(1.3,2.3),(2.0,2.3),(2.0,2.7)]
    tch = TopCameraHandler(controlled_delay=0.4, delay_std=0.25, pos_std=0.05, yaw_std=5)
    ins = INS(update_source=tch.update_sink, ram=ram, speed_update_rate=60)
    ins.start_updater()
    
    while True:
        x, y = list(map(float, input().split(' ')))
        p = (x,y)
        ram.move_to_point(p, on_done=OnDoneActions.STOP)
    