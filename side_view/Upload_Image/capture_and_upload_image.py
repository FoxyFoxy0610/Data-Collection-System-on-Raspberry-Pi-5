import requests
from PIL import Image
import io
import time
from picamera2 import Picamera2
import time
import cv2

picam2 = Picamera2()

picam2.configure(picam2.create_still_configuration())

picam2.start()
time.sleep(0.2)

start = time.time()

picam2.capture_file("image_test.jpg")

url = "http://415898e7948c.ngrok-free.app/record/upload-image/"
image_path = "/home/pi/side_view/Upload_Image/image_test.jpg"

data = {
    "plot_id": 2,
    "plant_index": 9,
    "record_date": "2025-07-30",
    "position": "R",
    "longitude": 121.8888,
    "latitude": 25.8888
}


with Image.open(image_path) as img:
    img = img.convert("RGB")
    compressed_io = io.BytesIO()
    img.save(compressed_io, format="JPEG", quality=50, optimize=True)
    compressed_io.seek(0)

files = {
    "image_file": ("image_test.jpg", compressed_io, "image/jpeg")
}

response = requests.post(url, data=data, files=files)

print(response.status_code, response.text)
print(time.time()-start)
