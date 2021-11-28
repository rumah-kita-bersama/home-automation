#include <ESP8266WiFi.h>

void connectWifi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while ( WiFi.status() != WL_CONNECTED) {
    Serial.println("Couldn't get a wifi connection");
    delay(5000);
  }
  Serial.println(WiFi.localIP());
  Serial.println("Connected");  
}
