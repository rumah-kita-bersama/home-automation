#include <ESP8266WiFi.h>

void connectWifi() {
  WiFi.persistent(false);
  WiFi.setOutputPower(5);
  WiFi.setSleepMode(WIFI_LIGHT_SLEEP, 10);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  reconnectWiFi();
}

void reconnectWiFi() {
  while (WiFi.status() != WL_CONNECTED && !WiFi.localIP()) {
    Serial.println("Couldn't get a wifi connection");
    delay(5000);
  }
  // Serial.println(WiFi.localIP());
  // Serial.println("Connected");
}
