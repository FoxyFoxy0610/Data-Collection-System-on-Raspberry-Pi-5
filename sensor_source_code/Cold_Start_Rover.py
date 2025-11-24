import serial
import time
import pynmea2
import time

start = time.time()
while True:
    try:
        port="/dev/ttyACM0"
        ser=serial.Serial(port, baudrate=115200, timeout=0.5)
        dataout = pynmea2.NMEAStreamReader()
        newdata=ser.readline().decode('ascii', errors='ignore').strip()
        print(newdata)

        if newdata.startswith("$GNRMC"):
            newmsg=pynmea2.parse(newdata)
            lat = newmsg.latitude
            lon = newmsg.longitude
            fix_type = newmsg.mode_indicator
            fix_types = {'D': "DGPS", 'A': "Autonomous", 'E': "Estimated", 'N': "Invalid"}
            print(f"Cold starting:{fix_types.get(fix_type)} | {round(time.time()-start)} seconds", end = '\r')
            if fix_types.get(fix_type) == "Autonomous":
                print("\nCold start finish!!")
                break

    except pynmea2.ParseError:
        pass

    except KeyboardInterrupt:
        print("Exiting program.")
        break