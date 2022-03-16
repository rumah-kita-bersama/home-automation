#ifdef ENABLE_WEBSERVER

#include <ESP8266WebServer.h>

ESP8266WebServer server(80);

void setupWebserver() {
   server.on("/", handle);
   server.begin();
}

void handleClientWebserver() {
  server.handleClient();
}

void handle() {
  if (!server.hasArg("temp")){
    retBadReq();
    return;
  }
  int temp = server.arg("temp").toInt();
  if (temp < 17 || temp > 30) {
   retBadReq();
   return;
  }
  
  if (!server.hasArg("fan")){
    retBadReq();
    return;
  }
  int fan = server.arg("fan").toInt();
  if (fan < 0 || fan > 5) {
   retBadReq();
   return;
  }
  
  if (!server.hasArg("mode")){
    retBadReq();
    return;
  }
  int mode_ = server.arg("mode").toInt();
  if (mode_ < 0 || mode_ > 3) {
   retBadReq();
   return;
  }
  
  if (!server.hasArg("swing")){
    retBadReq();
    return;
  }
  int swing = server.arg("swing").toInt();
  if (swing < 0 || swing > 1) {
   retBadReq();
   return;
  }
  
  if (!server.hasArg("fix")){
    retBadReq();
    return;
  }
  int fix = server.arg("fix").toInt();
  if (fix < 0 || fix > 1) {
   retBadReq();
   return;
  }
  
  if (!server.hasArg("off")){
    retBadReq();
    return;
  }
  int off = server.arg("off").toInt();
  if (off < 0 || off > 1) {
   retBadReq();
   return;
  }
  
  int code = sendCommand(off, fix, temp, mode_, fan, swing, 0);
  if (code != 0) {
   retBadReq();
   return;
  }
  
  server.send(200, "text/plain", "Ok");
  return;
}

void retBadReq() {
  server.send(400, "text/plain", "Bad request");
}

#endif
