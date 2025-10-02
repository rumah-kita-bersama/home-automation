// read internal VCC
void readVoltage() {  
  float volts = ESP.getVcc();
  Serial.printf("The internal VCC reads %1.2f volts\n", volts / 1000);
}
