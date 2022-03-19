#include <IRremote.h>

// References:
// http://blog.mrossi.com/2016/05/toshiba-air-conditioner-ir-signal.html
// All bytes are MSB

#define K_KHZ 38
#define K_HEADER_MARK 4400
#define K_HEADER_SPACE 4350
#define K_BIT_MARK 560
#define K_ONE_SPACE 1600
#define K_ZERO_SPACE 520
#define K_FOOTER_MARK 560
#define K_FOOTER_SPACE 7450

#define EMIT_PIN D1
 
#define MODE_AUTO 0
#define MODE_COOL 1
#define MODE_DRY 2
#define MODE_FAN 3

#define FAN_AUTO 0
#define FAN_1 1
#define FAN_2 2
#define FAN_3 3
#define FAN_4 4
#define FAN_5 5

#define SWING_NO_OP 0
#define SWING_ON 1
#define SWING_OFF 2

#define OPERATION_NO_OP 0
#define OPERATION_HI_POWER 1
#define OPERATION_ECO 2

void setupSender() {
  pinMode(EMIT_PIN, OUTPUT);  
  IrSender.begin(EMIT_PIN, 0, 0);    
}

int sendCommand(
  bool off,
  bool fix,
  byte temp,
  byte mode_, 
  byte fan, 
  byte swing,
  byte operation
) {

  // adjust louver to set airflow direction.
  if (fix) {
    byte data[7] = {0xF2, 0x0D, 0x01, 0xFE, 0x21, 0x00, 0x21};    
    sendBytes(data, 7, false);
    return 0;
  }

  if (swing != SWING_NO_OP) {
    int size_data = 7;
    byte data[7] = {0xF2, 0x0D, 0x01, 0xFE, 0x21, 0x00, 0x00};   
    
    switch(swing){
      case SWING_ON:   data[5] |= (byte) B00000001; break;
      case SWING_OFF:  data[5] |= (byte) B00000010; break;
      default: return -1; break;
    }
    
    // CRC is a simple bits addition
    for (int i = 0; i < size_data - 1; i++) {
      data[size_data-1] = (byte) data[i] ^ data[size_data-1];
    }
        
    sendBytes(data, size_data, true);
    return 0;
  }

//  // still buggy
//  if (operation != OPERATION_NO_OP) {
//    int size_data = 10;
//    byte data[10] = {0xF2, 0x0D, 0x04, 0xFB, 0x09, 0xD0, 0x00, 0x00, 0x00, 0x00};   
//
//    switch(operation){
//      case OPERATION_HI_POWER:   data[8] |= (byte) B00000001; break;
//      case OPERATION_ECO:        data[8] |= (byte) B00000011; break;
//      default: return; break;
//    }
//
//    // CRC
//    for (int i = 0; i < size_data - 1; i++) {
//      data[size_data-1] = (byte) data[i] ^ data[size_data-1];
//    }
//        
//    sendBytes(data, size_data, true);
//    return;
//  }

  int size_data = 9;
  byte data[9] = {0xF2, 0x0D, 0x03, 0xFC, 0x01, 0x00, 0x00, 0x00, 0x00};

  // temp
  byte t_temp = (temp - 17) % (30 - 17 + 1);
  data[5] |= (t_temp - 17) << 4;

  // fan
  byte t_fan = fan;  
  t_fan = t_fan % (5 + 1);
  if (fan != FAN_AUTO) {
    t_fan = (t_fan + 1);
  }
  data[6] |= t_fan << 5;

  // mode
  switch(mode_){
    case MODE_AUTO:   data[6] |= (byte) B00000000; break;
    case MODE_COOL:   data[6] |= (byte) B00000001; break;
    case MODE_DRY:    data[6] |= (byte) B00000010; break;
    case MODE_FAN:    data[6] |= (byte) B00000100; break;
    default: return -1; break;
  }

  // off
  if (off) {
    data[6] |= (byte) B00000111;
  }
  
  // CRC
  for (int i = 0; i < size_data - 1; i++) {
    data[size_data-1] = (byte) data[i] ^ data[size_data-1];
  }
        
  sendBytes(data, size_data, true);
  return 0;
}

void sendBytes(byte data[], int size_data, bool sendTwice) {
  IrSender.enableIROut(K_KHZ);

  for (int k = 0; k < 1 + sendTwice; k++) {
    IrSender.mark(K_HEADER_MARK);
    IrSender.space(K_HEADER_SPACE);

    for (int i = 0; i < size_data; i++) {
      for (byte j = (1<<7); j > 0; j >>= 1) {
        IrSender.mark(K_BIT_MARK);
        if ((data[i] & j) > 0) {
          IrSender.space(K_ONE_SPACE);
        } else {
          IrSender.space(K_ZERO_SPACE);
        }
      }
    }
            
    IrSender.mark(K_FOOTER_MARK);
    IrSender.space(K_FOOTER_SPACE);
  }
}
