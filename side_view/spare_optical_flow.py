import cv2
import numpy as np
from picamera2 import Picamera2
import time
import os

# Initialize Pi Camera V2

frame_width = 1640
frame_height = 1232
fps = 8

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size":(3280, 2464), "format": "RGB888"}))

current_date = time.strftime('%Y-%m-%d', time.localtime())
current_time = time.strftime('_%H-%M-%S', time.localtime())
folder_path = f'./Optical_Flow_Result/{current_date}'
os.makedirs(folder_path, exist_ok=True)
output_video_path = folder_path + '/Spare_Optical_Flow_' + current_date + current_time + '.mp4'

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

feature_params = dict(maxCorners=50, qualityLevel=0.5, minDistance=250, blockSize=15)
lk_params = dict(winSize=(15, 15), maxLevel=3,
                criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

try:
    picam2.start()
    time.sleep(1)

    prev_gray = None
    prev_points = None
    
    while True:
        start = time.time()
        frame = picam2.capture_array()
        frame_of = cv2.resize(frame, (frame_width, frame_height), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(frame_of, cv2.COLOR_BGR2GRAY)
        
        if prev_gray is None:
            prev_gray = gray
            prev_points = cv2.goodFeaturesToTrack(prev_gray, mask=None, **feature_params)
            continue

        if prev_points is not None:
            next_points, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev_points, None, **lk_params)
            good_old = prev_points[status == 1]
            good_new = next_points[status == 1]

            for i, (new, old) in enumerate(zip(good_new, good_old)):
                a, b = new.ravel()
                c, d = old.ravel()
                frame_of = cv2.line(frame_of, (int(a), int(b)), (int(c), int(d)), (255, 0, 0), 2)
                frame_of = cv2.circle(frame_of, (int(a), int(b)), 5, (0, 0, 255), -1)
            
            prev_points = good_new.reshape(-1, 1, 2)

        new_points = cv2.goodFeaturesToTrack(gray, mask=None, **feature_params)
        if new_points is not None:
            if prev_points is not None:
                prev_points = np.vstack((prev_points, new_points))
            else:
                prev_points = new_points

        prev_gray = gray

        out.write(frame_of)

        print(time.time()-start)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        

except KeyboardInterrupt:
    print("Exiting program...")
    
finally:
    # Release Webcam Source
    out.release()
    cv2.destroyAllWindows()
    picam2.stop()
    print(f"Video saved to {output_video_path}")

