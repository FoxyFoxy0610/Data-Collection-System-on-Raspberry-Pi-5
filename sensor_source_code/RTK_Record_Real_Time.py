import socket
import base64
import serial
import pynmea2
import yaml
import threading
import csv
import time
import os
import sys
import select

# ------------------ Global Variable ------------------
last_gga_sent = 0
last_gga_line = None
sock = None
RTK_data = [["Latitude", "Longitude", "mode", "satellite"]]
record_requested = False

# ------------------ Load the config ------------------
with open("NTRIP_Client/NTRIP_config.yaml", "r") as file:
    config = yaml.safe_load(file)
    NTRIP_HOST = config["Caster"]
    NTRIP_PORT = config["Port"]
    MOUNTPOINT = config["Mount_Point"]
    USERNAME = config["User"]
    PASSWORD = config["Password"]

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

# ------------------ NTRIP Request ------------------
def get_ntrip_request():
    auth = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    return (
        f"GET /{MOUNTPOINT} HTTP/1.1\r\n"
        f"User-Agent: NTRIP-Client\r\n"
        f"Authorization: Basic {auth}\r\n\r\n"
    ).encode()

def connect_to_ntrip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((NTRIP_HOST, NTRIP_PORT))
        s.sendall(get_ntrip_request())
        response = s.recv(1024).decode(errors='ignore')
        if "200 OK" not in response:
            print("NTRIP connection fail:", response)
            s.close()
            return None
        print("Connected to NTRIP Caster.")
        return s
    except Exception as e:
        print("Failed to connect to NTRIP:", e)
        return None

# ------------------ RTCM Threadand Resend GGA message ------------------
def rtcm_thread(ser):
    global sock, last_gga_sent, last_gga_line

    while True:
        try:
            data = sock.recv(4096)
            if data:
                ser.write(data)
                try:
                    sock.sendall((last_gga_line + "\r\n").encode('ascii')) # Resend GGA message to caster
                    print("\n Sent GGA after RTCM.")
                except Exception as e:
                    print(f"Failed to send GGA: {e}")
                    sock.close()
                    sock = connect_to_ntrip()
        
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[RTCM Thread Error] {e}")
            try:
                sock.close()
            except:
                pass
            sock = connect_to_ntrip()
            time.sleep(2)

# ------------------ UART GNSS Thread ------------------
last_gga_time = None
last_gga_utc = None

def parse_nmea(nmea_str):
    global record_requested, last_gga_time, last_gga_utc, last_gga_line

    try:
        now = time.time()
        if last_gga_time:
            print(f"[GGA Interval] {now - last_gga_time:.3f} sec")
        last_gga_time = now

        msg = pynmea2.parse(nmea_str)
        if isinstance(msg, pynmea2.types.talker.GGA):
            if msg.timestamp == last_gga_utc:
                return  # Ignore the blocking message
            last_gga_utc = msg.timestamp
            last_gga_line = nmea_str

            lat, lon = msg.latitude, msg.longitude
            sat_num = int(msg.num_sats)
            fix_type = {0: "No Fix", 1: "GPS", 2: "DGPS", 4: "RTK Fix", 5: "RTK Float"}.get(msg.gps_qual, "Unknown")

            print(f"Lat: {round(lat,8)} | Lon: {round(lon,8)} | Mode: {fix_type} | Sat: {sat_num}", end="\r")

            if record_requested:
                RTK_data.append([lat, lon, fix_type, sat_num])
                print("\n Saved current position.")
                record_requested = False
    except pynmea2.ParseError:
        pass

def uart_thread(ser):
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if line.startswith("$GNGGA"):
                parse_nmea(line)

# ------------------ Keyboard Listening Thread ------------------
def keyboard_listener():
    global record_requested
    while True:
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.readline().strip()
            if key.lower() == 'r':
                record_requested = True
                print("\n Will record next GGA position.")

# ------------------ Main Function ------------------
def main():
    global sock

    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    sock = connect_to_ntrip()
    if not sock:
        return

    threading.Thread(target=keyboard_listener, daemon=True).start()
    threading.Thread(target=uart_thread, args=(ser,), daemon=True).start()
    threading.Thread(target=rtcm_thread, args=(ser,), daemon=True).start()

    try:
        while True:
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\n Shutdown requested.")
    finally:
        save_rtk_data()
        if sock:
            sock.close()
        ser.close()

def save_rtk_data():
    current_date = time.strftime('%Y-%m-%d', time.localtime())
    current_time = time.strftime('_%H-%M-%S', time.localtime())
    rtk_folder_path = f'./RTK_data/{current_date}'
    os.makedirs(rtk_folder_path, exist_ok=True)
    csv_path = os.path.join(rtk_folder_path, f'RTK_{current_date}{current_time}.csv')
    with open(csv_path, 'w', newline='') as output:
        csv.writer(output).writerows(RTK_data)
    print(f"\n Saved RTK data to {csv_path}")

if __name__ == "__main__":
    main()
