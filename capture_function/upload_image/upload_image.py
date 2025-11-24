import requests
from PIL import Image
import io
import time

# 參數設定
url = "http://f1eedd99e1a0.ngrok-free.app/record/upload-image/"
image_path = "/home/pi/side_view/Upload_Image/image_test.jpg"

data = {
    "plot_id": 2,
    "plant_index": 5,
    "record_date": "2025-07-30",
    "position": "L"
}

start = time.time()
# 讀取與壓縮圖片
with Image.open(image_path) as img:
    # 轉成 RGB 避免 PNG 或 RGBA 問題
    img = img.convert("RGB")
    
    # 建立記憶體暫存
    compressed_io = io.BytesIO()
    
    # 壓縮品質可調整(1-95，越低檔案越小)
    img.save(compressed_io, format="JPEG", quality=50, optimize=True)
    compressed_io.seek(0)

# 上傳壓縮後圖片
files = {
    "image_file": ("image_test.jpg", compressed_io, "image/jpeg")
}

response = requests.post(url, data=data, files=files)

print(response.status_code, response.text)
print(time.time()-start)
