This is the data collection system for simulating robotic platform including following tools:  
- **RTK-GNSS:** [ublox ZED-F9P](https://ricelee.com/product/zed-f9p-gps-rtk-hat) with NTRIP from RTK2GO.  
- **LiDAR:** RPI-LiDAR A1 / HOKUYO UST-05LX / RPI-LiDAR S2L  
- **IMU:** CH-100 / GY91  
- **RPI Camera (v2.1 / v3):** This section is in the folder "side view" with record and camera calibration.

The base source code of each sensor is in the **"sensor_source_code"**.
The folder **"remote_capture_control"** is the package for the remote capture module which receiving the MQTT signal to control the capture function, then send it back to the server, and the fundamental communication programs are in **"remote_control"**.

The programs in the folder **"capture_function"** are major employed for fruit and flower detection, including:
- **distoration_collection** for calibratinng the wide-angle picture.
- **image_stitching** for establishing the array images to capture the whole tomato plants.

The programs in the folder "remote_control" are the system for remote capturing system by MQTT and socket portocol.
