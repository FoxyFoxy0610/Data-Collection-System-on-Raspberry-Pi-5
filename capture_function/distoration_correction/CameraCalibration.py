import cv2
import numpy as np
import os
import glob


npz_file_path = './output/camera_params_Wide.npz'
input_folder = './Original_Image/PiCamera_Wide/'
output_folder = './output/'

os.makedirs(output_folder, exist_ok=True)

with np.load(npz_file_path) as data:
    mtx = data['mtx']
    dist = data['dist']

print("Loaded calibration data:")
print("Camera Matrix (mtx):\n", mtx)
print("Distortion Coefficients (dist):\n", dist)

images = glob.glob(os.path.join(input_folder, '*.jpg'))

for idx, img_path in enumerate(images):
    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    new_camera_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

    undistorted = cv2.undistort(img, mtx, dist, None, new_camera_mtx)

    x, y, w, h = roi
    undistorted_cropped = undistorted[y:y+h, x:x+w]

    filename = os.path.basename(img_path)
    cv2.imwrite(os.path.join(output_folder, f"undistorted_{filename}"), undistorted_cropped)

    print(f"[{idx+1}/{len(images)}] Processed: {filename}")

print("所有圖片已成功校正並儲存至：", output_folder)
