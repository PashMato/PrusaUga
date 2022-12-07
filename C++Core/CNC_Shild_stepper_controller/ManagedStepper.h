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
    unsigned long _size = 0;
    bool _HIGHorLOW = true;
    
    short _forbiddenDir = Null;
    
    public: 
        int _microSwitchPin;
        bool _state = false;
        
        unsigned long _position = 0;
        unsigned long _target = 0;
        unsigned long _remaingTime = 0;

        ManagedStepper(int dirP, int stepP, int microSwitchP) {

            _microSwitchPin = microSwitchP;
            _dirPin = dirP;
            _stepPin = stepP;
            
            pinMode(_microSwitchPin, INPUT_PULLUP);
            pinMode(_dirPin, OUTPUT);
            pinMode(_stepPin, OUTPUT);
        }

        bool goTo(unsigned long target, unsigned long remaingTime) // makes the stepper move to a piont in a certenct time
        {
          _target = target;
          _remaingTime = remaingTime;
        }
        
        void setSpeed(short stepsPerSecond) // sets the speed os the stepper
        {
          if (_forbiddenDir == sign(stepsPerSecond) && _forbiddenDir) return;
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
          // Heandle Micro Switch
          _state = -digitalRead(_microSwitchPin) + 1;
          if (_state && _forbiddenDir == 0)
          {
            _forbiddenDir = sign(_stepsPerSecond);
            _position = sign(sign(_stepsPerSecond) + 1) * _size;
            _target = _position;
            _remaingTime = 0;
            setSpeed(0);
            return;
          }
          else
          {
            _forbiddenDir = Null;
            setSpeed(short((_target - _position) / _remaingTime));
          }

          unsigned long currentStepTime = millis();
          if (short((currentStepTime - _startTime) * _stepsPerSecond / 1000) == 0 || (_forbiddenDir != 0 && _forbiddenDir == sign(_stepsPerSecond))) return; 
          _position += _HIGHorLOW * sign(_stepsPerSecond);
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
