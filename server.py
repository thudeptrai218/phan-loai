from pathlib import Path
from flask import Flask, render_template, Response, jsonify
import cv2
import requests
import time
from ultralytics import YOLO

ESP8266_URL = "http://192.168.162.6/control"
ESP32CAM_STREAM_URL = "http://192.168.162.6:81/stream"
MODEL_PATH = "runs/detect/rotten_fruit/weights/best.pt"
FALLBACK_MODEL_PATH = "yolov8s.pt"

trained_model_available = Path(MODEL_PATH).exists()
model = YOLO(MODEL_PATH if trained_model_available else FALLBACK_MODEL_PATH)

app = Flask(__name__)

processed_objects = set()
history = []

# Train the rotten-fruit model with this label order:
# 0: Trai cay tot
# 1: Trai cay hong
CLASS_NAMES = {
    0: "Trai cay tot",
    1: "Trai cay hong",
}
DEFECTIVE_CLASS_IDS = {1}
SERVO_BY_STATUS = {
    "fresh": 2,
    "defective": 1,
}
CONFIDENCE_THRESHOLD = 0.7

MIN_WIDTH = 30
MIN_HEIGHT = 30
MAX_WIDTH = 500
MAX_HEIGHT = 500


def get_class_name(class_id):
    return CLASS_NAMES.get(class_id, f"Lop {class_id}")


def is_defective(class_id):
    return class_id in DEFECTIVE_CLASS_IDS


def send_servo_command(class_id):
    if not trained_model_available:
        return

    status = "defective" if is_defective(class_id) else "fresh"
    servo = SERVO_BY_STATUS.get(status)
    if servo is None:
        return

    requests.get(f"{ESP8266_URL}?servo={servo}", timeout=1)


def detect_objects():
    cap = cv2.VideoCapture(ESP32CAM_STREAM_URL)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Loi: Khong lay duoc frame tu camera!")
            continue

        results = model(frame)

        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            width, height = x2 - x1, y2 - y1

            if width < MIN_WIDTH or height < MIN_HEIGHT or width > MAX_WIDTH or height > MAX_HEIGHT:
                continue

            obj_id = f"{class_id}_{x1}_{y1}"

            if confidence > CONFIDENCE_THRESHOLD and obj_id not in processed_objects:
                class_name = get_class_name(class_id)
                defective = is_defective(class_id)
                status = "Hong" if defective else "Tot"
                if not trained_model_available:
                    class_name = model.names.get(class_id, class_name)
                    status = "Chua huan luyen"
                color = (0, 0, 255) if defective else (0, 255, 0)
                label = f"{class_name} - {status} ({confidence:.2f})"

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2,
                )

                try:
                    send_servo_command(class_id)
                except requests.exceptions.RequestException:
                    print("Loi: Khong the gui lenh den ESP8266!")

                history.append(
                    {
                        "time": time.strftime("%H:%M:%S"),
                        "fruit": class_name,
                        "status": status,
                    }
                )
                processed_objects.add(obj_id)

        yield frame


def generate_frames():
    for frame in detect_objects():
        _, buffer = cv2.imencode(".jpg", frame)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )


@app.route("/")
def index():
    return render_template("web_dashboard.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/history")
def get_history():
    return jsonify(history)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6003, debug=True)
