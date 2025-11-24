from hokuyolx import HokuyoLX
import numpy as np
import time
from datetime import datetime
from socket import error as SocketError

import csv
import time
import os

if __name__ == "__main__":
    laser = HokuyoLX()

    try:
        while True:
            now = datetime.now().strftime("%H:%M:%S.%f")
            print(f"\rStart to scan LiDAR. time: {now}", end=" ", flush=True)
            point_cloud = [["X", "Y"]]

            timestamp, scan = laser.get_dist()
            angles = np.degrees(laser.get_angles()) + 90
            x_lidar = scan * np.cos(np.radians(angles))
            y_lidar = scan * np.sin(np.radians(angles))

            for index, data in enumerate(scan):
                # Determine if the distance over 2 meter.
                if int((int(x_lidar[index])) ** 2 + (int(y_lidar[index])) ** 2) > 4000000: # 4000000(mm) = 2m^2
                    pass
                else:
                    point_cloud.append([x_lidar[index], y_lidar[index]])

            time.sleep(0.1)

    except SocketError:
        print("Stop")
        laser.close()

    except KeyboardInterrupt:
        print("Stop")
        laser.close()

    finally:
        current_date = time.strftime('%Y-%m-%d', time.localtime())
        current_time = time.strftime('_%H-%M-%S', time.localtime())
        lidar_folder_path = f'./LiDAR_data/{current_date}'
        os.makedirs(lidar_folder_path, exist_ok=True)
    
        with open(lidar_folder_path + '/LiDAR_'+ current_date + current_time +'(UST-05).csv', 'w', newline='') as output:
            writer = csv.writer(output)
            writer.writerows(point_cloud)
        laser.close()