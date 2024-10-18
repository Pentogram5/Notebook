from advanced_camera.SC_detectors import *

tch = TopCameraHandler(0, framework=CamFrameWorks.testFiles, fake_img_update_period=0.5, use_undist=False)
# while True:
#     # print(tch.results, tch.timestamp)
#     ...
tch.start_camera_handling()

print('NIGGERS0')
while tch.isOpened():
    # print('NIGGERS1')
    ret, frame = tch.read()
    # print('NIGGERS', frame)
    if not ret:
        break
    
    # res = model.predict(frame)
    # frame = undistort_img3(frame)[:, 300:-300]
    print(tch.get_results())
    cv2.imshow('Video Stream', frame)
    #cv2.imshow('Video Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break