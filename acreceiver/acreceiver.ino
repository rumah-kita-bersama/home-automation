// connect digital pin to pin2

int maximum = 500; 
unsigned int data[500], low[450], high[450]; 
unsigned int x = 0;
 
void setup() {
  Serial.begin(115200); 
  attachInterrupt(0, recInterrupt, CHANGE);
}

void loop() {
  Serial.println(F("Press the button once"));
  delay(5000);
  if (x) {
    Serial.println();
    Serial.print(F("Raw: ("));
    Serial.print((x - 1));
    Serial.print(F(") "));
    
    // stop interrupts and capture until finished here
    detachInterrupt(0);

    for (int i = 1, j = 0; i < x; i++, j++) {
      if (i%2 == 0) {
        low[j] = data[i] - data[i-1];
        if (data[i] - data[i-1] > 1000) {
          Serial.print("1");
        } else {
          Serial.print("0");
        }    
      } else {
        high[j] = (data[i] - data[i-1]);    
      }
    }
    x = 0;
    
    Serial.println();
    Serial.println();

    // re-enable ISR for receiving IR signal
    attachInterrupt(0, recInterrupt, CHANGE); 
  }
}

void recInterrupt() {
  // ignore if exceeds maximum
  if (x > maximum) {
    return;
  }

  // record
  data[x++] = micros();
}
