#include <Stepper.h>

#define EnablePin 8
#define Null 0
#define True 1
#define False -1

class ManagedStepper
{

    
    int _dirPin, _stepPin;

    short _stepsPerSecond = 0;
    
    
    unsigned long _startTime = 0;
    unsigned long _lastStepTime = 0;
    bool _HIGHorLOW = true;
    short _clockwise = True;
    
    short _forbiddenDir = Null;
    
    public: 
        int _microSwitchPin;
        bool _state = false;
        
        long _stepedSteps = 0;
        
        ManagedStepper(int dirP, int stepP, int microSwitchP) {

            _microSwitchPin = microSwitchP;
            _dirPin = dirP;
            _stepPin = stepP;
            
            pinMode(_microSwitchPin, INPUT_PULLUP);
            pinMode(_dirPin, OUTPUT);
            pinMode(_stepPin, OUTPUT);
        }

        void setSpeed(short stepsPerSecond)
        {
          if (_forbiddenDir == sign(stepsPerSecond)) return;
          digitalWrite(_dirPin, sign(sign(stepsPerSecond) + 1));
          _stepsPerSecond  = stepsPerSecond;
          _startTime = millis();
        }

        short getSpeed()
        {
          return _stepsPerSecond;
        }
        
        virtual void update()
        {
          unsigned long currentStepTime = millis();
          if (currentStepTime - _lastStepTime <= 1) return;
          if (abs(short((currentStepTime - _startTime) * _stepsPerSecond / 1000 - _stepedSteps)) <= 0) return;

          // Heandle Micro Switch
          _state = digitalRead(_microSwitchPin);
          if (_state)
          {
            _forbiddenDir = sign(_stepsPerSecond);
            setSpeed(0);
          }
          else
          {
            _forbiddenDir = Null;
          }
          
          _stepedSteps += _HIGHorLOW * sign(_stepsPerSecond);
          digitalWrite(_stepPin, _HIGHorLOW);
          _HIGHorLOW = !_HIGHorLOW;
          _lastStepTime = currentStepTime;
        }

        static void Enable(bool mode)
        {
          if (mode) digitalWrite(EnablePin, HIGH);
          else digitalWrite(EnablePin, LOW);
        }

        static inline int8_t sign(int val) 
        {
          if (val < 0) return -1;
          if (val == 0) return 0;
          return 1;
        }
};
