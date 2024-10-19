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
