import serial
import time

# UBX command：launch RTCM 1005 and 1077（binary format）
UBX_CFG_MSG_1005 = bytes.fromhex("B5 62 06 01 03 00 F5 05 01 03 0F")
UBX_CFG_MSG_1077 = bytes.fromhex("B5 62 06 01 03 00 F5 4D 01 4B 6F")

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(1)

ser.write(UBX_CFG_MSG_1005)
time.sleep(0.1)
ser.write(UBX_CFG_MSG_1077)
time.sleep(0.1)

ser.close()
