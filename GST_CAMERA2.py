import os
os.add_dll_directory("C:\\gstreamer\\1.0\\msvc_x86_64\\bin")
import cv2
# gst = 'rtspsrc location=rtsp://192.168.8.57/live1s3.sdp timeout= 30000 ! decodebin ! videoconvert ! video/x-raw,format=BGR ! appsink drop=1'
gst = 'udpsrc port=5600 ! application/x-rtp, payload=96 ! rtph264depay ! avdec_h264 ! appsink sync=false max-buffers=2 drop=true'

cap = cv2.VideoCapture(gst,cv2.CAP_GSTREAMER)
while(cap.isOpened()):
  ret, frame = cap.read()
  if not ret:
    break
  cv2.imshow('frame', frame)
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

cv2.destroyAllWindows()
cap.release()