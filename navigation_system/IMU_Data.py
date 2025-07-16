#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from CH_100.hipnuc_module import *
import traceback

import csv
import time

log_file = 'chlog.csv'
IMU_data=[["Acceleration(X)", "Acceleration(Y)", "Acceleration(Z)",
            "Gyroscope(X)", "Gyroscope(Y)", "Gyroscope(Z)",
            "Euler_Angles(Pitch)", "Euler_Angles(Roll)", "Euler_Angles(Yaw)",
            "Magnetometer(X)", "Magnetometer(Y)", "Magnetometer(Z)"]]

if __name__ == '__main__':

    m_IMU = hipnuc_module('./CH_100/config.json')
    print("Press Ctrl-C to terminate while statement.")

    #uncomment following line to enable csv logger
    # m_IMU.create_csv(log_file) #uncomment this line to enable
    
    while True:
        try:
            data = m_IMU.get_module_data(10)
            
            #uncomment following line to enable csv logger
            # m_IMU.write2csv(data, log_file)           
            
            acc = [value for dic in data['acc'] for value in dic.values()]
            gyr = [value for dic in data['gyr'] for value in dic.values()]
            euler = [value for dic in data['euler'] for value in dic.values()]
            mag = [value for dic in data['mag'] for value in dic.values()]

            IMU_list = acc + gyr + euler + mag
            # IMU_list = euler
            print(IMU_list)

            IMU_data.append(IMU_list)

        except KeyboardInterrupt:            
            m_IMU.close()
            print("Serial is closed.")

            current_date = time.strftime('%Y-%m-%d', time.localtime())
            current_time = time.strftime('_%H-%M-%S', time.localtime())
    
            imu_folder_path = f'./IMU_data/{current_date}'
            os.makedirs(imu_folder_path, exist_ok=True)

            with open(imu_folder_path + '/IMU_'+ current_date + current_time +'.csv', 'w', newline='') as output:
                writer = csv.writer(output)
                writer.writerows(IMU_data)

            break  
        except Exception:
            print(traceback.format_exc())
            # or
            print(sys.exc_info()[2])
            pass