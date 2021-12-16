#include <ESP8266WebServer.h>

ESP8266WebServer server(80);

void setupWebserver() {
   server.on("/", handle);
   server.on("/ping", healthCheck);
   server.begin();
}

void handleClientWebserver() {
  server.handleClient();
}

void handle() {

   int power = server.arg("power").toInt();
   int temp = server.arg("temp").toInt();
   int hvac = server.arg("hvac").toInt();
   int fan = server.arg("fan").toInt();
   int vane = server.arg("vane").toInt();

   if ((temp >= 16 && temp <= 31)) {
     sendCommand(power, temp, hvac, fan, vane);
     server.send(200, "text/plain", "Ok");
     return;
   }

   server.send(400, "text/plain", "Bad request");
   return;
}

void healthCheck() {
   server.send(200, "text/plain", "PONG");
}