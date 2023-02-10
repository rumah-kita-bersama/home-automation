// connect 5v to cathode
// connect anode with 110 ohm to gnd
// between anode and resistor connect pin2
// ref: https://github.com/techiesms/IR-Remote-Parameters/blob/master/Protocol_Analyzer.ino#L6

int maximum = 500;
unsigned int data[500], low[450], high[450];
unsigned int x = 0;
int threshold = 1000; // threshold for 1 or 0 based on how long the low signal is

void setup() {
  Serial.begin(115200);
  attachInterrupt(digitalPinToInterrupt(2), recInterrupt, CHANGE);
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
    detachInterrupt(digitalPinToInterrupt(2));

    Serial.println();
    for (int i = 1, j = 0; i < 300; i++, j++) {
      if (i%2 == 0) {
        low[j] = data[i] - data[i-1];
//        if (data[i] - data[i-1] > threshold) {
//          Serial.print("1");
//        } else {
//          Serial.print("0");
//        }
        Serial.print("LOW ");
        Serial.println(data[i] - data[i - 1]);
      } else {
        high[j] = (data[i] - data[i-1]);
        Serial.print("HIGH ");
        Serial.println(data[i] - data[i - 1]);
      }
    }
    x = 0;

    Serial.println();
    Serial.println();

    // re-enable ISR for receiving IR signal
    attachInterrupt(digitalPinToInterrupt(2), recInterrupt, CHANGE);
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
