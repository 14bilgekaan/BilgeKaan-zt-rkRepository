#include <Servo.h>

Servo myservo;
int servoPin = 9;
int pos = 90;  // Servo başlangıç pozisyonu (90 derece)
int screenWidth = 900;  // Ekran genişliği
int centerX = screenWidth / 2;
int speed = 5;  // Dönüş hızı

void setup() {
  Serial.begin(9600);
  myservo.attach(servoPin);
  myservo.write(pos);  // Servoyu başlangıç pozisyonuna getir
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    int x_center = data.toInt();

    // Ekran merkezine göre servonun dönüş yönünü belirle
    if (x_center < centerX) {
      pos -= speed;  // Sola döndür
      if (pos > 180) pos = 180;  // 180 dereceden fazla dönmemesi için sınır koy
    } else {
      pos += speed;  // Sağa döndür
      if (pos < 0) pos = 0;  // 0 dereceden az dönmemesi için sınır koy
    }

    myservo.write(pos);  // Servo motoru yeni pozisyona getir

    delay(15);  // Servonun hareketine zaman tanı
  }
}
