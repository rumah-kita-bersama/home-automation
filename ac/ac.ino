#define ENABLE_WEBSERVER 0
#define ENABLE_TELEGRAM 1

void setup() {
  Serial.begin(115200);

  connectWifi();
  setupSender();
  if (ENABLE_WEBSERVER) {
    setupWebserver();
  }
  if (ENABLE_TELEGRAM) {
    setupTelegram();
  }
}


void loop() {   
  if (ENABLE_WEBSERVER) {
    handleClientWebserver(); 
  }
  if (ENABLE_TELEGRAM) {
    getUpdatesLongPollTelegram();
  }
}
