#define ENABLE_WEBSERVER 1
#define ENABLE_TELEGRAM 0

void setup() {
  Serial.begin(115200);
  
  connectWifi();
  setupSender();
  
  #ifdef ENABLE_WEBSERVER
  if (ENABLE_WEBSERVER) {
    setupOTA();
    setupWebserver();
  }
  #endif

  #ifdef ENABLE_TELEGRAM
  if (ENABLE_TELEGRAM) {
    setupTelegram();
  }
  #endif
}


void loop() {  

  #ifdef ENABLE_WEBSERVER
  if (ENABLE_WEBSERVER) {
    handleOTA();
    handleClientWebserver(); 
  }
  #endif

  #ifdef ENABLE_TELEGRAM
  if (ENABLE_TELEGRAM) {
    getUpdatesLongPollTelegram();
  }
  #endif
}
