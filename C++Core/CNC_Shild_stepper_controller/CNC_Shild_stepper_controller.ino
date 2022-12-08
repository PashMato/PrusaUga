#include "ManagedStepper.h"

#define XPIN A6
#define YPIN A7



//KcodeReader reader(_array, 2);
ManagedStepper stepperX(2, 5, 9, 9);
ManagedStepper stepperY(3, 6, 9, 9);

void setup() { 
  Serial.begin(1000000);
  ManagedStepper::enable(true);
  
//  stepper.calibration();
}
unsigned long last = 0;
bool fwd = true;

int ctr=0;

float alpha = 0;
float r = 1000;
float rate = 0.03 * 2 * PI;

unsigned long lastPrint = 0;
unsigned long lastUpdate= 0;

void loop() {
 unsigned long now = millis();
 alpha = (float) now / 1000. * rate;
 float x = r * cos(alpha);
 float y = r * sin(alpha);

if (lastUpdate - now > 500) {
   stepperX.goTo(x, now + 100);
   // stepperY.goTo(y, now + 400);
   lastUpdate = now;
}

 if (lastPrint - now > 100) {
  Serial.print(stepperX._pos0); //stepperX._position);
  Serial.print(",");
  Serial.print(stepperX._posF); //stepperX._position);  
  Serial.print(",1010,-1010,");
  Serial.println(stepperX._position); //stepperX._position);
  lastPrint = now;
 }

//  if (now > last + 2000) {
//    stepper.goTo(1000 + (fwd ? 50 : -50), now + 1500);
//    // stepper.goTo(900, now + 500);
//    last = now;
//    fwd = !fwd;
//    Serial.print(" _position: "); Serial.print(stepper._position);
//    Serial.print(" _pos0: "); Serial.print(stepper._pos0);
//    Serial.print(" _posF: "); Serial.print(stepper._posF);
//    Serial.print(" _time0: "); Serial.print(stepper._time0);
//    Serial.print(" _timeF: "); Serial.print(stepper._timeF);
//    Serial.print(" iters="); Serial.println(ctr);
//    ctr = 0;    
//  }
  
  
 stepperX.update();
 // stepperY.update();
  
 delay(2);
}
