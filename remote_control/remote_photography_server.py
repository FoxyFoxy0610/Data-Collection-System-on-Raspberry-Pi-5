import socket
import paho.mqtt.client as mqtt
import threading
import time
import sys

SERVER_IP = "192.168.50.22"
PORT = 8000
MQTT_BROKER = "192.168.50.22"

device_status = {}
running = True

# Monitor the connection status
def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected.")
    client.subscribe("camera/+/status")
    print("[MQTT] Subscribed to all device status.")


def on_message(client, userdata, msg):
    topic = msg.topic         # camera/CAM01/status
    payload = msg.payload.decode()
    cam_id = topic.split("/")[1]

    device_status[cam_id] = payload

    print(f"[STATUS] {cam_id} → {payload}")
    print(f"[STATUS] Devices: {device_status}")


# Receive the image by socket
def socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((SERVER_IP, PORT))
        s.listen(5)
        print("[SOCKET] Waiting for camera connections...")

        while running:
            try:
                s.settimeout(1.0)
                conn, addr = s.accept()
            except socket.timeout:
                continue

            threading.Thread(target=handle_client, args=(conn, addr)).start()


def handle_client(conn, addr):
    try:
        print(f"[SOCKET] Connected from {addr}")

        cam_id_raw = b""
        while b"::" not in cam_id_raw:
            cam_id_raw += conn.recv(1)
        cam_id = cam_id_raw.replace(b"::", b"").decode()
        print(f"[SOCKET] Receiving from {cam_id}")

        img_data = b""
        while True:
            packet = conn.recv(4096)
            if not packet:
                break
            img_data += packet

        save_path = f"{cam_id}_{int(time.time())}.jpg"
        with open(save_path, "wb") as f:
            f.write(img_data)

        print(f"[SAVE] Saved: {save_path}")

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        conn.close()


def keyboard_loop(mqtt_client):
    global running

    print("\n=== Server Command Menu ===")
    print("R → Trigger capture on ALL cameras")
    print("S → Show online/offline device list")
    print("Q → Quit program")
    print("============================\n")

    while running:
        key = input("Enter command (R/S/Q): ").strip().lower()

        if key == "r":
            print("[CMD] Broadcasting capture command to all cameras...")
            mqtt_client.publish("camera/all/cmd", "capture", qos=1)
        
        elif key == "s":
            print("\n===== Device Status =====")
            if not device_status:
                print("No devices online yet.")
            else:
                for cam, st in device_status.items():
                    print(f"{cam}: {st}")
            print("=========================\n")

        elif key == "q":
            print("[SYSTEM] Shutting down server...")
            running = False
            break

        else:
            print("[ERROR] Unknown command. Use R / S / Q.")


def main():
    global running

    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, 1883, 60)

    threading.Thread(target=mqtt_client.loop_forever, daemon=True).start()
    threading.Thread(target=socket_server, daemon=True).start()

    keyboard_loop(mqtt_client)
    print("[SYSTEM] Program fully exited.")


if __name__ == "__main__":
    main()
