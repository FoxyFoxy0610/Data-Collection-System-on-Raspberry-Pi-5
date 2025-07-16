import smbus
import time

bus = smbus.SMBus(1)
MPU_ADDR = 0x68

# Initialize MPU9250
def mpu_init():
    bus.write_byte_data(MPU_ADDR, 0x6B, 0x00)  # Power management register: wake up
    print('Initialize IMU...')
    time.sleep(0.1)

# Read two bytes and combine to the signed integer
def read_raw_data(addr):
    high = bus.read_byte_data(MPU_ADDR, addr)
    low = bus.read_byte_data(MPU_ADDR, addr + 1)
    value = (high << 8) | low
    if value > 32767:
        value -= 65536
    return value

mpu_init()
print("Start to reading MPU9250 data...")

while True:
    ax = read_raw_data(0x3B) / 16384.0 * 90
    ay = read_raw_data(0x3D) / 16384.0 * 90
    az = read_raw_data(0x3F) / 16384.0 * 90

    gx = read_raw_data(0x43) / 131.0
    gy = read_raw_data(0x45) / 131.0
    gz = read_raw_data(0x47) / 131.0

    print(f"Accel(g): X={ax:.2f} Y={ay:.2f} Z={az:.2f} || Gyro (°/s): X={gx:.2f} Y={gy:.2f} Z={gz:.2f}", end = '\r')
    time.sleep(0.1)
