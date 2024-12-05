import cv2
import pyautogui
import numpy as np
from ultralytics import YOLO
import serial
import time
import sys

# YOLOv8 modelini yükle
model = YOLO("C:/Users/User/.spyder-py3/runs/detect/train9/weights/best.pt")

# Haar cascade ile yüz algılayıcı
face_casc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Arduino ile seri iletişim kurmak için
try:
    seri = serial.Serial('COM4', 9600)  # COM4 yerine Arduino'nun bağlı olduğu portu yazın
    time.sleep(2)  # Arduino'nun resetlenmesi için kısa bir bekleme
except serial.SerialException as e:
    print(f"Seri port hatası: {e}")
    sys.exit()

# Ekran görüntüsünü al ve belirli bir alanı kes
def Ekran_goruntusu(x, y, width, height):
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return frame

# YOLOv8 ile yüz tanıma işlemi
def Yolo_tani(frame, conf_threshold=0.7):
    results = model(frame)
    faces = results[0].boxes.xyxy.cpu().numpy()
    confidences = results[0].boxes.conf.cpu().numpy()
    
    # Threshold değerinin altındaki tahminleri filtrele
    taninan_yuz = []
    for i, conf in enumerate(confidences):
        if conf >= conf_threshold:
            taninan_yuz.append(faces[i])
    
    return np.array(taninan_yuz)

# Haar cascade ile yüz tanıma işlemi
def Haar_tani(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    yuz = face_casc.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return yuz

# Yüzlerin etrafına dikdörtgen çiz ve konumlarını yazdır
def Bounding_box(frame, faces, is_yolo=True):
    for det in faces:
        if is_yolo:
            x1, y1, x2, y2 = det[:4]
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)  # Lacivert dikdörtgen
            # Yüzün konumunu yazdır
            print(f"0 {int(x1)} {int(y1)} {int(x2-x1)} {int(y2-y1)}")
        else:
            x, y, w, h = det
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Yeşil dikdörtgen
            # Yüzün konumunu yazdır
            print(f"0 {x} {y} {w} {h}")
    return frame

# Motor kontrol fonksiyonu
def control_motor(x_center):
    # Arduino'ya yüzün x merkez koordinatını gönder
    try:
        seri.write(f"{x_center}\n".encode())
        print(f"Arduino'ya gönderildi': {x_center}")
    except serial.SerialException as e:
        print(f"Seri port yazma hatası: {e}")

def main():
    # Ekran görüntüsünün kesileceği alanı belirle
    x, y, width, height = 400, 100, 900, 900
    screen_center = width / 2

    while True:
        # Ekran görüntüsünü al ve belirli bir alanı kes
        frame = Ekran_goruntusu(x, y, width, height)

        # YOLOv8 ile yüz tanıma işlemi yap
        faces = Yolo_tani(frame, conf_threshold=0.3)

        if len(faces) == 0:
            # Eğer YOLOv8 ile yüz algılanmazsa Haar cascade ile yüz tanıma işlemi yap
            faces = Haar_tani(frame)
            Kareli_goruntu = Bounding_box(frame, faces, is_yolo=False)
        else:
            Kareli_goruntu = Bounding_box(frame, faces, is_yolo=True)

        # Yüzlerin merkezini hesapla ve motoru kontrol et
        if len(faces) == 1:
            if isinstance(faces[0], np.ndarray):
                x1, y1, x2, y2 = faces[0][:4]
                x_center = int(x1 + (x2 - x1) / 2)
            else:
                x, y, w, h = faces[0]
                x_center = x + w // 2
            control_motor(x_center)

        # Görüntüyü göster
        cv2.imshow('Yüz tanıma', Kareli_goruntu)

        # 'q' tuşuna basıldığında döngüyü kır
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Pencereyi kapat
    cv2.destroyAllWindows()
    seri.close()  # Seri portu kapat

if __name__ == "__main__":
    main()
