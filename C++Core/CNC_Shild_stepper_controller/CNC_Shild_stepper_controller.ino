#include "ManagedStepper.h"

#define XPIN A6
#define YPIN A7


int speed = 40;

short sx, sy;
long lastWriteTime;

ManagedStepper stepperX(2, 5, 9);
ManagedStepper stepperY(3, 6, 10);
void setup() { 
  Serial.begin(1000000);
  pinMode(XPIN, INPUT); 
  pinMode(XPIN, INPUT);
//  stepperX.setSpeed(1000);
//  stepperY.setSpeed(-1000);
 ManagedStepper::Enable(true);
 lastWriteTime = millis();
}

void loop() {

  if (millis() - lastWriteTime > 100)
  {
    sx = short((analogRead(XPIN) - 512) / 20) * 2;
    sy = short((analogRead(YPIN) - 512) / 20) * 2;

    Serial.print(sx);
    Serial.println(sy);
    
    stepperY.setSpeed(sy);
    stepperX.setSpeed(sx);
    
    
    lastWriteTime = millis();
  }
  
 stepperY.update(); 
 stepperX.update();
 delay(1);
}
