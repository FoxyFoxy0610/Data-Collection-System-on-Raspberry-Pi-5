import cv2
import numpy as np
import time

# 讀入兩張圖片
img_top = cv2.imread('undistorted_image_2-2.jpg')
img_bottom = cv2.imread('undistorted_image_1-2.jpg')

start_time = time.time()

# 灰階處理
gray_top = cv2.cvtColor(img_top, cv2.COLOR_BGR2GRAY)
gray_bottom = cv2.cvtColor(img_bottom, cv2.COLOR_BGR2GRAY)

# ---- ROI 限定 (上下拼接，取上下接縫區域) ----
overlap = 1000
gray_top_crop = gray_top[-overlap:, :]
gray_bottom_crop = gray_bottom[:overlap, :]

# 建立 AKAZE 偵測器
akaze = cv2.AKAZE_create()

# 偵測特徵點與描述子
kp1_crop, des1 = akaze.detectAndCompute(gray_top_crop, None)
kp2_crop, des2 = akaze.detectAndCompute(gray_bottom_crop, None)

# 調整 ROI 特徵點座標到原圖
kp1 = [cv2.KeyPoint(k.pt[0], k.pt[1] + gray_top.shape[0] - overlap, k.size, k.angle, k.response, k.octave, k.class_id) for k in kp1_crop]
kp2 = [cv2.KeyPoint(k.pt[0], k.pt[1], k.size, k.angle, k.response, k.octave, k.class_id) for k in kp2_crop]

# 用 BFMatcher + KNN 找匹配點（Hamming 距離）
bf = cv2.BFMatcher(cv2.NORM_HAMMING)
matches = bf.knnMatch(des1, des2, k=2)

# Ratio Test
good = [m for m, n in matches if m.distance < 0.75 * n.distance]

# 至少 4 點才能計算 Homography
if len(good) > 4:
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    # RANSAC 過濾錯配
    H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

    # warp 下方圖片到上方座標空間
    height = img_top.shape[0] + img_bottom.shape[0]
    width = max(img_top.shape[1], img_bottom.shape[1])
    result = cv2.warpPerspective(img_bottom, H, (width, height))

    # 將上方圖片貼上（覆蓋掉重疊區）
    result[0:img_top.shape[0], 0:img_top.shape[1]] = img_top

    # 裁剪空白區域
    gray_result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_result, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    x, y, w, h = cv2.boundingRect(contours[0])
    final = result[y:y+h, x:x+w]

    # 儲存結果
    cv2.imwrite("stitched_image(AKAZE).jpeg", final)
    print("AKAZE 縫合完成，耗時:", time.time() - start_time, "秒")
else:
    print("匹配點不足，無法縫合")
