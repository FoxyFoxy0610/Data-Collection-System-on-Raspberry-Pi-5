from picamera2 import Picamera2
import time
import threading

cam0 = Picamera2(0)
cam1 = Picamera2(1)

config0 = cam0.create_still_configuration()
config1 = cam1.create_still_configuration()

cam0.configure(config0)
cam1.configure(config1)

cam0.start()
cam1.start()

time.sleep(0.2)

def capture_cam0():
    # frame0 = cam0.capture_file("image_cam0.jpg")
    for i in range(10):
        start = time.time()
        cam0.capture_file(f"image_0_{i}.jpg")
        print(time.time() - start)
    cam0.stop()

def capture_cam1():
    # frame1 = cam1.capture_file("image_cam1.jpg")
    for i in range(10):
        start = time.time()
        cam1.capture_file(f"image_1_{i}.jpg")
        print(time.time() - start)
    cam1.stop()

t0 = threading.Thread(target=capture_cam0)
t1 = threading.Thread(target=capture_cam1)

start = time.time()
t0.start()
t1.start()

t0.join()
t1.join()

print("✅ Finished capturing from both cameras. Time:", time.time()-start)
