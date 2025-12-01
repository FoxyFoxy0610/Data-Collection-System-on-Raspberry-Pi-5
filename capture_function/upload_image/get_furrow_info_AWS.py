import boto3

# -------------------------------
# S3 Client
# -------------------------------
s3 = boto3.client(
    "s3",
    aws_access_key_id="",
    aws_secret_access_key="",
    region_name="ap-northeast-1"
)

bucket = "monitor-robot-upload"

# -------------------------------
# 查詢條件
# -------------------------------
location = "NTU"
field = "SSL 403"
furrow_num = "2"
position = "R"

prefix = f"{location}/{field}/"

# -------------------------------
# 1. 列出 field 下所有物件
# -------------------------------
plant_data = {}  # plot_id -> {plant_index -> info}

continuation_token = None
while True:
    if continuation_token:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, ContinuationToken=continuation_token)
    else:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

    for obj in response.get("Contents", []):
        key = obj["Key"]
        head = s3.head_object(Bucket=bucket, Key=key)
        md = head.get("Metadata", {})

        # 篩選 furrow_num 和 position
        if md.get("furrow_num") == str(furrow_num) and md.get("position") == position:
            plot_id = md.get("plot_id")
            plant_index = md.get("plant_index")
            longitude = md.get("longitude")
            latitude = md.get("latitude")

            # 初始化 plot_id
            if plot_id not in plant_data:
                plant_data[plot_id] = {}

            # 同一個 plant_index 只保留第一次
            if plant_index not in plant_data[plot_id]:
                plant_data[plot_id][plant_index] = {
                    "longitude": longitude,
                    "latitude": latitude,
                    "key": key
                }

    # 判斷是否有下一頁
    if response.get("IsTruncated"):
        continuation_token = response.get("NextContinuationToken")
    else:
        break

# -------------------------------
# 2. 輸出每個 plot 對應 plant 數量與座標
# -------------------------------
for plot_id, plants in plant_data.items():
    print(f"Plot ID: {plot_id}, Plant Count: {len(plants)}")
    for plant_index, info in plants.items():
        print(f"  Plant {plant_index}: ({info['longitude']}, {info['latitude']})")