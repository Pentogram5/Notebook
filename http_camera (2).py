import time

import cv2
from ultralytics import YOLO
import numpy as npwsssw


cap = cv2.VideoCapture('http://192.168.245.178:8080/?action=stream')
model = YOLO('best_cam.pt')


#fourcc = cv2.VideoWriter.fourcc(*'MP4V')
#out = cv2.VideoWriter('robotCam_tst.avi', fourcc, 20.0, (640, 480))
while True:
    ret, frame = cap.read()
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #out.write(frame)
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    res = model(frame)

    # time.sleep(1)

    for result in res:
        boxes = result.boxes  # Get bounding box outputs
        for box in boxes:
            # Extract coordinates and class information
            x1, y1, x2, y2 = map(int, box.xyxy.flatten().cpu().numpy())  # Convert to integers
            score = box.conf.item()  # Confidence score
            cls = result.names[box.cls.int().item()]  # Class name

            # Draw the bounding box and label on the image
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green rectangle
            cv2.putText(frame, f'{cls} {score:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow('video feed', frame)
    #cv2.imshow('gray feed', gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
#out.release()
cv2.destroyAllWindows()
