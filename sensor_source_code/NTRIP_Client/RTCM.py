import socket
import base64
import serial
import pyrtcm
from pyrtcm import RTCMReader
import yaml

config_file="NTRIP_config.yaml"
with open(config_file, "r") as file:
    config = yaml.safe_load(file)
    
    NTRIP_HOST = config["Caster"]
    NTRIP_PORT = config["Port"]
    MOUNTPOINT = config["Mount_Point"]
    USERNAME = config["User"]
    PASSWORD = config["Password"]

SERIAL_PORT = "/dev/ttyAMA0"  # UART of Raspberry pi
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

def main():
    # Connect to  ZED-F9P
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=3)

    # Connect to RTK2GO NTRIP Caster
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((NTRIP_HOST, NTRIP_PORT))
    sock.sendall(get_ntrip_request())

    # Check the response
    response = sock.recv(1024).decode(errors='ignore')
    if "200 OK" not in response:
        print("NTRIP is failed to be connected:", response)
        sock.close()
        return

    print("Sucessfully connect to RTK2GO, Receiving the RTCM data...")
    
    try:
        while True:
            data = sock.recv(4096)  # Read RTCM
            try:
                msg = RTCMReader.parse(data)
                print(msg)
                ser.write(data)  # Send to ZED-F9P
            except pyrtcm.exceptions.RTCMParseError as e:
                print("RTCMParseError")
                pass

    except KeyboardInterrupt:
        print("Shutdown")
    finally:
        sock.close()
        ser.close()

if __name__ == "__main__":
    main()
