from picamera2 import Picamera2
from libcamera import controls
import time
import cv2

picam2 = Picamera2()

video_config = picam2.create_video_configuration(
    main={"size": (1640, 1232)},
    controls={
        "ExposureTime": 5000,         # unit: microseconds（μs）
        "AnalogueGain": 0.0,          # ISO (4.0 ~ 12.0）
    }
)
picam2.configure(video_config)

frame_width = 960
frame_height = 720
fps = 30
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter("./video_test.mp4", fourcc, fps, (frame_width, frame_height))

try:
    picam2.start()
    time.sleep(1)
    # picam2.start_and_record_video("video.mp4", duration=5)

    while True:
        start = time.time()
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (frame_width, frame_height))
        out.write(frame)
        print(time.time()-start)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Exiting program...")

finally:
    # Release Webcam source
    out.release()
    cv2.destroyAllWindows()
    print(f"Video recording finish!")
