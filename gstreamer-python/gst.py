import os
import threading
import time
import cv2
import dxcam
from windowsing import *
# camera = dxcam.create()


class GstCam:
    cam1 = 'rtsp://Admin:rtf123@192.168.2.251/251:554/1/1'
    cam2 = 'rtsp://Admin:rtf123@192.168.2.250/251:554/1/1'
    command = 'gst-launch-1.0 rtspsrc location={} latency=0 ! decodebin ! autovideosink'
    def __init__(self):
        self.win_name = "Direct3D11 renderer"
        self.camera = None
        self.fps = 30
    def _run_cam(self,c):
        # cam = 0
        # if c==0:
        #     cam = GstCam.cam1
        # else:
        #     cam = GstCam.cam2
        # os.system(self.command.format(cam))
        os.system("gst-launch-1.0 videotestsrc ! videoconvert ! autovideosink")
    def VideoCapture(self,cam):
        th = threading.Thread(target=self._run_cam, args=(cam,))
        th.start()
        time.sleep(2)
        
        w = 1333
        h = 889
        position_window(self.win_name, w, h)
        bring_window_to_front(self.win_name)
        
        # Создаем экземпляр камеры
        if self.camera is not None:
            self.camera.stop()  # Останавливаем старую камеру перед созданием новой
            del self.camera  # Удаляем старый объект камеры

        self.camera = dxcam.create()

        # Получаем список всех окон и ищем нужное
        windows = gw.getWindowsWithTitle(self.win_name)
        if not windows:
            raise ValueError(f"Окно с именем '{self.win_name}' не найдено.")
        
        target_window = windows[0]  # Берем первое найденное окно

        # Определяем область захвата (left, top, right, bottom)
        region = (target_window.left, target_window.top,
                  target_window.right, target_window.bottom)
        print(region)

        # Запускаем захват в заданной области
        self.camera.start(region=region, target_fps=self.fps)
    
        
    def read(self):
        # print(self.camera.is_capturing)
        if self.camera is None:
            return None, None
        # Захватываем одно изображение
        # frame = self.camera.grab()
        frame = self.camera.get_latest_frame()
        # frame = self.camera.grab()
        # print(dxcam.device_info())

        if frame is None:
            raise RuntimeError("Не удалось захватить изображение.")

        # Возвращаем изображение в формате NumPy массива
        return True, frame

    def stop(self):
        # Останавливаем захват
        self.camera.stop()

cam = GstCam()
cam.VideoCapture(0)
while True:
    ret, frame = cam.read()
    if ret:
        # print(frame)
        # Display the captured frame
        cv2.imshow('Camera', frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        break