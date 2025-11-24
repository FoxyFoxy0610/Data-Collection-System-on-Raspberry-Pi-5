import serial
import time
import string
import pynmea2
import csv
import time
import os

GPS_data=[["Latitude", "Longitude", "Mode"]]

while True:
    try:
        port="/dev/ttyACM0"
        ser=serial.Serial(port, baudrate=115200, timeout=0.5)
        dataout = pynmea2.NMEAStreamReader()
        newdata=ser.readline().decode('ascii', errors='ignore').strip()

        if newdata.startswith("$GNRMC"):
            newmsg=pynmea2.parse(newdata)
            lat = newmsg.latitude
            lon = newmsg.longitude
            fix_type = newmsg.mode_indicator
            fix_types = {'D': "DGPS", 'A': "Autonomous", 'E': "Estimated", 'N': "Invalid"}
            print(f"Lon: {lon}, Lat: {lat}, mode: {fix_types.get(fix_type, 'Unknown')}")
            GPS_data.append([lat, lon, fix_types.get(fix_type, 'Unknown')])

    except pynmea2.ParseError:
        pass

    except KeyboardInterrupt:
        print("Exiting program.")

        current_date = time.strftime('%Y-%m-%d', time.localtime())
        current_time = time.strftime('_%H-%M-%S', time.localtime())
        
        gps_folder_path = f'./GPS_data/{current_date}'

        os.makedirs(gps_folder_path, exist_ok=True)
        
        with open(gps_folder_path + '/GPS_'+ current_date + current_time +'.csv', 'w', newline='') as output:
            writer = csv.writer(output)
            writer.writerows(GPS_data)
        
        break