// uncomment to enable
#define ENABLE_WEBSERVER
//#define ENABLE_TELEGRAM
//#define ENABLE_REPLAY


// to measure voltage
// ADC_MODE(ADC_VCC);

void setup() {
  Serial.begin(115200);

  connectWifi();
  setupSender();

#ifdef ENABLE_WEBSERVER
  // disable OTA
  // setupOTA();
  setupWebserver();
#endif

// OTA is not working on Telegram because it
// would use long poll for retrieving msg and blocks the OTA
#ifdef ENABLE_TELEGRAM
  setupTelegram();
#endif

  // turn off built-in LED
  pinMode(D0, OUTPUT);
}

void loop() {
  reconnectWiFi();

#ifdef ENABLE_WEBSERVER
  // disable OTA
  // handleOTA(); 
  handleClientWebserver();
#endif

#ifdef ENABLE_TELEGRAM
  getUpdatesLongPollTelegram();
#endif

#ifdef ENABLE_REPLAY
  sendReplay();
  delay(2000);
#endif

  // turn off built-in LED
  digitalWrite(D0, HIGH);

  // to read voltage
  // readVoltage();

  // delay to save battery
  delay(100);
}
