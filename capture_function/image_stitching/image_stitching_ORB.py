import cv2
import numpy as np
import time

# 讀入兩張圖片
img_top = cv2.imread('image_1.jpg')
img_bottom = cv2.imread('image_2.jpg')

start_time = time.time()

# 灰階處理
gray_top = cv2.cvtColor(img_top, cv2.COLOR_BGR2GRAY)
gray_bottom = cv2.cvtColor(img_bottom, cv2.COLOR_BGR2GRAY)

# 建立 ORB 偵測器（最多 1000 個特徵點）
orb = cv2.ORB_create(
    nfeatures=1000,       # 限制特徵點數 (500)
    scaleFactor=1.5,     # 金字塔縮放比例 (1.2)
    nlevels=12,           # 金字塔層數 (8)
    edgeThreshold=31,    # 邊界忽略寬度 (31)
    firstLevel=0,        # 從第幾層開始 (0)
    WTA_K=2,             # 每個特徵點選擇的方向數 (2)
    scoreType=cv2.ORB_HARRIS_SCORE,  # 使用 Harris 分數（或 FAST_SCORE)
    patchSize=31,        # 描述子計算的區域大小 (31)
    fastThreshold=20     # FAST 檢測門檻 (20)
)

# 偵測特徵點與描述子
kp1, des1 = orb.detectAndCompute(gray_top, None)
kp2, des2 = orb.detectAndCompute(gray_bottom, None)

# 使用 BFMatcher 搭配 Hamming 距離
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(des1, des2)

# 按照距離排序，取前 50 個匹配點
matches = sorted(matches, key=lambda x: x.distance)
good = matches[:200]

# 至少要 4 點才能計算 Homography
if len(good) >= 4:
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    # 計算 Homography（將 bottom warp 到 top）
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
    final = result[y:y + h, x:x + w]

    end_time = time.time()

    # 儲存結果
    cv2.imwrite("stitched_image(ORB).jpeg", final)
    print("Stitching completed. Time taken:", end_time - start_time, "seconds")

else:
    print("找不到足夠的特徵點來拼接")