import RPi.GPIO as GPIO
import time

# Select BCM number
GPIO.setmode(GPIO.BCM)

# Define GPIO pin
SW_PINS = {
    12: "SW1 (GPIO12)",
    16: "SW2 (GPIO16)",
    21: "SW3 (GPIO21)",
}

# Set as input with pull-down resistance
for pin in SW_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def on_rising(channel):
    print(f"[{time.strftime('%H:%M:%S')}] Triggered: {SW_PINS[channel]}")

# Event detection: Rasing voltage to 3.3v with filtering vibration (bouncetime=50~200ms)
for pin in SW_PINS:
    GPIO.add_event_detect(pin, GPIO.RISING, callback=on_rising, bouncetime=100)

print("Waiting for trigger on (Ctrl+C to exit)...")
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
