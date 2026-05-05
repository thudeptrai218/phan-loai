from ultralytics import YOLO

image_path = "Dataset/test/images/image.png"
model = YOLO("runs/detect/rotten_fruit/weights/best.pt")

results = model(image_path, save=True)

for box in results[0].boxes:
    class_id = int(box.cls[0])
    confidence = float(box.conf[0])
    class_name = model.names.get(class_id, f"Lop {class_id}")
    print(f"Nhan dien: {class_name} ({confidence:.2f})")

results[0].show()

print(f"Da nhan dien tren anh: {image_path}")
