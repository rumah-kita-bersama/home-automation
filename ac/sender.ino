#include <IRremote.h>

#define K_KHZ 38
#define K_UNIT 440
#define K_HEADER_MARK (8 * K_UNIT)  // 3520 ~3464
#define K_HEADER_SPACE (4 * K_UNIT) // 1760 ~1692
#define K_BIT_MARK K_UNIT
#define K_ONE_SPACE (3 * K_UNIT) // 1320 ~1240
#define K_ZERO_SPACE K_UNIT

#define EMIT_PIN D0

void setupSender() {
  pinMode(EMIT_PIN, OUTPUT);  
  IrSender.begin(EMIT_PIN, 0, 0);    
}

void sendCommand(int cmd) {
  // base command
  byte data[18] = {0x23, 0xCB, 0x26, 0x01, 0x00, 0xa0, 0x3, 0xf, 0x0, 0x0, 0x0, 0x20, 0x0, 0x0};

  IrSender.enableIROut(K_KHZ);
  IrSender.mark(K_HEADER_MARK);
  IrSender.space(K_HEADER_SPACE);

  // cmd < 0 off
  // 16 <= cmd <= 31
  if (cmd >= 0 && !(cmd >= 16 && cmd <= 31)) {
    return;
  }

  if (cmd >= 16 && cmd <= 31) {
    byte temp = (byte) cmd;   
    data[5] = data[5] | (byte)0x4; // set to on
    data[7] = ~(~data[7] | temp); // flip bit, or, and flip again
  }

  // byte 13 - CRC
  data[13] = 0;
  for (int i = 0; i < 13; i++) {
    data[13] = (byte)data[i] + data[13]; // CRC is a simple bits addition
  }

  for (int i = 0; i < 14; i++) {
    byte bitz = 1;
    for (int j = 0; j < 8; j++) {
      IrSender.mark(K_BIT_MARK);

      if ((data[i] & bitz) > 0) {
        IrSender.space(K_ONE_SPACE);       
      } else {
        IrSender.space(K_ZERO_SPACE);
      }

      bitz = bitz << 1;
    }
  }

  IrSender.mark(K_BIT_MARK);  
}
