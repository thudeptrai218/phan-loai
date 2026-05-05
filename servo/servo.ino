#include <Servo.h>

Servo servo1;
Servo servo2;

unsigned long servo1StartTime = 0;
unsigned long servo2StartTime = 0;
unsigned long servo2DelayStartTime = 0;
bool servo1Active = false;
bool servo2Active = false;
bool servo2Delayed = false;

const unsigned long SERVO_GAT_TIME = 500;  // Thời gian gạt servo (ms)
const unsigned long SERVO2_DELAY = 1450;   // Thời gian trễ trước khi gạt (ms) (Có thể điều chỉnh)

void setup() {
    Serial.begin(9600);
    servo1.attach(9);
    servo2.attach(10);

    servo1.write(90);
    servo2.write(90);
}

void loop() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();

        if (command == "1") {  
            servo1.write(45);  
            servo1StartTime = millis();
            servo1Active = true;
        } 
        else if (command == "2") {  
            servo2DelayStartTime = millis();  // Lưu thời điểm bắt đầu đợi
            servo2Delayed = true;  // Bật cờ báo hiệu đang chờ
        }
    }

    // Kiểm tra nếu đã đủ thời gian trễ, thì bắt đầu gạt servo 2
    if (servo2Delayed && millis() - servo2DelayStartTime > SERVO2_DELAY) {
        servo2.write(45);
        servo2StartTime = millis();
        servo2Active = true;
        servo2Delayed = false;  // Reset cờ chờ
    }

    if (servo1Active && millis() - servo1StartTime > SERVO_GAT_TIME) {  
        servo1.write(90);
        servo1Active = false;
    }

    if (servo2Active && millis() - servo2StartTime > SERVO_GAT_TIME) {  
        servo2.write(90);
        servo2Active = false;
    }
}
