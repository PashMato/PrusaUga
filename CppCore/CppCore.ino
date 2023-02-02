// https://lastminuteengineers.com/esp32-pinout-reference/

#include "defs.h"
#include "ManagedStepper.h"
#include "data.h"


ManagedStepper stepperX(X, LEN, T, LEN, X_DIR, X_STEP, X_BEG, X_END, "X");
ManagedStepper stepperY(Y, LEN, T, LEN, Y_DIR, Y_STEP, Y_BEG, Y_END, "Y");

const float r = 200;
const float rate = 0.05 * 2 * PI;

void setup() { 
   Serial.begin(115200);
   Serial.println("Starting");
   ManagedStepper::enable(false);
   delay(100);
   pinMode(LED_PIN, OUTPUT);
   ManagedStepper::enable(true);
   delay(3000);
   ManagedStepper::Update();
   stepperX.setPosition(X[0]);
   stepperY.setPosition(Y[0]);
   stepperX.start();
   stepperY.start();
 }

 unsigned long last = 0;

 unsigned long lastPrint = 0;
 unsigned long lastUpdate = 0;

 const unsigned long DT = 100;

void loop() {
  // unsigned long now = millis();
  // float alpha = (float) now / 1000. * rate;
  // float x = r * cos(alpha);
  // float y = r * sin(alpha);

  // if (now - lastUpdate > DT) {
  //    stepperX.goTo(x, now + DT);
  //    stepperY.goTo(y, now + DT);
  //    lastUpdate = now;
  // }
  
  ManagedStepper::Update();
  stepperX.update();
  stepperY.update();
  
  unsigned long now = millis();
  digitalWrite(LED_PIN, (now % 1000) > 500 ? HIGH : LOW);
  // Serial.println((now % 1000) > 500 ? HIGH : LOW);
 
  delay(1);
}

//#include "Network.h"
//
//void setup()
//{
//  delay(100);
//  Serial.begin(500000);
//  networkSetup("Shapira", "inbal123", "192.168.20.197");
//  delay(100);
//}
//
//void loop() 
//{
//  clientUpdate();
//  if (theCode.valid()) {
//    theCode.print();
//    delay(100);
//    theCode.reset();
//  }
//  delay(1);
//}
