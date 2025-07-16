import cv2
import glob
import numpy as np
import pickle
import os

save_path = './Original_Image/PiCamera_Wide/'
resault_path = './output/'

if __name__ == '__main__':
    f = pickle.load(open("./output/FeatureFactor_Wide",'rb'))
    ret, mtx, dist, rvecs, tvecs = f['ret'], f['mtx'], f['dist'], f['rvecs'], f['tvecs']

images = glob.glob(save_path + '*.jpg')
for name in images:
    print('name:', name)
    img = cv2.imread(name)
    img = cv2.resize(img, (2592, 1944), interpolation=cv2.INTER_AREA)
    h, w = img.shape[:2]
    new_camera_mtx,roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    dst = cv2.undistort(img, mtx, dist, None, new_camera_mtx)
    # cv2.imshow('img',dst)
    cv2.imwrite(resault_path + name.split(os.sep)[-1], dst)
    # cv2.waitKey(1)