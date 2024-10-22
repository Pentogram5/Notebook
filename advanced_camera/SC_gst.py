import os
import threading
import time
import cv2
# from SC_get_direction import *
# from wincam import DXCamera  # Importing the new camera module
import bettercam
from .windowsing import *

class GstCam:
    cam1 = 'rtsp://Admin:rtf123@192.168.2.250/251:554/1/1'
    cam2 = 'rtsp://Admin:rtf123@192.168.2.251/251:554/1/1'
    cam3 = 'rtsp://192.168.245.213:8080/h264_ulaw.sdp'
    command = 'gst-launch-1.0 rtspsrc location={} latency=0 ! decodebin ! autovideosink'

    def __init__(self, w=1391+250, h=934, fps=30, margin=(20,50,200,100)):
        # l,t,r,b
        self.win_name = "Direct3D11 renderer"
        self.camera = None
        self.fps = fps
        self.w = w
        self.h = h
        self.margin = margin

    def _run_cam(self, c):
        cam = ''
        if c == -1:
            os.system("gst-launch-1.0 videotestsrc ! videoconvert ! autovideosink")
            return None
        if c == 0:
            cam = GstCam.cam1
        elif c == 1:
            cam = GstCam.cam2
        elif c == 2:
            cam = GstCam.cam3
            os.system('gst-launch-1.0 rtspsrc location=rtsp://192.168.245.213:8080/h264_ulaw.sdp latency=0 ! rtph264depay ! h264parse ! decodebin ! autovideosink')
        os.system(self.command.format(cam))

    def VideoCapture(self, cam):
        th = threading.Thread(target=self._run_cam, args=(cam,))
        th.start()
        time.sleep(2)

        w, h = self.w, self.h
        position_window(self.win_name, w, h)
        bring_window_to_front(self.win_name)

        # Get the list of all windows and search for the target window
        windows = gw.getWindowsWithTitle(self.win_name)
        while not windows:
            windows = gw.getWindowsWithTitle(self.win_name)
            print(f"Окно с именем '{self.win_name}' не найдено.")
            time.sleep(1)
            # raise ValueError(f"Окно с именем '{self.win_name}' не найдено.")
        
        target_window = windows[0]  # Take the first found window

        # Define the capture area (left, top, right, bottom)
        region = (target_window.left, target_window.top,
                  target_window.right, target_window.bottom)
        # print(region)

        # Create an instance of the camera
        if self.camera is not None:
            self.camera.stop()  # Stop the old camera before creating a new one
            del self.camera  # Delete the old camera object
            
        # w = region[2]-region[0]
        # h = region[3]-region[1]
        x, y, w, h = region[0], region[1], w, h
        x += self.margin[0]
        y += self.margin[1]
        w -= self.margin[2]+self.margin[0]
        h -= self.margin[3]+self.margin[1]
        # print(x, y, w, h)
        self.camera = bettercam.create()
        #, fps=self.fps
        self.camera.start(region=(x, y, w, h), target_fps=self.fps)  # Create a new camera instance
        # Start capturing in the specified area
        # self.camera.start(region=region, target_fps=self.fps)

    def read(self):
        if self.camera is None:
            return None, None
        position_window(self.win_name, self.w, self.h)
        bring_window_to_front(self.win_name)
        while True:
            try:
                # frame = self.camera.get_latest_frame()
                rgb = self.camera.get_latest_frame()  # Get the latest RGB frame
                frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR
                break
            except Exception as ex:
                print(ex)
        
        if frame is None:
            raise RuntimeError("Не удалось захватить изображение.")

        # Return the image in NumPy array format
        return True, frame

    def stop(self):
        # Stop capturing
        if self.camera is not None:
            self.camera.stop()

if __name__=='__main__':
    # Main execution
    cam = GstCam()
    cam.VideoCapture(0)

    print('AAAA')
    while True:
        old_t = time.time()
        ret, frame = cam.read()
        t = time.time()
        print(t-old_t)
        if ret:
            cv2.imshow('Camera', frame)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) == ord('q'):
            break

    # Clean up resources on exit
    cam.stop()
    cv2.destroyAllWindows()