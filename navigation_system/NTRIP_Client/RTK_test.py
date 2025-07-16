import socket
import base64
import serial
import pyrtcm
from pyrtcm import RTCMReader
import pynmea2
import yaml

# config file
config_file = "NTRIP_config.yaml"
with open(config_file, "r") as file:
    config = yaml.safe_load(file)
    
    NTRIP_HOST = config["Caster"]
    NTRIP_PORT = config["Port"]
    MOUNTPOINT = config["Mount_Point"]
    USERNAME = config["User"]
    PASSWORD = config["Password"]

SERIAL_PORT = "/dev/ttyAMA0"
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

def parse_nmea(nmea_str):
    """Analyze NMEA message to receive location message"""
    try:
        msg = pynmea2.parse(nmea_str)
        if isinstance(msg, pynmea2.types.talker.GGA):  # Analyze GGA message
            lat = msg.latitude
            lon = msg.longitude
            fix_type = msg.gps_qual
            fix_types = {0: "No Fix", 1: "GPS", 2: "DGPS", 4: "RTK Fix", 5: "RTK Float"}
            print(f"GGA - long: {lon}, lat: {lat}, mode: {fix_types.get(fix_type, 'Unknown')}")
    except pynmea2.ParseError:
        pass  # Ignore the unvaliable NMEA message

def main():
    # Connect to ZED-F9P UART
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

    # Connect to RTK2GO NTRIP Caster
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((NTRIP_HOST, NTRIP_PORT))
    sock.sendall(get_ntrip_request())

    # Check NTRIP response
    response = sock.recv(1024).decode(errors='ignore')
    if "200 OK" not in response:
        print("NTRIP connect fail:", response)
        sock.close()
        return

    print("Successfully connect to RTK2GO, Receiving RTCM message...")

    try:
        while True:
            data = sock.recv(4096)
            try:
                msg = RTCMReader.parse(data)
                print("RTCM message:", msg)
                ser.write(data)

                while ser.in_waiting > 0:
                    line = ser.readline().decode('ascii', errors='ignore').strip()
                    if line.startswith("$GNGGA"):
                        parse_nmea(line)

            except pyrtcm.exceptions.RTCMParseError as e:
                print("RTCM analyzing error")
                pass

    except KeyboardInterrupt:
        print("Program stop")
    finally:
        sock.close()
        ser.close()

if __name__ == "__main__":
    main()
