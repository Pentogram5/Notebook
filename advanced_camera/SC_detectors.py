import cv2

from .SC_undist import undistort_img3
from .SC_gst import *
# https://github.com/ultralytics/ultralytics/issues/518
import os
# os.environ["YOLO_VERBOSE"]="False"
# VERBOSE = str(os.getenv("YOLO_VERBOSE", True)).lower() == "False"  # global verbose mode
os.environ['YOLO_VERBOSE'] = 'False'

from ultralytics import YOLO

import sys
sys.path.append("..")
from SC_utils import *
from .SC_CS import *
import time
import glob

class CamFrameWorks:
    cv2 = 0
    gst = 1
    testCam = 2
    testFiles = 3

class RobotColors:
    RED = 0
    GREEN = 1

class FileCamera:
    def __init__(self, folder='./new9/*', T=5):
        self.folder = folder
        self.T = 5
        self.last_time = time.time()
        
        self.index = 0
        self.imgs = []
        image_names = glob.glob('./new9/*')
        for name in image_names:
            self.imgs.append(cv2.imread(name))
    def read(self):
        t = time.time()
        dt = t - self.last_time
        # if dt > self.T:
        if True:
            self.index = (self.index + 1) % len(self.imgs)
            self.last_time = t
        return True, self.imgs[self.index]
        

# class LoopedCV2Camera:
#     def __init__(self):
#         ...
#     def read(self):
#         ret, frame = self.cam.read()
VIDEO_TEST_PATH = ""
# cap = cv2.VideoCapture(0)
# ret, frame = cap.read()
# cap.release()
# res = model.predict(frame)
# print(res)

def thread_safe_predict(image_path):
    ...

