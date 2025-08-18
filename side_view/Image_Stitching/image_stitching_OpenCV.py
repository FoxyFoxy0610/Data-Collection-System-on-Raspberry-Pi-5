import cv2
import time
import numpy as np

def remove_black_borders(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    
    # 找到非黑區域的邊界
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return img
    
    # 取最大區域
    cnt = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(cnt)
    crop = img[y:y+h, x:x+w]
    return crop

# 讀圖
img_top = cv2.imread('undistorted_image_2.jpg')
img_bottom = cv2.imread('undistorted_image_1.jpg')

start_time = time.time()

# 建立縫合器（SCANS 模式）
stitcher = cv2.Stitcher_create(cv2.Stitcher_SCANS)
# stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)

# 進行縫合
status, pano = stitcher.stitch([img_top, img_bottom])

if status == cv2.Stitcher_OK:
    pano = remove_black_borders(pano)
    cv2.imwrite("stitched_image(OpenCV).jpeg", pano)
    print("OpenCV Stitcher 縫合完成，耗時:", time.time() - start_time, "秒")
else:
    print("縫合失敗，錯誤碼:", status)
