from picamera2 import Picamera2
import time

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())

picam2.start()
time.sleep(0.2)

for i in range(10):
    start = time.time()
    picam2.capture_file(f"image_{i}.jpg")
    print(time.time() - start)