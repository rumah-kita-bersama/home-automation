#include <IRremote.h>

// Ref:
// https://www.analysir.com/blog/2015/01/06/reverse-engineering-mitsubishi-ac-infrared-protocol/
// https://github.com/r45635/HVAC-IR-Control/blob/master/HVAC_ESP8266/HVAC_ESP8266.ino

#define K_KHZ 38
#define K_HEADER_MARK 3400
#define K_HEADER_SPACE 1680
#define K_BIT_MARK 440
#define K_ONE_SPACE 1260
#define K_ZERO_SPACE 420
#define K_RPT_MARK 440
#define K_RPT_SPACE 12740

#define EMIT_PIN D1

void setupSender() {
  pinMode(EMIT_PIN, OUTPUT);
  IrSender.begin(EMIT_PIN, 0, 0);
}

int sendCommand(bool off, byte temp, byte swing, byte fan) {
  // base command
  byte data[18] = {0x23, 0xcb, 0x26, 0x01, 0x00, 0x00, 0x18, 0x00, 0x36, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

  // on/off
  data[5] = (byte) 0x20;
  if (off) {
    data[5] = (byte) 0x00;
  }

  // temp
  if (temp < 18 || temp > 30) {
    return -1;
  }
  data[7] = temp - 16;


  // fan speed, either 2 or 3
  data[9] = (byte) 0x02;
  if (fan) {
    data[9] = (byte) 0x03;  
  }

  // swing auto/off
  if (swing) {
    data[9] = (byte) data[9] | 0x78;
  } else {
    data[9] = (byte) data[9] | 0x48;
  }

  // CRC
  data[17] = 0;
  for (int i = 0; i < 17; i++) {
    data[17] = (byte) data[i] + data[17]; // CRC is a simple bits addition
  }


  IrSender.enableIROut(K_KHZ);

  IrSender.mark(K_HEADER_MARK);
  IrSender.space(K_HEADER_SPACE);
  for (int j = 0; j < 18; j++) {
    byte bitz = 1;
    for (int k = 0; k < 8; k++) {
      IrSender.mark(K_BIT_MARK);
      if ((data[j] & bitz) > 0) {
        IrSender.space(K_ONE_SPACE);
      } else {
        IrSender.space(K_ZERO_SPACE);
      }

      bitz = bitz << 1;
    }
  }
  IrSender.mark(K_RPT_MARK);
  IrSender.space(K_RPT_SPACE);

  IrSender.mark(K_HEADER_MARK);
  IrSender.space(K_HEADER_SPACE);

  IrSender.mark(K_BIT_MARK);
  IrSender.space(K_ONE_SPACE);

  IrSender.mark(K_BIT_MARK);
  IrSender.space(K_ONE_SPACE);

  IrSender.mark(K_BIT_MARK);
  IrSender.space(0);
  return 0;
}
