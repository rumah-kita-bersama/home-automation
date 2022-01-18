#ifdef ENABLE_TELEGRAM

#include <WiFiClientSecure.h>
#include <UniversalTelegramBot.h>

#define LONG_POLL_SEC 60
#define SCAN_INTERVAL 1000

const char fingerprint[] PROGMEM = "F2 AD 29 9C 34 48 DD 8D F4 CF 52 32 F6 57 33 68 2E 81 C1 90";

WiFiClientSecure https_client;
UniversalTelegramBot bot(BOT_TOKEN, https_client);

unsigned long last_time = 0; 

void setupTelegram() {
  // manual setup https related
  https_client.setFingerprint(fingerprint);
  https_client.setTimeout(15000);
  
  bot.longPoll = LONG_POLL_SEC;
}

void getUpdatesLongPollTelegram() {  
  unsigned long now = millis();
  if (now - last_time > SCAN_INTERVAL || now - last_time < 0) {
    int numNewMessages = bot.getUpdates(bot.last_message_received + 1);
    while (numNewMessages) {      
      handleNewMessages(numNewMessages);
      numNewMessages = bot.getUpdates(bot.last_message_received + 1);
    }
    last_time = now;
  }
}

void handleNewMessages(int numNewMessages) {
  for (int i = 0; i < numNewMessages; i++) {  
    if (bot.messages[i].chat_id.equals(ALLOWED_CHAT_ID)) {
      int cmd = bot.messages[i].text.toInt();      
      if (cmd < 0 || (cmd >= 16 && cmd <= 31)) {       
      sendCommand(cmd);
      bot.sendSimpleMessage(bot.messages[i].chat_id, "OK", "");
    } else {
      bot.sendSimpleMessage(bot.messages[i].chat_id, "Invalid", "");
    }
    }
  }
}

#endif
