import cv2
import glob
import numpy as np
import pickle
import os

Board_raw = 5
Board_col = 7

save_path = './Original_Image/PiCamera_Wide/'
result_path = './output/'

if __name__ == '__main__':
    obj_p=np.zeros((Board_raw * Board_col, 3), np.float32)
    obj_p[:, :2] = np.mgrid[0:Board_raw, 0:Board_col].T.reshape(-1, 2)
    
    obj_points=[]
    img_points=[]

    images = glob.glob(save_path + '*.jpg')
    for name in images:
        print('name:', name)
        img = cv2.imread(name)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, (Board_raw, Board_col), None)
        if ret == True:
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TermCriteria_MAX_ITER, 30, 0.001)
            sub_corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

            obj_points.append(obj_p)
            img_points.append(sub_corners)

            img = cv2.drawChessboardCorners(img, (Board_raw, Board_col), sub_corners, ret)
            # cv2.imshow('img',img)
            cv2.imwrite(result_path + name.split(os.sep)[-1] + '_FeatureLine.png', img)
            # cv2.waitKey(1)
    
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, gray.shape[::-1], None, None)
print('ret:', ret)
print('mtx:', mtx)
print('dist:', dist)
print('rvecs:', rvecs)
print('tvecs:', tvecs)

FeatureFile = open('./output/FeatureFactor_Wide.txt', 'w')
print('ret:', ret, file = FeatureFile)
print('mtx:', mtx, file = FeatureFile)
print('dist:', dist, file = FeatureFile)
print('rvecs:', rvecs, file = FeatureFile)
print('tvecs:', tvecs, file = FeatureFile)
FeatureFile.close()

cal_parameter =  {'ret':ret, 'mtx':mtx, 'dist':dist, 'rvecs':rvecs, 'tvecs':tvecs}
pickle.dump(cal_parameter, open("./output/FeatureFactor_Wide","wb"),0)
print("Save successfully!")