import boto3
from PIL import Image
import io
from picamera2 import Picamera2
import time
import uuid

# -------------------------------
# 1. Raspberry Pi 啟動相機
# -------------------------------
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()
time.sleep(0.2)

image_path = "/home/pi/captured.jpg"
picam2.capture_file(image_path)

# -------------------------------
# 2. 壓縮圖片
# -------------------------------
with Image.open(image_path) as img:
    img = img.convert("RGB")
    compressed_io = io.BytesIO()
    img.save(compressed_io, format="JPEG", quality=100, optimize=True)
    compressed_io.seek(0)

# -------------------------------
# 3. 上傳到 S3
# -------------------------------
s3 = boto3.client(
    "s3",
    aws_access_key_id="",
    aws_secret_access_key="",
    region_name="ap-northeast-1"
)

bucket = "monitor-robot-upload"

# -------------------------------
# 4. 場域與植物資訊
# -------------------------------
location = "NTU"
field = "SSL 403"
furrow_num = 2
plot_id = 2427
plant_index = 4
position = "R"
longitude = 121.8855
latitude = 25.8855
record_date = time.strftime("%Y-%m-%d")

# -------------------------------
# 5. S3 Key 與 Metadata
# -------------------------------
filename = f"{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}.jpg"
key = f"{location}/{field}/plot_{plot_id}/plant_{plant_index}/{filename}"

metadata = {
    "location": location,
    "field": field,
    "furrow_num": str(furrow_num),
    "plot_id": str(plot_id),
    "plant_index": str(plant_index),
    "position": position,
    "record_date": record_date,
    "longitude": str(longitude),
    "latitude": str(latitude)
}

# -------------------------------
# 6. 上傳
# -------------------------------
s3.put_object(
    Bucket=bucket,
    Key=key,
    Body=compressed_io,
    ContentType="image/jpeg",
    ServerSideEncryption='AES256',
    Metadata=metadata
)

print("Upload complete:", filename)

