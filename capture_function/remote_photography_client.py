import paho.mqtt.client as mqtt
import socket
import subprocess

# MQTT Setting
MQTT_BROKER = "192.168.50.22"
MQTT_TOPIC = "camera/capture"

# Socket Setting
SERVER_IP = "192.168.50.22"
SERVER_PORT = 8000

# Take picture (libcamera-still)
def take_photo(filename="image.jpg"):
    subprocess.run(["libcamera-still","--camera", "0", "-o", filename, "-t", "250"], check=True)
    print("Photo taken.")

# Socket function
def send_image_via_socket(filepath):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))
        with open(filepath, "rb") as f:
            data = f.read()
        s.sendall(data)
    print("Image sent to server.")

# Get MQTT information
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8").strip()
    print(f"MQTT Message received: {payload}")
    
    if payload.lower() == "capture":
        print("Capture command received via MQTT.")
        take_photo("image.jpg")
        send_image_via_socket("image.jpg")

# MQTT initialization and listening
def start_mqtt_client():
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883, 60)
    client.subscribe(MQTT_TOPIC)
    print("?MQTT client subscribed. Waiting for capture command...")
    client.loop_forever()

if __name__ == "__main__":
    start_mqtt_client()
