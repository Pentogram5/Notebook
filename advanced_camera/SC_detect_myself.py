# import cv2
# from ultralytics import YOLO
# import time
#
# model1 = YOLO('best_nano.pt')
#
# image = cv2.imread('new1\\frame0.jpg')
# cv2.imshow('kadr', image)
#
# results = model1(image)
#
# a = 0
#
# for result in results:
#     boxes = result.boxes
#
#     for box in boxes:
#         a += 1
#
#
# cv2.waitKey(0)
# cv2.destroyAllWindows()
from fileinput import filename

import cv2
import numpy as np


# rstp = 'rtsp://Admin:rtf123@192.168.2.251/251:554/1/1'
# cap = cv2.VideoCapture(rstp)  # Use 0 for the default camera

# Define lower and upper limits for red color in HSV
lower_red = np.array([0, 100, 100])
upper_red = np.array([10, 255, 255])
lower_red2 = np.array([170, 100, 100])
upper_red2 = np.array([180, 255, 255])

# Define lower and upper limits for green color in HSV
lower_green = np.array([40, 100, 100])
upper_green = np.array([80, 255, 255])


# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break


from ultralytics import YOLO
import cv2
import math
model = YOLO('best_nano.pt')

filenam = 'new7\\frame860.jpg'
frame = cv2.imread(filenam)
results = model(frame)


