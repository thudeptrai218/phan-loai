import cv2
from ultralytics import YOLO

url = "http://172.20.10.2:81/stream"
model = YOLO("runs/detect/rotten_fruit/weights/best.pt")

cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("Khong the ket noi den ESP32-CAM!")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Loi khi nhan du lieu tu camera!")
        break

    results = model(frame)

    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        confidence = float(box.conf[0])
        class_id = int(box.cls[0])

        if confidence > 0.75:
            class_name = model.names.get(class_id, f"Lop {class_id}")
            defective = class_id == 1
            color = (0, 0, 255) if defective else (0, 255, 0)
            status = "Hong" if defective else "Tot"
            label = f"{class_name} - {status} {confidence:.2f}"

            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(
                frame,
                label,
                (int(x1), int(y1) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

    cv2.imshow("ESP32-CAM Live Stream", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
