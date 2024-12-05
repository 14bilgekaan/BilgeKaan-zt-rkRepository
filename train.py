from ultralytics import YOLO


model = YOLO("yolov8n.yaml")  # Kendi modelini üret

# Eğitim parametreleri
model.train(data="C:/Users/User/Desktop/haar cascade/haar cascade/config.yaml", epochs=10,batch=16)
