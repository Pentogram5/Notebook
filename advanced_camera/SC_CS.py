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
    for result in results:
        boxes = result.boxes
        for box in boxes:
            score = box.conf.item()  # Confidence score
            cls = result.names[box.cls.int().item()]
            x1, y1, x2, y2 = map(int, box.xyxy.flatten().cpu().numpy())
            if cls == 'border':
                if x1 < x_min:
                    x_min = x1
                if x2 > x_max:
                    x_max = x2
                if y1 < y_min:
                    y_min = y1
                if y2 > y_max:
                    y_max = y2

    WIDTH = 400
    HEIGHT = 310
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


def to_map_system(koeffs, x, y, sm = True):
    koef1, koef2, x_min, y_min = koeffs

    if sm:
        return (x - x_min) * koef1, (y - y_min) * koef2

    return x - x_min, y - y_min

def to_map_system_arr(koeffs, arr, sm = True):
    koef1, koef2, x_min, y_min = koeffs

    res = []
    for point in arr:
        x, y = point

        res.append([(x - x_min) * koef1, (y - y_min) * koef2])
    
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