class TopCameraHandler:
    # Handles actions of top camera
    cam1_url = "rtsp://Admin:rtf123@192.168.2.250/251:554/1/1"
    cam2_url = "rtsp://Admin:rtf123@192.168.2.251/251:554/1/1"
    def __init__(self, cam, framework=CamFrameWorks.cv2, fps_cam=30, fps_yolo=30, use_undist=True, fake_img_update_period=5,
                 robot_color=RobotColors.GREEN):
        self.framework = framework
        if   framework==CamFrameWorks.cv2:
            if cam==0:
                self.cam = cv2.VideoCapture(TopCameraHandler.cam1_url)
            else:
                self.cam = cv2.VideoCapture(TopCameraHandler.cam2_url)
        elif framework==CamFrameWorks.gst:
            self.cam = GstCam()
            self.cam.VideoCapture(cam)
        elif framework==CamFrameWorks.testCam:
            self.cam = cv2.VideoCapture(0)
            # self.cam.set(cv2.CAP_PROP_POS_FRAMES, 0)
        elif framework==CamFrameWorks.testFiles:
            self.cam = FileCamera(T=fake_img_update_period)
        self.frame, self.timestamp = None, 0
        self.last_processed_frame = None
        
        ret = False
        while not ret:
            ret, self.frame = self.cam.read()
        
        self.robot_color = robot_color

        #!!!
        self.results = None
        self.tr_cam  = ThreadRate(fps_cam )
        self.tr_yolo = ThreadRate(fps_yolo)
        self.use_undist = use_undist
        
        self.timestamp_cam       = 0 # Время поступления последнего изображения
        self.last_timestamp_cam  = 0
        self.timestamp_yolo      = 0 # Время поступления последнего обработанного изображения
        self.inference_yolo      = 0 # Время обработки изобрежения
        self.last_timestamp_yolo = 0
        
        # Проверка на наличие нового кадра
        self.has_new_frame_to_process = True
        
        # self.start_camera_handling()
        
        # Запущена ли YOLO в данный момент
        self.is_yolo_running = True
        self.ts_inference = TimeStamper()
    
    def continue_yolo(self):
        self.is_yolo_running = True
        
    def pause_yolo(self):
        self.is_yolo_running = False
        
    def isOpened(self):
        return True
    
    def start_camera_handling(self):
        self.th_cam  = threading.Thread(target=self._capture_data)
        self.th_cam .start()
        self.th_yolo = threading.Thread(target=self._process_data)
        self.th_yolo.start()
    
    #!!!
    def read(self):
        ret = (self.frame is not None)
        return ret, self.frame

    def read_yolo(self):
        # print(self.last_processed_frame)
        time.sleep(0)
        ret = (self.last_processed_frame is not None)
        return ret, self.last_processed_frame
    
    #!!!
    def read_with_timestamp(self):
        ret = (self.timestamp > self.last_timestamp) and (self.frame)
        return ret, self.frame, self.timestamp

    def get_results(self):
        return self.results, self.timestamp_yolo
            
    def _capture_data(self):
        ts = TimeStamper()
        while True:
            ret, frame = self.cam.read()
            if ret:
                self.last_timestamp_cam = self.timestamp_cam
                self.timestamp_cam      = time.time_ns()
                ts.timestamp()
                if self.use_undist:
                    frame = undistort_img3(frame)
                # print(ts.timestamp())
                self.frame = frame
                self.has_new_frame_to_process = True
            self.tr_cam.sleep()
    
    def _predict(self, frame):
        model = YOLO('best_nano.pt', verbose=False)
        # Получения предсказания и оценка задержки
        self.ts_inference.timestamp()
        res = model.predict(frame, verbose=False)
        # Сохранение времени последнего поступившего кадра
        self.timestamp_yolo = time.time_ns() 
        
        self.inference_yolo = self.ts_inference.timestamp()
        self.last_processed_frame = frame
        # print(self.last_processed_frame)
        
        # Запись результатов
        self.results = res
        
        # Сохранение времени последнего обработанного изображения, чтобы проверить на изменения в изображении
        self.last_timestamp_yolo = self.timestamp_yolo
    
    def _process_data(self):
        # ts           = TimeStamper()
        ts = TimeStamper()
        while True:
            frame = self.frame
            # print((frame is not None) and self.has_new_frame_to_process)
            if self.is_yolo_running:
                if (frame is not None) and self.has_new_frame_to_process:
                    self._predict(frame)
                    # th = threading.Thread(target=self._predict, args=(frame,))
                    # th.start()
                    
                    # Старый фрейм мы обработали, ждём новый
                    self.has_new_frame_to_process = False
            self.tr_yolo.sleep()
    
    
    
    
    def get_objects(self):
        # Возвращает словарь
        # - ключи    - имена классов
        # - значения - расположение на карте в сантиметрах
        obj_dict = {}
        
        for result in self.results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy.flatten().cpu().numpy())  # Convert to integers
                # score = box.conf.item()  # confidence score
                cls = result.names[box.cls.int().item()]  # cls name
                if cls not in obj_dict.keys():
                    obj_dict[cls] = []
                obj_dict[cls].append([x1, y1, x2, y2])
        return obj_dict



    
    def get_our_raw_position(self):
        # Возвращает
        # - позицию нашего робота в см на основании CV
        # - timestamp с которого их получили
        ts = self.timestamp_yolo

        robot_pos = get_our_robot_pos_3(self.frame, self.results)
        x1, y1, x2, y2 = robot_pos
        if x1 == np.NAN:
            return None, None, ts

        x, y = to_map_system(get_koeffs(self.results), (x2 - x1), (y2 - y1))
        return np.array([x, y]), ts


    def _get_our_raw_rotation(self):
        # Возвращает
        # - курс нашего робота на основании CV в градусах
        # - timestamp с которых их получили
        # 0  градусов соответствует +Ox
        # 90 градусов соответствует +Oy
        # ts = self.timestamp_yolo
        angle_deg = None

        robot_pos = get_our_robot_pos_3(self.frame, self.results, self.robot_color)
        robot_dir, _, _ = get_direction_for_one(frame, robot_pos, (0, 0, 0, 0))
        x1, y1, x2, y2 = robot_dir

        angle_rad = math.atan2(y2 - y1, x2 - x1)
        # Преобразуем радианы в градусы
        angle_deg = math.degrees(angle_rad)
        # Корректируем угол
        angle_deg = (angle_deg + 180) % 360
        return angle_deg

        angle_rad = math.atan2(y2 - y1, x2 - x1)
    # Преобразуем радианы в градусы
        angle_deg = math.degrees(angle_rad)
    # Корректируем угол
        angle_deg = (angle_deg + 90) % 360
        return angle_deg
    