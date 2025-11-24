import subprocess
import csv
import time
import os
from datetime import datetime
import math

# The path and parameter of ultra_simple
ultra_simple_path = './rplidar_sdk/output/Linux/Release/ultra_simple'
serial_port = '/dev/ttyUSB0'
baudrate = '1000000'

# The path of result
output_dir = 'LiDAR_data'
os.makedirs(output_dir, exist_ok=True)

# Launch ultra_simple
process = subprocess.Popen(
    [ultra_simple_path, '--channel', '--serial', serial_port, baudrate],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,  # Set the output as txt
    bufsize=1   # Read in real-time with every line
)

# Save the last information
latest_scan = []
scan_num = 0

def save_scan_to_csv(scan_data):
    if not scan_data:
        return
    
    # Remove the data which Q value is 0
    filtered_data = [item for item in scan_data if item[3] != 0]

    # Transform the raw data to coordination
    for i in range(len(filtered_data)):
        theta_deg = filtered_data[i][1]  # Angle(degree)
        distance = filtered_data[i][2]  # Distance(mm)
        theta_rad = math.radians(theta_deg)  # Angle(Rad)
        
        x = distance * math.cos(theta_rad)
        y = distance * math.sin(theta_rad)
        
        filtered_data[i].append(x)
        filtered_data[i].append(y)


    # Save as .csv file
    current_date = time.strftime('%Y-%m-%d', time.localtime())
    current_time = time.strftime('_%H-%M-%S', time.localtime())
    lidar_folder_path = f'./LiDAR_data/{current_date}'
    os.makedirs(lidar_folder_path, exist_ok=True)
    
    with open(lidar_folder_path + '/LiDAR_'+ current_date + current_time +'(S2L).csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
       
        writer.writerow(['timestamp', 'theta', 'distance_mm', 'quality', 'x', 'y'])
        for item in filtered_data:
            writer.writerow(item)
    
    print(f"Sucessfully save the LiDAR data!")

try:
    for line in process.stdout:
        line = line.strip()
        if not line:
            continue

        # Remove the last data when receiving new angle
        if line.startswith('S '):
            latest_scan = []
            print(f'New Scan[{scan_num}]   ', end = '\r')
            scan_num += 1

        # Decode
        try:
            parts = line.split()
            theta_value = float(parts[1])
            distance_value = float(parts[3])
            quality_value = int(parts[5])

            timestamp_now = datetime.now().isoformat()
            if distance_value <= 2000:
                latest_scan.append([timestamp_now, theta_value, distance_value, quality_value])

        except (IndexError, ValueError) as e:
            pass

except KeyboardInterrupt:
    print("Stop Recording!")
    save_scan_to_csv(latest_scan)
    process.terminate()
    process.wait()
