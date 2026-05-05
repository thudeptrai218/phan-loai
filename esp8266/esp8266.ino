#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "IoT Network";
const char* password = "aiotlab@123";

// Cấu hình Static IP
IPAddress local_ip(192, 168, 162, 6);      // Địa chỉ IP tĩnh
IPAddress gateway(192, 168, 160, 1);       // Địa chỉ Gateway
IPAddress subnet(255, 255, 248, 0);        // Subnet mask

ESP8266WebServer server(80);

void setup() {
    Serial.begin(9600);
    
    // Cấu hình IP tĩnh trước khi kết nối WiFi
    WiFi.config(local_ip, gateway, subnet);
    WiFi.begin(ssid, password);

    Serial.print("Đang kết nối WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\n✅ WiFi kết nối thành công!");
    
    Serial.print("📶 Địa chỉ IP của ESP8266: ");
    Serial.println(WiFi.localIP());

    server.on("/control", HTTP_GET, []() {
        String servo = server.arg("servo");

        if (servo == "1" || servo == "2") {
            Serial.println("🔄 Gửi lệnh Servo: " + servo);
            Serial.println(servo);  

            // Phản hồi ngay lập tức cho Flask để tránh bị timeout
            server.send(200, "text/plain", "OK Servo " + servo);
        } else {
            server.send(400, "text/plain", "Invalid request");
        }
    });

    server.begin();
    Serial.println("🌐 Server ESP8266 đã khởi động!");
}

void loop() {
    server.handleClient();
}