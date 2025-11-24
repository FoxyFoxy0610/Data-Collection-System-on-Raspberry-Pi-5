import serial
import pynmea2

# Setting ZED-F9P UART
SERIAL_PORT = "/dev/ttyAMA0"
BAUD_RATE = 115200

def parse_nmea(nmea_str):
    """Analyze NMEA message to extract longtitude and latitude"""
    try:
        msg = pynmea2.parse(nmea_str)
        if isinstance(msg, pynmea2.types.talker.GGA):  # Analysis GGA 
            lat = msg.latitude
            lon = msg.longitude
            fix_type = msg.gps_qual  # 0: None, 1: GPS, 2: DGPS, 4: RTK Fix, 5: RTK Float
            fix_types = {0: "No Fix", 1: "GPS", 2: "DGPS", 4: "RTK Fix", 5: "RTK Float"}
            print(f"Lon: {lon}, Lat: {lat}, mode: {fix_types.get(fix_type, 'Unknown')}")
    except pynmea2.ParseError:
        pass

def main():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("Start reading NMEA message...")
    
    try:
        while True:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if line.startswith("$GNGGA"):
                parse_nmea(line)
                
    except KeyboardInterrupt:
        print("Shutdown")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
