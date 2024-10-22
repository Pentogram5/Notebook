import cv2
import numpy as np


def get_center_system_center(results): # height, width imd.size[:2]
    center = []
    acc = 0
    for result in results:
        boxes = result.boxes  # Get bounding box outputs
        for box in boxes:
            # Extract coordinates and class information
            score = box.conf.item()  # Confidence score
            cls = result.names[box.cls.int().item()]  # Class name

            if cls == 'center' and score > acc:
                center = list(map(int, box.xyxy.flatten().cpu().numpy()))  # Convert to integers)
                acc = score

    x1, y1, x2, y2 = center

    WIDTH_CENTER = 79.5 #hyperparameter
    HEIGHT_CENTER = 77 #hyperparameter
    koef1 = WIDTH_CENTER / (x2 - x1)
    koef2 = HEIGHT_CENTER / (y2 - y1)

    # print(koef1)
    # print(koef2)

    return koef1, koef2


def get_koeffs(results):
    x_min = 10e6
    x_max = 0
    y_min = 10e6
    y_max = 0
    points = []
    for result in results:
        boxes = result.boxes
        for box in boxes:
            score = box.conf.item()  # Confidence score
            cls = result.names[box.cls.int().item()]
            x1, y1, x2, y2 = map(int, box.xyxy.flatten().cpu().numpy())
            p1, p2 = (x1, y1), (x2, y2)
            if cls == 'labirint':
                points.append(p1)
                points.append(p2)
    for (x,y) in points:
        if x < x_min:
            x_min = x
        if x > x_max:
            x_max = x
        if y < y_min:
            y_min = y
        if y > y_max:
            y_max = y
    # NW = (float('inf'), float('inf'))
    # NE = (float('inf'), float('-inf'))
    # SE = (float('-inf'), float('-inf'))
    # SW = (float('inf'), float('-inf'))

    # for (x, y) in points:
    #     if x < NW[0] and y < NW[1]:
    #         NW = (x, y)
    #     if x > NE[0] and y < NE[1]:
    #         NE = (x, y)
    #     if x > SE[0] and y > SE[1]:
    #         SE = (x, y)
    #     if x < SW[0] and y > SW[1]:
    #         SW = (x, y)

    # WIDTH = 201
    # HEIGHT = 210
    WIDTH  = 92
    HEIGHT = 95
    koef1 = WIDTH / (x_max - x_min)
    koef2 = HEIGHT / (y_max - y_min)
    # print(koef1, koef2)
    
    
    # x_min = 10e6
    # y_min = 10e6

    # for result in results:
    #     boxes = result.boxes
    #     for box in boxes:
    #         # score = box.conf.item()  # Confidence score
    #         cls = result.names[box.cls.int().item()]

    #         if cls == 'border':
    #             x1, y1, x2, y2 = map(int, box.xyxy.flatten().cpu().numpy())
    #             if x1 < x_min:
    #                 x_min = x1
    #             if y1 < y_min:
    #                 y_min = y1
    
    return koef1, koef2, x_min, y_min

def get_NW_SW_NE(results):
    x_min = 10e6
    x_max = 0
    y_min = 10e6
    y_max = 0
    points = []
    for result in results:
        boxes = result.boxes
        for box in boxes:
            score = box.conf.item()  # Confidence score
            cls = result.names[box.cls.int().item()]
            x1, y1, x2, y2 = map(int, box.xyxy.flatten().cpu().numpy())
            p1, p2 = (x1, y1), (x2, y2)
            if cls == 'labirint':
                points.append(p1)
                points.append(p2)
                # if x1 < x_min:
                #     x_min = x1
                # if x2 > x_max:
                #     x_max = x2
                # if y1 < y_min:
                #     y_min = y1
                # if y2 > y_max:
                #     y_max = y2
    
    # Преобразуем список точек в массив NumPy
    points = np.array(points)

    if points.size == 0:
        return (None, None, None)  # Если нет точек, возвращаем None

    # Находим координаты для NW, SW и NE
    NW = points[np.argmin(points[:, 0] + points[:, 1])]  # Минимум по x+y
    NE = points[np.argmin(-points[:, 0] + points[:, 1])]  # Минимум по -x+y
    SW = points[np.argmin(points[:, 0] - points[:, 1])]  # Минимум по x-y
    SE = points[np.argmax(points[:, 0] + points[:, 1])]  # Максимум по x+y (если нужно)

    return (tuple(NW), tuple(SW), tuple(NE))


