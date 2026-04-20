#ifdef ENABLE_REPLAY

char cmd[] = "111100100000110100000011111111000000000111000000010000000000000010000001";

void sendReplay() {
    int size_data = strlen(cmd) / 8;
    byte data[size_data];
    for (int i = 0, k = 0; k < size_data; k++){
      for (byte j = (1<<7); j > 0; j >>= 1, i++) {
        if (cmd[i] == '1') {
           data[k] = (data[k] | j);        
        } else {
           data[k] = (data[k] & ~j);
        }
      }
    }
    sendBytes(data, size_data, true);
}

#endif
