#include "defs.h"

#define NULL 0
#define True 1
#define False -1

static long RealTime = 0;
char msg[50];

class ManagedStepper
{
  
  private:
    
    const char *_name;
    
    unsigned int* _pTimeArray;
    unsigned int _timeArrayLen;
    short* _pPosArray;
    unsigned int _posArrayLen;

    unsigned long _lastTimeCommmand = 0;
    unsigned int _commandPointer = 0;
     
    bool shouldRun = false;

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
    
    int _position = 1000; // Current position
    int _pos0 = 1000; // Start of current section
    int _posF = 1000; // End of current section
    unsigned long _time0 = 0; // Start of current section
    unsigned long _timeF = 0; // End of current section
    unsigned long turnOffTime = 0; // when the step pin should turn off

    int maxPos = 1;

    void setup(int dirP, int stepP, int microSwitchPin0, int microSwitchPin1, const char *name) {
        _name = name;
        _microSwitchPin0 = microSwitchPin0;
        _microSwitchPin1 = microSwitchPin1;
        _dirPin = dirP;
        _stepPin = stepP;
        
        pinMode(_microSwitchPin0, INPUT_PULLUP);
        pinMode(_microSwitchPin1, INPUT_PULLUP);

        pinMode(_dirPin, OUTPUT);
        pinMode(_stepPin, OUTPUT);

        _lastCommandTime = RealTime;
    }

  public:
    ManagedStepper(int dirP, int stepP, int microSwitchPin0, int microSwitchPin1, const char *name=NULL) {
      setup(dirP, stepP, microSwitchPin0, microSwitchPin1, name);
    }

    ManagedStepper(short* pPosArray, unsigned int posArrayLen, unsigned int* pTimeArray, unsigned int timeArrayLen,
                            int dirP, int stepP, int microSwitchPin0, int microSwitchPin1, const char *name=NULL) {
      setup(dirP, stepP, microSwitchPin0, microSwitchPin1, name);
      
      if (timeArrayLen != posArrayLen) {
        sprintf(msg, "timeArray length (%i) doesn't match posArray length (%i)", timeArrayLen, posArrayLen);
        Serial.println(msg);
        return;
      }
      _pPosArray = pPosArray;
      _posArrayLen = posArrayLen;

      _pTimeArray = pTimeArray;
      _timeArrayLen = timeArrayLen;
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

    // void oneWayCalibration(int size) // calibrate the stepper which has only one micro switch (get a given size)
    // {
    //   calibretingSate = CalibretionState::findSize; // the next phase is to get to the stating point 
    //   maxPos = size;
    //   goTo(-1000000, 2000000);
    // }
    
    void start() {
      Serial.print("Statring Stepper ");
      Serial.println(_name);
      shouldRun = true;
      _commandPointer = 0;
    }
    
    void continueWorking() {
      Serial.print("Stepper Continue Working");
      Serial.println(_name);
      shouldRun = true;
    }

    void stop() {
      shouldRun = false;
      Serial.print("Stopping Stepper ");
      Serial.println(_name);
    }

    bool isRunning() {
      return shouldRun;
    }

    unsigned long getSize() {return _size;}

    void setPosition(int newPos)
    {
      _position = newPos;
      _posF = newPos;
      _timeF = millis();
    }
    void goTo(int targetPosition, unsigned long targetTime) // makes the stepper move to a point in a certain time
    {
      _pos0 = _position;
      _time0 = RealTime;
      _posF = targetPosition;
      _timeF = RealTime + targetTime;
    }

    bool isDone() {return _timeF <= millis();}
    
    static void Update() {
      RealTime = millis();
    }

    void update()
    {
      if (_executingCommand) {
        digitalWrite(_stepPin, LOW);
        _executingCommand = false;  
      }
      else {
        unsigned long RealTime = millis();
        if ((_timeF > _time0) && (_timeF > RealTime)) {
          float slope = (float)(_posF - _pos0) / (float)(_timeF - _time0);
          int optPose = (int)(((float) _pos0) + ((float) (RealTime - _time0)) * slope + 0.5);
  
          int deltaPos = optPose - _position;
          int minToMove = 1;
          int toMove = sign(deltaPos / minToMove);
  
          if ((toMove < 0) && (switchPressed(false))) {
            toMove = 0;
          }
          if ((toMove > 0) && (switchPressed(true))) {
            toMove = 0;
          }
  
          if (toMove != 0) {
            digitalWrite(_stepPin, HIGH);
            digitalWrite(_dirPin, toMove > 0 ? HIGH : LOW);
            _position += sign(toMove);
            turnOffTime = (int)((float)(_position - _pos0) + (float)_time0 * slope + 0.5) / (2 * slope);
            _executingCommand = true;
          }
        }
      }

      if (shouldRun && _commandPointer < _timeArrayLen)
      {
        if (isDone()) {
          goTo(_pPosArray[_commandPointer], _pTimeArray[_commandPointer]);
          sprintf(msg, "exe commend (%d) [%d, %d]", _commandPointer, _pPosArray[_commandPointer], _pTimeArray[_commandPointer]);
          Serial.println(msg);
          _commandPointer++;
          
          if (_commandPointer >= _timeArrayLen && _commandPointer >= _posArrayLen)
          {
            stop();
            Serial.println("Done");
            _commandPointer = 0;
          }
        }
      } 
    }

    static void enable(bool isEnabled)
    {
      pinMode(ENABLE_PIN, OUTPUT);
      digitalWrite(ENABLE_PIN, !isEnabled ? HIGH : LOW);
    }

    static inline int sign(int val) {
      return val < 0 ? -1 : (val > 0 ? 1 : 0);
    }
};
