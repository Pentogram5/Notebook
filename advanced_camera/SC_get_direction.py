import cv2
import numpy as np
import math

def calculate_slope(line):
    x1, y1, x2, y2 = line
    if x2 - x1 == 0:
        return float('inf')

    return round(math.atan((y2 - y1) / (x2 - x1)) * 180 / math.pi)

def get_direction(frame, results, margin=(10,10,10,10)):
    robots = []
    accs = []
    for result in results:
        boxes = result.boxes  # Get bounding box outputs
        for box in boxes:
            # Extract coordinates and class information
            x1, y1, x2, y2 = map(int, box.xyxy.flatten().cpu().numpy())  # Convert to integers
            score = box.conf.item()  # Confidence score
            cls = result.names[box.cls.int().item()]  # Class name
            if cls == 'robot':
                robots.append(list(map(int, box.xyxy.flatten().cpu().numpy())))  # Convert to integers)
                accs.append(score)

    sorted_indices = sorted(range(len(accs)), key=lambda i: accs[i], reverse=True)

    # Step 2: Create sorted arrays using the sorted indices
    sorted_array = [accs[i] for i in sorted_indices]
    sorted_consequence_array = [robots[i] for i in sorted_indices]

    ind = 0

    res = []
    for robot in sorted_consequence_array:
        if ind >= 2:
            break
        ind += 1
        x1 = robot[0] + margin[0]
        y1 = robot[1] + margin[1]
        x2 = robot[2] - margin[2]
        y2 = robot[3] - margin[3]

        src1 = frame[y1:y2, x1:x2]
        gray = cv2.cvtColor(src1, cv2.COLOR_BGR2GRAY)

        dst = cv2.Canny(gray, 50, 200, None, 3)

        linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 50, None, 35, 3)
        slope_dict = {}
        if linesP is not None:
            for line in linesP:
                l = line[0]
                slope = calculate_slope(l)
                if slope not in slope_dict:
                    slope_dict[slope] = []

                slope_dict[slope].append(l)

        parallel_lines = {}
        slope_threshold = 10  # Adjust this value as needed

        for slope, line_segments in slope_dict.items():
            # Check if there are other slopes within the threshold range
            for other_slope in list(parallel_lines.keys()):
                if abs(slope - other_slope) < slope_threshold:
                    parallel_lines[other_slope].extend(line_segments)
                    break
            else:
                parallel_lines[slope] = line_segments

        # Draw parallel lines on the original image for visualization
        max_count = 0
        max_line = []
        for slope, lines in parallel_lines.items():
            cnt = len(lines)  # Count occurrences of this line segment
            if cnt > max_count:
                max_count = cnt
                max_line = lines[0]
        if len(max_line) > 0:
            from_to = find_line_direction([0, 0, x2 - x1, y2 - y1], max_line, src1)
            #from_to = max_line
            print(from_to)
            res.append([from_to, x1, y1])
    return res

def get_direction_for_one(frame, robot_pos, margin=(10, 10, 10, 10)):
        x1 = robot_pos[0] + margin[0]
        y1 = robot_pos[1] + margin[1]
        x2 = robot_pos[2] - margin[2]
        y2 = robot_pos[3] - margin[3]

        src1 = frame[y1:y2, x1:x2]
        gray = cv2.cvtColor(src1, cv2.COLOR_BGR2GRAY)

        dst = cv2.Canny(gray, 50, 200, None, 3)

        linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 50, None, 35, 3)
        slope_dict = {}
        if linesP is not None:
            for line in linesP:
                l = line[0]
                slope = calculate_slope(l)
                if slope not in slope_dict:
                    slope_dict[slope] = []

                slope_dict[slope].append(l)

        parallel_lines = {}
        slope_threshold = 10  # Adjust this value as needed

        for slope, line_segments in slope_dict.items():
            # Check if there are other slopes within the threshold range
            for other_slope in list(parallel_lines.keys()):
                if abs(slope - other_slope) < slope_threshold:
                    parallel_lines[other_slope].extend(line_segments)
                    break
            else:
                parallel_lines[slope] = line_segments

        # Draw parallel lines on the original image for visualization
        max_count = 0
        max_line = []
        for slope, lines in parallel_lines.items():
            cnt = len(lines)  # Count occurrences of this line segment
            if cnt > max_count:
                max_count = cnt
                max_line = lines[0]
        if len(max_line) > 0:
            from_to = find_line_direction([0, 0, x2 - x1, y2 - y1], max_line, src1)
            #from_to = max_line
            print(from_to)
            return [from_to, x1, y1]
        return [[np.NAN, np.NAN, np.NAN, np.NAN], x1, x2]


