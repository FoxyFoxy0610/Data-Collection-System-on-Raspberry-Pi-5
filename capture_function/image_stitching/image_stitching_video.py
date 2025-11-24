import cv2
import time

# 讀取影片
video_path = "side_view(spare_1)-Trim.mp4"
cap = cv2.VideoCapture(video_path)

fps = int(cap.get(cv2.CAP_PROP_FPS))
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count // fps
print(f"影片長度: {duration} 秒, FPS: {fps}")

start_time = time.time()

frames = []
interval_ms = 40  # 0.25 秒
sec = 0

while sec * interval_ms < duration * 1000 / 24:
    cap.set(cv2.CAP_PROP_POS_MSEC, sec * interval_ms)
    ret, frame = cap.read()
    if not ret:
        break
    frames.append(frame)
    sec += 1

cap.release()
print(f"共擷取 {len(frames)} 張影格")

# 建立縫合器（垂直縫合模式 SCANS）
stitcher = cv2.Stitcher_create(cv2.Stitcher_SCANS)

# 一次性縫合所有影格
status, pano = stitcher.stitch(frames)

if status == cv2.Stitcher_OK:
    cv2.imwrite("stitched_video_result.jpeg", pano)
    print("縫合完成，總耗時:", round(time.time() - start_time, 2), "秒")
else:
    print("縫合失敗，錯誤碼:", status)
