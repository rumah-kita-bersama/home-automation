#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include "secrets.h"

#define NUM_RETRY 10
#define HOST "api.telegram.org"
#define SEND_THRESHOLD_MILLIS 10000
#define BELL_PIN D8

WiFiClientSecure httpsClient;
unsigned long lastSentMillis = 0, lastMillis = 0, currentMillis = 0;
bool isLastSentSet = false;
char buf[1024];

void setup() {
  // Serial.begin(115200);
  // delay(1000);

  connectWiFi();
  setupHttpsClient();
  pinMode(BELL_PIN, INPUT);
}

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    // Serial.printf("Connecting...\n");
  }
}

void setupHttpsClient() {
  httpsClient.setInsecure();
  httpsClient.setTimeout(15000);
}

void loop() {
  currentMillis = millis();

  // in case millis() overflow, reset all states
  if (currentMillis < lastMillis) {
    isLastSentSet = false;
  }
  
  int readValue = digitalRead(BELL_PIN);  
  if (readValue) {
    // Serial.printf("Signal %d...\n", readValue);
    if (shouldSend()) {
      // Serial.printf("Sending...\n");    
      sendMessage("Assalamualaikum, ada orang di depan.");
      isLastSentSet = true;
      lastSentMillis = currentMillis;
    }
  }

  lastMillis = currentMillis;

  delay(50); // reduce power usage
}

bool shouldSend() {
  if (!isLastSentSet) {
    return true;
  }

  if (currentMillis - lastSentMillis >= SEND_THRESHOLD_MILLIS) {
    return true;
  }

  return false;
}

int sendMessage(char* text) {
  for (int i = 0; i < NUM_RETRY; i++) {
    if (httpsClient.connect(HOST, 443)) {
      break;
    }

    // Serial.printf("Failed to connect HTTPS...\n");
    return -1;
  }

  sprintf(buf, "GET /bot%s/sendMessage?text=%s&chat_id=%s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n", BOT_TOKEN, text, CHAT_ID, HOST);
  return httpsClient.println(buf);
}
