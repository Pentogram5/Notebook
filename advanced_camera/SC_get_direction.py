import cv2
import numpy as np
import math

def calculate_slope(line):
    x1, y1, x2, y2 = line
    if x2 - x1 == 0:
        return float('inf')

    return round(math.atan((y2 - y1) / (x2 - x1)) * 180 / math.pi)

def get_direction(frame, results):
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

    max_line = None

    for robot in sorted_consequence_array:
        if ind >= 2:
            break
        ind += 1
        x1 = robot[0]
        y1 = robot[1]
        x2 = robot[2]
        y2 = robot[3]

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
        for slope, lines in parallel_lines.items():
            cnt = len(lines)  # Count occurrences of this line segment
            if cnt > max_count:
                max_count = cnt
                max_line = lines[0]
    return max_line