def find_line_direction(robot, max_line, src):
    x1, y1, x2, y2 = robot
    lx1, ly1, lx2, ly2 = max_line
    center_point = [(x1 + x2) // 2, (y1 + y2) // 2]

    perp_vec = find_perpendicular(vec_from_points([lx1, ly1], [lx2, ly2]))
    hsv_img = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)

    h, s, v = cv2.split(hsv_img)

    rows, cols = v.shape
    i_ind, j_ind = np.indices((rows, cols))

    mask = check_point(perp_vec, center_point, [i_ind, j_ind])

    side1 = np.mean(v, where=mask)
    mask2 = np.bitwise_not(mask)
    side2 = np.mean(v, where=mask2)

    new_x = center_point[0] + (lx2 - lx1)
    new_y = center_point[1] + (ly2 - ly1)
    flag = check_point(perp_vec, center_point, [new_x, new_y])

    if (flag and side1 > side2) or ((not flag) and side2 < side1):
        return [center_point[0], center_point[1], new_x, new_y]

    return [new_x, new_y, center_point[0], center_point[1]]


def check_point(vec, center_point, point):
    x, y, = point
    x0, y0 = center_point
    xn, yn = vec
    return (yn * (x - x0)) <= (xn * (y - y0))


def find_perpendicular(line):
    return [-line[1], line[0]]
    # if vector[0] != 0:
    #     return [-vector[1] / vector[0], 1]
    #
    # return [1, 0]


def vec_from_points(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    if (x2 - x1) != 0:
        return [1, (y2 - y1) / (x2 - x1)]
    return [0, 1]


def get_our_robot_pos(frame, results):
    robots = []
    max_score = 0
    for result in results:
        boxes = result.boxes  # Get bounding box outputs
        for box in boxes:
            score = box.conf.item()  # Confidence score
            cls = result.names[box.cls.int().item()]  # Class name
            if cls == 'robot' and score > max_score:
                robots = list(map(int, box.xyxy.flatten().cpu().numpy()))  # Convert to integers)
                max_score = score
    return robots

def get_our_robot_pos_2(frame, results):
    robots = []
    accs = []

    for result in results:
        boxes = result.boxes
        for box in boxes:
            score = box.conf.item()  # Confidence score
            cls = result.names[box.cls.int().item()]  # Class name
            if cls == 'robot':
                robots.append(list(map(int, box.xyxy.flatten().cpu().numpy())))  # Convert to integers)
                accs.append(score)

    sorted_indices = sorted(range(len(accs)), key=lambda i: accs[i], reverse=True)
    # Step 2: Create sorted arrays using the sorted indices
    sorted_array = [accs[i] for i in sorted_indices]
    sorted_consequence_array = [robots[i] for i in sorted_indices]

    ind = 0

    clrs = []
    for robot in sorted_consequence_array:
        if ind >= 2:
            break
        ind += 1
        x1 = robot[0]
        y1 = robot[1]
        x2 = robot[2]
        y2 = robot[3]

        src = frame[y1:y2, x1:x2]

        img_hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)

        h, s, v = cv2.split(img_hsv)

        mask = (v > 240).astype(np.uint8) * 255
        mask_3channel = cv2.merge([mask, mask, mask])

        masked_image = cv2.bitwise_and(src, mask_3channel)
        b, g, r = cv2.split(masked_image)
        g_mean = np.mean(g)
        r_mean = np.mean(r)
        print(g_mean, r_mean)
        if g_mean > r_mean:
            clrs.append(['green', robot, r_mean - g_mean])
        else:
            clrs.append(['red', robot, r_mean - g_mean])

    if len(robots) == 0:
        return [None, None]
    elif len(robots) == 1:
        return [clrs[0], None]

    clr1 = clrs[0]
    clr2 = clrs[1]
    if clr2[2] > clr1[2]:
        clr2[0] = 'red'
        clr1[0] = 'green'
        return [clr1, clr2]

    else:
        clr1[0] = 'red'
        clr2[0] = 'green'
        return [clr1, clr2]

