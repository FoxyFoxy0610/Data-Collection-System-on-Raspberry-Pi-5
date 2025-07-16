import cv2

cap = cv2.VideoCapture("/dev/video8")

cap.set(3, 3840)
cap.set(4, 2160)
cap.set(5, 30)

width = cap.get(3)
heigh = cap.get(4)
fps = cap.get(5)

print(width, heigh, fps)

# while True:
ret, frame = cap.read()
if not ret:
    print("錯誤：無法從相機讀取影像")
    exit()
# if not ret:
#     break

    # cv2.imshow("Frame", frame)
cv2.waitKey(1000)
cv2.imwrite("image_test.jpg", frame)
cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()