def from_px_to_cm(pos, NW_SW_NE=((0, 0), (0, -1), (1, 0)), WIDTH=201, HEIGHT=210):
    # Распаковка входных параметров
    px, py = pos
    P_NW, P_SW, P_NE = NW_SW_NE
    
    # Определение векторов
    v1 = np.array(P_NE) - np.array(P_NW)  # NW -> NE
    v2 = np.array(P_SW) - np.array(P_NW)  # NW -> SW
    
    # Длина векторов
    L1 = np.linalg.norm(v1)
    L2 = np.linalg.norm(v2)
    
    # Нормализация векторов
    hat_v1 = v1 / L1 if L1 != 0 else v1
    hat_v2 = v2 / L2 if L2 != 0 else v2
    
    # Масштабирование
    S_x = WIDTH / L1
    S_y = HEIGHT / L2
    
    # Смещение (центр новой системы координат)
    T_x = -np.dot(hat_v1, P_NW)
    T_y = -np.dot(hat_v2, P_NW)

    # Построение матрицы перехода
    T = np.array([
        [S_x * hat_v1[0], S_y * hat_v2[0], T_x],
        [S_x * hat_v1[1], S_y * hat_v2[1], T_y],
        [0, 0, 1]
    ])
    
    # Применение матрицы к точке pos
    pos_homogeneous = np.array([px, py, 1])
    pos_sne_homogeneous = T @ pos_homogeneous
    
    # Возвращаем результат в виде (x_sne, y_sne)
    return pos_sne_homogeneous[0] + 95, pos_sne_homogeneous[1] + 45

def to_map_system(koeffs, x, y, sm = True):
    koef1, koef2, x_min, y_min = koeffs

    if sm:
        return (x - x_min) * koef2 + 95, (y - y_min) * koef2 + 45

    return x - x_min, y - y_min

def to_map_system_arr(koeffs, arr, sm = True):
    koef1, koef2, x_min, y_min = koeffs

    res = []
    for point in arr:
        x, y = point

        res.append([round((x - x_min) * koef2) + 95, round((y - y_min) * koef2) + 45])
    
    return res

#get zero point of map system
def map_system_zero(results, h, w):

    x_min = 10e6
    y_min = 10e6

    for result in results:
        boxes = result.boxes
        for box in boxes:
            # score = box.conf.item()  # Confidence score
            cls = result.names[box.cls.int().item()]

            if cls == 'border':
                x1, y1, x2, y2 = list(map(int, box.xyxy.flatten().cpu().numpy()))
                if x1 < x_min:
                    x_min = x1
                if y1 < y_min:
                    y_min = y1

    return int(x_min), int(y_min)


def sm2pix_point(koeffs, point):
    # Из см в пиксели
    x, y = point
    koef1, koef2, x_min, y_min = koeffs
    # print('---')
    # print(point, koeffs)
    res = [round((x - 95) / koef2) + x_min, round((y - 45) / koef2) + y_min]
    # print(res)
    # print('---')
    return res

def sm2pix_point_arr(koeffs, arr):
    # Из см в пиксели (массив)
    # koef1, koef2, x_min, y_min = koeffs
    ans = []
    for point in arr:
        ans.append(sm2pix_point(koeffs, point))

    return ans


def show_sm_point(frame, koeffs, point, color=(0, 255, 255)):
    x_c, y_c = sm2pix_point(koeffs, point)
    try:
        cv2.circle(frame, (x_c, y_c), 3, color, 3)
    except Exception as ex:
        # print('show_sm_point error', ex)
        pass

    return frame

def show_px_point(frame, point, color=(0,255,255)):
    try:
        cv2.circle(frame, point, 3, color, 3)
    except Exception as ex:
        print('show_px_point error', ex)
        pass

    return frame


def show_sm_line(frame, koeffs, point1, point2):
    point1, point2 = sm2pix_point_arr(koeffs, (point1, point2))
    x1, y1 = point1
    x2, y2 = point2
    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 3)

    return frame