def get_our_robot_pos_3(frame, results, col):
    robots = []
    accs = []

    for result in results:
        boxes = result.boxes
        for box in boxes:
            score = box.conf.item()  # Confidence score
            cls = result.names[box.cls.int().item()]  # Class name
            if cls == 'robot':
                robots.append(list(map(int, box.xyxy.flatten().cpu().numpy())))  # Convert to integers)
                accs.append(score)

    sorted_indices = sorted(range(len(accs)), key=lambda i: accs[i], reverse=True)
    # Step 2: Create sorted arrays using the sorted indices
    sorted_array = [accs[i] for i in sorted_indices]
    sorted_consequence_array = [robots[i] for i in sorted_indices]

    ind = 0

    clrs = []
    for robot in sorted_consequence_array:
        if ind >= 2:
            break
        ind += 1
        x1 = robot[0]
        y1 = robot[1]
        x2 = robot[2]
        y2 = robot[3]

        src = frame[y1:y2, x1:x2]

        img_hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)

        h, s, v = cv2.split(img_hsv)

        mask = (v > 240).astype(np.uint8) * 255
        mask_3channel = cv2.merge([mask, mask, mask])

        masked_image = cv2.bitwise_and(src, mask_3channel)
        b, g, r = cv2.split(masked_image)
        g_mean = np.mean(g)
        r_mean = np.mean(r)
        print(g_mean, r_mean)
        if g_mean > r_mean:
            clrs.append(['green', robot, r_mean - g_mean])
        else:
            clrs.append(['red', robot, r_mean - g_mean])

    if len(robots) == 0:
        return None
    
    if len(robots) == 1:
        if clrs[0][0] == col:
            return clrs[0][1]
        return None

    clr1 = clrs[0]
    clr2 = clrs[1]
    if clr2[2] > clr1[2]:
        clr2[0] = 'red'
        clr1[0] = 'green'
        
        if col == 'red':
            return clr2[1]
        return clr1[1]

    else:
        clr1[0] = 'red'
        clr2[0] = 'green'
        if col == 'red':
            return clr1[1]
        return clr2[1]
    

def find_barriers(frame, results):
    x_min = 10e6
    y_min = 10e6
    x_max = 0
    y_max = 0
    for result in results:
        boxes = result.boxes
        for box in boxes:
            score = box.conf.item()  # Confidence score
            cls = result.names[box.cls.int().item()]  # Class name
            if cls == 'labirint':
                x1, y1, x2, y2 = map(int, box.xyxy.flatten().cpu().numpy()) # Convert to integers)
                if x1 < x_min:
                    x_min = x1
                if y1 < y_min:
                    y_min = y1
                if x2 > x_max:
                    x_max = x2
                if y2 > y_max:
                    y_max = y2
    # cv2.circle(frame, (x_min, y_min), 5, (255, 0, 0), 3)
    # cv2.circle(frame, (x_min, y_max), 5, (255, 0, 0), 3)
    # cv2.circle(frame, (x_max, y_min), 5, (255, 0, 0), 3)
    # cv2.circle(frame, (x_max, y_max), 5, (255, 0, 0), 3)

    x_c = (x_min + x_max) // 2
    y_c = (y_min + y_max) // 2
    MARG = 40 # эвристика, опытным путем определили
    SHT = 40 # эвристика, опытным путем определили
    # cv2.rectangle(frame, (x_c - MARG, y_min - MARG + SHT), (x_c + MARG, y_min + MARG + SHT), (255, 0, 0), 4) #1
    # cv2.rectangle(frame, (x_c - MARG, y_max - MARG - SHT), (x_c + MARG, y_max + MARG - SHT), (255, 0, 0), 4) #3
    # cv2.rectangle(frame, (x_min - MARG + SHT, y_c - MARG), (x_min + MARG + SHT, y_c + MARG), (255, 0, 0), 4) #4
    # cv2.rectangle(frame, (x_max - MARG - SHT, y_c - MARG), (x_max + MARG - SHT, y_c + MARG), (255, 0, 0), 4) #2
    box1 = [x_c - MARG, y_min - MARG + SHT, x_c + MARG, y_min + MARG + SHT]
    box2 = [x_max - MARG - SHT, y_c - MARG, x_max + MARG - SHT, y_c + MARG]
    box3 = [x_c - MARG, y_max - MARG - SHT, x_c + MARG, y_max + MARG - SHT]
    box4 = [x_min - MARG + SHT, y_c - MARG, x_min + MARG + SHT, y_c + MARG]

    res = []
    inds = [0, 1, 2, 3]
    for box in [box1, box2, box3, box4]:
        res.append(is_open(frame, box))

    ans = [0, 0, 0, 0]
    res = np.array(res)
    sort_inds = np.argsort(res)
    ans[sort_inds[0]] = 1
    ans[sort_inds[1]] = 1
    print(res)
    print(ans)
    return ans


#0 - закрыт, 1 - открыт
def is_open(frame, box):
    x1, y1, x2, y2 = box
    src = frame[y1:y2, x1:x2]
    hsv_img = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_img)

    mask = (v < 100)
    mean_black = np.mean(mask)

    return mean_black