import cv2
import numpy as np



def undistort_image(img_path):
    camera_matrix = np.array([[1182.719, 0, 927.03], [0, 1186.236, 609.52], [0, 0, 1]], dtype = np.float32)
    dist_coefs = np.array([-0.5, 0.3, 0, 0, 0], dtype = np.float32)
    img = cv2.imread(img_path)
    h, w = img.shape[:2]
    
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w,h), 1, (w,h))
    
    # Коррекция изображения
    dst = cv2.undistort(img, camera_matrix, dist_coefs, None, new_camera_matrix)
    
    # Обрезка изображения по ROI
    x,y,w,h = roi
    dst = dst[y:y+h, x:x+w]
    
    return dst


def undistort_img(img):
    camera_matrix = np.array([[1182.719, 0, 927.03], [0, 1186.236, 609.52], [0, 0, 1]], dtype=np.float32)
    dist_coefs = np.array([-0.5, 0.3, 0, 0, 0], dtype=np.float32)
    h, w = img.shape[:2]

    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))

    # Коррекция изображения
    dst = cv2.undistort(img, camera_matrix, dist_coefs, None, new_camera_matrix)

    # Обрезка изображения по ROI
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]

    return dst

def undistort_img2(img):
    camera_matrix = np.array([[1.20414740e+03, 0.00000000e+00, 9.96387991e+02],
       [0.00000000e+00, 1.19320316e+03, 5.31173289e+02],
       [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]], dtype=np.float32)
    dist_coefs = np.array([-4.12864650e-01,  2.04757108e-01,  3.15379090e-04, -6.31257829e-03,
       -6.16459477e-02], dtype=np.float32)
    h, w = img.shape[:2]

    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))

    # Коррекция изображения
    dst = cv2.undistort(img, camera_matrix, dist_coefs, None, new_camera_matrix)

    # Обрезка изображения по ROI
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]

    return dst

def undistort_img3(img):
    camera_matrix = np.array([[1.20414740e+03, 0.00000000e+00, 9.96387991e+02],
       [0.00000000e+00, 1.19320316e+03, 5.31173289e+02],
       [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]], dtype=np.float32)
    dist_coefs = np.array([-0.40,  0.2,  0.0003, -0.006, -0.006], dtype=np.float32)
    h, w = img.shape[:2]

    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))

    # Коррекция изображения
    dst = cv2.undistort(img, camera_matrix, dist_coefs, None, new_camera_matrix)

    # Обрезка изображения по ROI
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]

    return dst



# # Применение функции к изображению
# corrected_image = undistort_image('video.jpg')
# cv2.imwrite('corrected_image.jpg', corrected_image)