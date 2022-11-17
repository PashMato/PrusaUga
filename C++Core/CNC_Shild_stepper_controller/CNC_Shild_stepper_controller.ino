#include "ManagedStepper.h"

int speed = 40;
ManagedStepper stepperX(2, 5, 9);
ManagedStepper stepperY(3, 6, 10);
void setup() { 


  Serial.begin(1000000);
 stepperX.setSpeed(1500);
 stepperY.setSpeed(1500);
 ManagedStepper::Enable(true);
  attachInterrupt(digitalPinToInterrupt(9), HeandleMicroSwitchX, CHANGE);
}

void loop() {
 stepperX.update(); 
 stepperY.update(); 
 delay(1);
}

void HeandleMicroSwitchX()
{
  stepperX._state = !stepperX._state;
  Serial.println(stepperX._state);
}
