from ultralytics import YOLO

# Replace Dataset/data.yaml with a rotten-fruit YOLO dataset that uses:
# names:
#   0: Trai cay tot
#   1: Trai cay hong
DATA_YAML = "Dataset/data.yaml"
BASE_MODEL = "yolov8s.pt"

model = YOLO(BASE_MODEL)

model.train(
    data=DATA_YAML,
    epochs=50,
    imgsz=640,
    batch=16,
    project="runs/detect",
    name="rotten_fruit",
)