robots = []
accs = []
for result in results:
    boxes = result.boxes  # Get bounding box outputs
    for box in boxes:
        # Extract coordinates and class information
        score = box.conf.item()  # Confidence score
        cls = result.names[box.cls.int().item()]  # Class name

        if cls == 'robot':
            x1, y1, x2, y2 = map(int, box.xyxy.flatten().cpu().numpy())  # Convert to integers
            score = box.conf.item()  # Confidence score
            cls = result.names[box.cls.int().item()]  # Class name

            # Draw the bounding box and label on the image
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green rectangle
            cv2.putText(frame, f'{cls} {score:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            robots.append(list(map(int, box.xyxy.flatten().cpu().numpy())))  # Convert to integers)
            accs.append(score)

# Convert the frame to HSV color space

# # Create masks for red and green colors
# for elem in robots:
#
#
#
#     x1 = elem[0]
#     y1 = elem[1]
#     x2 = elem[2]
#     y2 = elem[3]
#     new_frame = frame[y1:y2, x1:x2]
#     hsv_frame = cv2.cvtColor(new_frame, cv2.COLOR_BGR2HSV)
#
#     mask_red1 = cv2.inRange(hsv_frame, lower_red, upper_red)
#     mask_red2 = cv2.inRange(hsv_frame, lower_red2, upper_red2)
#     mask_green = cv2.inRange(hsv_frame, lower_green, upper_green)
#
#     # Combine masks for red
#     mask_red = cv2.bitwise_or(mask_red1, mask_red2)
#
#     # Find contours for red LEDs
#     contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
#     # Draw circles around detected red LEDs
#     for contour in contours_red:
#         if cv2.contourArea(contour) > 1000:  # Filter small contours
#             M = cv2.moments(contour)
#             if M["m00"] != 0:
#                 cX = int(M["m10"] / M["m00"])
#                 cY = int(M["m01"] / M["m00"])
#                 cv2.circle(frame, (x1 + cX, y1 + cY), 10, (0, 0, 255), -1)  # Red circle
#
#     # Draw circles around detected green LEDs
#     for contour in contours_green:
#         if cv2.contourArea(contour) > 1000:  # Filter small contours
#             M = cv2.moments(contour)
#             if M["m00"] != 0:
#                 cX = int(M["m10"] / M["m00"])
#                 cY = int(M["m01"] / M["m00"])
#                 cv2.circle(frame, (x1 + cX, y1 + cY), 10, (0, 255, 0), -1)  # Green circle
#
#     # Display the result
#     cv2.imshow('LED Detection', frame)
#     cv2.waitKey(0)
#
# cv2.destroyAllWindows()
#
#     # if cv2.waitKey(1) & 0xFF == ord('q'):
#     #     break
# #
# # cap.release()
# # cv2.destroyAllWindows()


import argparse
import numpy as np
import math
import cv2 as cv
import sys
def downsize(image):
     k = 0.5
     x = int(k * image.shape[1])
     y = int(k * image.shape[0])
     return cv.resize(image, (x, y), k, k)
COLORS = {"yellow": (0, 255, 255),
 "blue": (255, 0, 0),
 "lime": (0, 255, 0),
 "black": (0, 0, 0),
 "white": (255, 255, 255),
 "red": (0, 0, 255),
 "green": (0, 128, 0),
 "cyan": (255, 255, 0),
 "magenta": (255, 0, 255),
 "purple": (128, 0, 128),
 "gray": (128, 128, 128)
 }
THICKNESS = 2

# parser = argparse.ArgumentParser()
# # parser.add_argument('filename', help='The name of the file containing an image')
#
# parser.add_argument('shape', help='The shapes that need to be detected',
#  choices=('circles', 'lines'))
# parser.add_argument('--no_show', help='Prevents the program from showing'
#  ' processing results in windows',
#  action='store_true')
# parser.add_argument('-o', '--output', help='The file to write the results to.'
#  ' Note that in the case of lines'
#  ' detection the filename will be'
#  ' prepended with \'p_\' for the'
#  ' probabilistic line transform',
#  default='output.png')
# parser.add_argument('--color', '-c', help='The color to highlight shapes with',
#  choices=COLORS.keys(), default="magenta")
# args = parser.parse_args()
shape = 'lines'
detecting_lines = (shape == "lines")
color = COLORS['magenta']
# color = COLORS[args.color]
# if not cv.haveImageReader(args.filename):
#  print("Could not read the image from file")
#  sys.exit(1)

def calculate_slope(line):
    x1, y1, x2, y2 = line
    if x2 - x1 == 0:
        return float('inf')

    return round(math.atan((y2 - y1) / (x2 - x1)) * 180 / math.pi)



fil = filenam
src = cv.imread(cv.samples.findFile(fil), cv.IMREAD_COLOR)
sorted_indices = sorted(range(len(accs)), key=lambda i: accs[i], reverse=True)

# Step 2: Create sorted arrays using the sorted indices
sorted_array = [accs[i] for i in sorted_indices]
sorted_consequence_array = [robots[i] for i in sorted_indices]

ind = 0
for robot in sorted_consequence_array:
    if ind >= 2:
        break
    ind += 1
    x1 = robot[0]
    y1 = robot[1]
    x2 = robot[2]
    y2 = robot[3]

    src1 = src[y1:y2, x1:x2]
    gray = cv.cvtColor(src1, cv.COLOR_BGR2GRAY)
    if detecting_lines:
        dst = cv.Canny(gray, 50, 200, None, 3)
        cdst = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)
        cdstP = np.copy(cdst)
        # lines = cv.HoughLines(dst, 1, np.pi / 180, 200, None, 0, 0)
        # if lines is not None:
        #     for line in lines:
        #         rho = line[0][0]
        #         theta = line[0][1]
        #         a = math.cos(theta)
        #         b = math.sin(theta)
        #         x0 = a * rho
        #         y0 = b * rho
        #         pt1 = (int(x0 + 900 * (-b)), int(y0 + 900 * a))
        #         pt2 = (int(x0 - 900 * (-b)), int(y0 - 900 * a))
        #         cv.line(cdst, pt1, pt2, color, THICKNESS, cv.FILLED)
        linesP = cv.HoughLinesP(dst, 1, np.pi / 180, 50, None, 35, 3)
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

        max_line = None
        max_count = 0

        for slope, lines in parallel_lines.items():
            cnt = len(lines)  # Count occurrences of this line segment
            if cnt > max_count:
                max_count = cnt
                max_line = lines[0]

        cv2.line(cdstP, (max_line[0], max_line[1]), (max_line[2], max_line[3]), (0, 255, 0), 2)  # Draw in green

        # Display the result
        cv2.imshow('Parallel Lines', cdstP)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        # if not args.no_show:
            # cv.imshow("Source", downsize(src1))
            # cv.imshow("Canny Edge Detection", downsize(dst))
            # cv.imshow("Grayscale", downsize(gray))
            # cv.imshow("Standard Hough Line Transform",
            # downsize(cdst))


        # cv.imwrite(args.output, cdst)
        # cv.imwrite('p_' + args.output, cdstP)
    # else:
    #     gray = cv.medianBlur(gray, 7)
    #     height = gray.shape[0]
    #     circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, height / 8, param1=100, param2=35, minRadius=1,maxRadius=int(0.5 * min(gray.shape[:2])))
    #
    #     if circles is not None:
    #         circles = np.uint16(np.around(circles))
    #         for circle in circles[0, :]:
    #             center = tuple(circle[:2])
    #             cv.circle(src1, center, 1, COLORS["gray"], 3)
    #             radius = circle[2]
    #             cv.circle(src1, center, radius, color, THICKNESS)
    #     if not args.no_show:
    #         cv.imshow("Median blur", downsize(gray))
    #         cv.imshow("The Circles Detected", downsize(src1))
    #     cv.imwrite(args.output, src1)
    cv.waitKey(0)