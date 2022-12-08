#define ENABLE_PIN 8
#define NULL 0
#define True 1
#define False -1

class ManagedStepper
{
  private:  
  public:  
    int _dirPin, _stepPin;

    short _stepsPerSecond = 0;
    
    unsigned long _lastCommandTime = 0;
    unsigned long _lastStepTime = 0;
    unsigned long _size = 0;
    bool _executingCommand = true;
    
    short _forbiddenDir = NULL;

    unsigned short _calibrationState = 0;

    int _microSwitchPin0;
    int _microSwitchPin1;
    
    int _position = 1000; // Current position // TODO: Make int
    int _pos0 = 1000; // Start of current section
    int _posF = 1000; // End of current section
    unsigned long _time0 = 0; // Start of current section
    unsigned long _timeF = 0; // End of current section

  public:
    ManagedStepper(int dirP, int stepP, int microSwitchPin0, int microSwitchPin1) {
        _microSwitchPin0 = microSwitchPin0;
        _microSwitchPin1 = microSwitchPin1;
        _dirPin = dirP;
        _stepPin = stepP;
        
        pinMode(_microSwitchPin0, INPUT_PULLUP);
        pinMode(_microSwitchPin1, INPUT_PULLUP);

        pinMode(_dirPin, OUTPUT);
        pinMode(_stepPin, OUTPUT);
    }

    bool switchPressed(bool is_1) {
      return digitalRead(is_1 ? _microSwitchPin1 : _microSwitchPin0) == LOW;
    }

    // void calibrate() // calibrate the stepper size and position
    // {
    //   _calibrationState = _calibrationState % 4;
    //   if (_calibrationState == 1) {
    //     // Run backward, to hit micro switch 0 ("beginning")
    //     setSpeed(-1000);
    //   }
    //   if (_calibrationState == 2) setSpeed(1000);
    //   if (_calibrationState == 3) 
    //   {
    //     setSpeed(-1000);
    //     _size = _position;
    //   }
    //   _calibrationState++;
    // }

    // void oneWayCalibration(unsigned long size) // calibrate the stepper hich has only one microswitch (get a given size)
    // {
    //   if (_calibrationState == 0)
    //   {
    //     setSpeed(-1000);
    //     _size = size;
    //     _calibrationState = 4;
    //   }
    // }

    // unsigned long getSize() {return _size;}

    void goTo(int targetPosition, unsigned long targetTime)
    {  // makes the stepper move to a point in a certain time
      _pos0 = _position;
      _time0 = millis();
      _posF = targetPosition;
      _timeF = targetTime;
    }

    bool isDone() {return _timeF <= millis();}
    
    // void setSpeed(short stepsPerSecond) // sets the speed os the stepper
    // {
    //   bool goingFwd = stepsPerSecond > 0;
    //   if (switchPressed(goingFwd)) {
    //     return;
    //   }
    //   digitalWrite(_dirPin, goingFwd);
    //   _stepsPerSecond  = stepsPerSecond;
    //   _lastCommandTime = millis();
    // }

    // short getSpeed()
    // {
    //   return _stepsPerSecond;
    // }
    
    void update()
    {
      if (_executingCommand) {
        digitalWrite(_stepPin, LOW);
        _executingCommand = false;
      } else {
        unsigned long now = millis();
        if ((_timeF > _time0) && (_timeF > now)) {
          float slope = (float)(_posF - _pos0) / (float)(_timeF - _time0);
          float optPoseF = (float) _pos0 + (float) (now - _time0) * slope;
          int optPose = (int) (optPoseF + 0.5);

          int deltaPos = optPose - _position;
          int minToMove = 1;
          int toMove = sign(deltaPos / minToMove);

          if ((toMove > 0) && (switchPressed(true)) ||
              ((toMove < 0) && (switchPressed(false)))) {
                toMove = 0;
          }

          if (toMove) {
            digitalWrite(_stepPin, HIGH);
            digitalWrite(_dirPin, toMove > 0 ? HIGH : LOW);
            _position += sign(toMove);
            _executingCommand = true;
          }
        }
      }      
    }

    static void enable(bool isEnabled)
    {
      digitalWrite(ENABLE_PIN, isEnabled ? HIGH : LOW);
    }

    static inline int sign(int val) {
      return val < 0 ? -1 : (val > 0 ? 1 : 0);
    }
};
