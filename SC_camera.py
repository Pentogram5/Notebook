# opencv
import time
import cv2
import ffmpegcv
# !!! нужно установить https://phoenixnap.com/kb/ffmpeg-windows

# ffmpegcv, IP Camera Low-latency
# e.g. HIK Vision IP Camera, `101` Main camera stream, `102` the second
stream_url = 'rtsp://Admin:rtf123@192.168.2.250/251:554/1/1'
cap = ffmpegcv.VideoCaptureStreamRT(stream_url)  # Low latency & recent buffered
# cap = ffmpegcv.ReadLiveLast(ffmpegcv.VideoCaptureStreamRT, stream_url) #no buffer
while True:
    ret, frame = cap.read()
    if not ret:
        break
    # print(frame)
    cv2.imshow('aa',frame)
    # print(frame)
    # cv2.waitKey(0)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break