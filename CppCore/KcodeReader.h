// #include "ManagedStepper.h"

// #define DIR_PIN_X 2
// #define STEP_PIN_X 5
// #define MICRO_SWITCH_PIN_X 9

// #define DIR_PIN_Y 3
// #define STEP_PIN_Y 6
// #define MICRO_SWITCH_PIN_Y 10 

// #define DIR_PIN_HEAD 4
// #define STEP_PIN_HEAD 7
// #define MICRO_SWITCH_PIN_HEAD 11


// class KcodeReader {
// private:
//     /*
//     steppers
//     kcode
//     kcodePointer 
//      */

//     ManagedStepper* StepperX;
//     ManagedStepper* StepperY;
//     ManagedStepper* StepperHead;


//     unsigned int KcodePointer = 0;
//     float* Kcode; // an array
//     unsigned short KcodeLength; // the array length
    
//     unsigned long targer_x, targer_y, targer_head, time = 0;

// public:
//     unsigned short plotingSpeed = 100;
//     unsigned short HeadSpeed = 50;
//     unsigned long HeadLength = 200;

//     KcodeReader(float* _kcode, unsigned short length)
//     {
//         StepperX = new ManagedStepper(DIR_PIN_X, STEP_PIN_X, MICRO_SWITCH_PIN_X);
//         StepperY = new ManagedStepper(DIR_PIN_Y, STEP_PIN_Y, MICRO_SWITCH_PIN_Y);
//         StepperHead = new ManagedStepper(DIR_PIN_HEAD, STEP_PIN_HEAD, MICRO_SWITCH_PIN_HEAD);

//         StepperX->oneWayCalibration(200);
//         StepperY->oneWayCalibration(200);
//         StepperHead->oneWayCalibration(HeadLength);

//         ManagedStepper::Enable(true);

//         Kcode = _kcode;
//         KcodeLength = length;
//     }

//     ~KcodeReader()
//     {
//         free(StepperX);
//         free(StepperY);
//         free(StepperHead);
//         free(Kcode);
//     }

//     bool isDone()
//     {
//         return true;
//     }
    
//     bool DonePrinting()
//     {
//         return KcodePointer >= KcodeLength;
//     }

//     void update() // update
//     {
//         if (DonePrinting()) 
//         {
//             StepperX->setSpeed(-1000);
//             StepperX->setSpeed(-1000);
//             StepperHead->goTo(StepperHead->getSize(), 20);
//             return;
//         }

//         if (isDone() && StepperX->isDone() && StepperY->isDone() && StepperHead->isDone())
//         {
//             StepperX->goTo(targer_x, time);
//             StepperY->goTo(targer_y, time);
//             StepperHead->goTo(targer_head, time);

//             targer_x = Kcode[KcodePointer * 4 + 0];
//             targer_y = Kcode[KcodePointer * 4 + 1];
//             targer_head = Kcode[KcodePointer * 4 + 2] * float(HeadSpeed);
//             time = sign(Kcode[KcodePointer * 4 + 2]) * float(plotingSpeed) * 10 + millis();

//             KcodePointer++;
//         }

//         StepperX->update();
//         StepperY->update();
//         StepperHead->update();
//     }
        
//     static inline int8_t sign(int val) 
//     {
//         if (val < 0) return -1;
//         if (val == 0) return 0;
//         return 1;
//     }
    
// };
