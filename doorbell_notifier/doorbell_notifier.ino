#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h> 

#define NUM_RETRY 10
#define HOST "api.telegram.org"
#define SEND_THRESHOLD_MILLIS 6000
#define BELL_PIN D8

WiFiClientSecure httpsClient;
const char fingerprint[] PROGMEM = "F2 AD 29 9C 34 48 DD 8D F4 CF 52 32 F6 57 33 68 2E 81 C1 90";
unsigned long lastSentMillis = 0, lastMillis = 0, currentMillis = 0;
bool isLastSentSet = false;
char buf[1024];

void setup() {
  connectWiFi();
  setupHttpsClient();
  pinMode(BELL_PIN, INPUT);
  Serial.println("ready");
}

void connectWiFi() {
  Serial.begin(9600);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
  }
}

void setupHttpsClient() {
  httpsClient.setFingerprint(fingerprint);
  httpsClient.setTimeout(15000);
}

void loop() {
  currentMillis = millis();

  // in case millis() overflow, reset all states
  if (currentMillis < lastMillis) {
    isLastSentSet = false;
  }
  
  if (digitalRead(BELL_PIN)) {
    Serial.print(currentMillis);
    Serial.println(" on");
    if (shouldSend()) {
      sendMessage("Oi anjing! Ada orang di depan.");
      isLastSentSet = true;
      lastSentMillis = currentMillis;
    }
  }

  lastMillis = currentMillis;
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

    return -1;
  }

  sprintf(buf, "GET /bot%s/sendMessage?text=%s&chat_id=%s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n", BOT_TOKEN, text, CHAT_ID, HOST);
  return httpsClient.println(buf);
}
