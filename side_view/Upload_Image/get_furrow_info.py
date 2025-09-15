import requests

BASE_URL = "http://f1eedd99e1a0.ngrok-free.app"

field_name = "BME_Grassland"
furrow_num = 1

params = {
    "field_name": field_name,
    "furrow_num": furrow_num
}

response = requests.get(f"{BASE_URL}/record/get-plots-by-furrow/", params=params)

if response.status_code == 200:
    data = response.json()
    for plot in data.get("plots", []):
        print(f"Plot ID: {plot['plot_id']}, Plant Count: {plot['plant_count']}")
else:
    print("錯誤:", response.status_code, response.text)