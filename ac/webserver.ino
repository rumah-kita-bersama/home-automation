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
   if (!server.hasArg("cmd")){
      server.send(400, "text/plain", "Bad request");
      return;
   }

   int cmd = server.arg("cmd").toInt();
   if (cmd < 0 || (cmd >= 16 && cmd <= 31)) {
     sendCommand(cmd);
     server.send(200, "text/plain", "Ok");
     return;
   }

   server.send(400, "text/plain", "Bad request");
   return;
}
