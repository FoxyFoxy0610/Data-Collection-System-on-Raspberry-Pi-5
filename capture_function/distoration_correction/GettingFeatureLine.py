import cv2
import glob
import numpy as np
import os

Board_raw = 7
Board_col = 5

save_path = 'Original_Image/PiCamera_Wide/'
result_path = './output/'
feature_file = 'FeatureFactor_Wide.txt'
npz_file = 'camera_params_Wide.npz'

if not os.path.exists(result_path):
    os.makedirs(result_path)

if __name__ == '__main__':
    obj_p = np.zeros((Board_raw * Board_col, 3), np.float32)
    obj_p[:, :2] = np.mgrid[0:Board_raw, 0:Board_col].T.reshape(-1, 2)

    obj_points = []
    img_points = []
    image_shape = None

    images = glob.glob(save_path + '*.jpg')
    for name in images:
        print('Processing:', name)
        img = cv2.imread(name)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, (Board_raw, Board_col), None)
        if ret:
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TermCriteria_MAX_ITER, 30, 0.001)
            sub_corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

            obj_points.append(obj_p)
            img_points.append(sub_corners)

            img = cv2.drawChessboardCorners(img, (Board_raw, Board_col), sub_corners, ret)
            filename = os.path.basename(name)
            output_path = os.path.join(result_path, filename + '_FeatureLine.png')
            cv2.imwrite(output_path, img)

            if image_shape is None:
                image_shape = gray.shape[::-1]

    if image_shape is None:
        print("Can not fine the chessboard, please check the image quality.")
        exit()

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, image_shape, None, None)

    print("Calibration successful.")
    print('ret:', ret)
    print('mtx:', mtx)
    print('dist:', dist)

    with open(os.path.join(result_path, feature_file), 'w') as f:
        print('ret:', ret, file=f)
        print('mtx:', mtx, file=f)
        print('dist:', dist, file=f)
        print('rvecs:', rvecs, file=f)
        print('tvecs:', tvecs, file=f)

    np.savez(os.path.join(result_path, npz_file),
             ret=ret,
             mtx=mtx,
             dist=dist,
             rvecs=rvecs,
             tvecs=tvecs)
    
    print("Calibration parameters saved as .npz.")
