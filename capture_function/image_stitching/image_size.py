import cv2

img = cv2.imread('test4.jpeg')
height, width = img.shape[:2]
print(f"Width: {width}, Height: {height}")
