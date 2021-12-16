#include <IRremote.h>

#define K_KHZ 38
#define K_UNIT 440
#define K_HEADER_MARK (8 * K_UNIT)  // 3520 ~3464
#define K_HEADER_SPACE (4 * K_UNIT) // 1760 ~1692
#define K_BIT_MARK K_UNIT
#define K_ONE_SPACE (3 * K_UNIT) // 1320 ~1240
#define K_ZERO_SPACE K_UNIT

#define EMIT_PIN D0

#define K_POWER_ON 1

#define K_HVAC_IFEEL 0
#define K_HVAC_COOL 1
#define K_HVAC_DRY 2
#define K_HVAC_FAN 3

#define K_FAN_SMART 0
#define K_FAN_ONE 1
#define K_FAN_TWO 2
#define K_FAN_THREE 3

#define K_VANE_SMART 0
#define K_VANE_ONE 1
#define K_VANE_TWO 2
#define K_VANE_THREE 3
#define K_VANE_FOUR 4
#define K_VANE_FIVE 5
#define K_VANE_FLAP 6

void setupSender() {
  pinMode(EMIT_PIN, OUTPUT);  
  IrSender.begin(EMIT_PIN, 0, 0);    
}

void sendCommand(int power, int temp, int hvacmode, int fanmode, int vanemode) {
  // base command
  byte data[18] = {0x23, 0xCB, 0x26, 0x01, 0x00, 0xa0, 0x3, 0xf, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0};

  IrSender.enableIROut(K_KHZ);
  IrSender.mark(K_HEADER_MARK);
  IrSender.space(K_HEADER_SPACE);

  // Power handling
  if (power == 1) {
    data[5] = data[5] | (byte)0x4;
  }

  // Temp handling
  if (!(temp >= 16 && temp <= 31)) {
    return;
  } else {
    data[7] = ~(~data[7] | (byte)temp);
  }

  // HVAC mode handling
  if (hvacmode != K_HVAC_COOL) {
    data[7] = 0x07;
  }

  if (hvacmode == K_HVAC_IFEEL) {
    data[6] = (byte)0x08;
  } else if (hvacmode == K_HVAC_COOL) {
    data[6] = (byte)0x03;
  } else if (hvacmode == K_HVAC_DRY) {
    data[6] = (byte)0x02;
  } else if (hvacmode == K_HVAC_FAN) {
    data[6] = (byte)0x07;
  } else {
    return;
  }

  // Fan mode handling
  if (fanmode == K_FAN_ONE) {
    data[8] = data[8] | (byte)0x2;
  } else if (fanmode == K_FAN_TWO) {
    data[8] = data[8] | (byte)0x3;
  } else if (fanmode == K_FAN_THREE) {
    data[8] = data[8] | (byte)0x5;
  }

  // Vane mode handling
  if (vanemode == K_VANE_ONE) {
    data[8] = data[8] | (byte)0x8;
  } else if (vanemode == K_VANE_TWO) {
    data[8] = data[8] | (byte)0x10;
  } else if (vanemode == K_VANE_THREE) {
    data[8] = data[8] | (byte)0x18;
  } else if (vanemode == K_VANE_FOUR) {
    data[8] = data[8] | (byte)0x20;
  } else if (vanemode == K_VANE_FIVE) {
    data[8] = data[8] | (byte)0x28;
  } else if (vanemode == K_VANE_FLAP) {
    data[8] = data[8] | (byte)0x38;
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