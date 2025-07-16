import socket
import base64
import serial
import pyrtcm
from pyrtcm import RTCMReader
import pynmea2
import yaml
import threading
# import keyboard

import csv
import time
import os
import sys
import select

RTK_data=[["Latitude", "Longitude", "mode", "satellite"]]
record_requested = False

# Import the yaml
config_file = "NTRIP_Client/NTRIP_config.yaml"
with open(config_file, "r") as file:
    config = yaml.safe_load(file)
    
    NTRIP_HOST = config["Caster"]
    NTRIP_PORT = config["Port"]
    MOUNTPOINT = config["Mount_Point"]
    USERNAME = config["User"]
    PASSWORD = config["Password"]

SERIAL_PORT = "/dev/ttyACM0"  # UART of raspberry 
BAUD_RATE = 115200

# Request to NTRIP
def get_ntrip_request():
    auth = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    request = (
        f"GET /{MOUNTPOINT} HTTP/1.1\r\n"
        f"User-Agent: NTRIP-Client\r\n"
        f"Authorization: Basic {auth}\r\n"
        f"\r\n"
    )
    return request.encode()

def connect_to_ntrip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((NTRIP_HOST, NTRIP_PORT))
        sock.sendall(get_ntrip_request())

        response = sock.recv(1024).decode(errors='ignore')
        if "200 OK" not in response:
            print("NTRIP connection fail:", response)
            sock.close()
            return None
        print("Connected to NTRIP Caster.")
        return sock
    except Exception as e:
        print("Failed to connect to NTRIP:", e)
        return None

def parse_nmea(nmea_str,num):
    global record_requested
    try:
        msg = pynmea2.parse(nmea_str)
        if isinstance(msg, pynmea2.types.talker.GGA):  # Analyze GGA message
            lat = msg.latitude
            lon = msg.longitude
            fix_type = msg.gps_qual  # 0: None, 1: GPS, 2: DGPS, 4: RTK Fix, 5: RTK Float
            fix_types = {0: "No Fix", 1: "GPS", 2: "DGPS", 4: "RTK Fix", 5: "RTK Float"}
            sat_num = int(msg.num_sats)
            
            # print(f"GGA({num}) - Lat: {round(lat,8)} | Lon: {round(lon,8)} | Mode: {fix_types.get(fix_type, 'Unknown')} | Satellite:{sat_num}     ", end="\r")
            if record_requested == True:
                RTK_data.append([lat, lon, fix_types.get(fix_type, 'Unknown'), sat_num])
                print("Save Successfully!!")
                record_requested = False

            time.sleep(0.1)
    
    except pynmea2.ParseError:
        pass

def keyboard_listener():
    global record_requested
    while True:
        # Check for input without blocking using select.select()
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)  # Timeout is 0.1 seconds
        if rlist:
            key = sys.stdin.readline().strip()  # Read input without blocking
            if key.lower() == 'r':
                record_requested = True
                print("[按下 r] 將儲存下一筆 GGA 座標")

def main():
    # Connect to ZED-F9P UART
    threading.Thread(target=keyboard_listener, daemon=True).start()

    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    sock = connect_to_ntrip()
    if not sock:
        return

    last_rtcm_data = b''
    num=0
    try:
        while True:
            try:
                start = time.time()
                data = sock.recv(4096)
                last_rtcm_data = data
                ser.write(data)  # Send RTCM to ZED-F9P

                # Analyze GGA message
                while ser.in_waiting > 0:
                    line = ser.readline().decode('ascii', errors='ignore').strip()
                    if line.startswith("$GNGGA"):
                        parse_nmea(line, num)
                        sock.sendall((line + "\r\n").encode('ascii'))
                        num += 1
            
                print(time.time() - start)

            except socket.error as e:
                print("\n[Socket Error]", e)
                print("NTRIP Reconnecting...")
                sock.close()
                time.sleep(0.1)
                sock = connect_to_ntrip()
                if not sock:
                    print("Retrying in 3 seconds...")
                    time.sleep(3)
            except serial.SerialException as e:
                print("\n[Serial Error]", e)

    except KeyboardInterrupt:
        print("\nShutdown")
        
    finally:
        current_date = time.strftime('%Y-%m-%d', time.localtime())
        current_time = time.strftime('_%H-%M-%S', time.localtime())
        rtk_folder_path = f'./RTK_data/{current_date}'
        os.makedirs(rtk_folder_path, exist_ok=True)
    
        with open(rtk_folder_path + '/RTK_'+ current_date + current_time +'.csv', 'w', newline='') as output:
            writer = csv.writer(output)
            writer.writerows(RTK_data)
        
        sock.close()
        ser.close()
        RTK_data.clear()


if __name__ == "__main__":
    main()
