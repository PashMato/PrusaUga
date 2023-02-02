#include "defs.h"

#if PLATFORM == ESP32
 #include <WiFi.h>
#elif PLATFORM == ESP8266
 #include <ESP8266WiFi.h>
#endif

#include <PubSubClient.h>
#include <Wire.h>

const char* _ssid;
const char* _password;
const char* _mqtt_server;

WiFiClient espClient;
PubSubClient* client = new PubSubClient(espClient);

#define KCODE_TOPIC "/prusa_uga/kcode"
#define DEBUG_TOPIC "prusa_uga/message"

struct KHeader {
    int numRows;
    int xMin, xMax;
    int yMin, yMax;
    KHeader() {
      reset();
    }
    void reset() {
      numRows = 0;
      xMin = xMax = 0;
      yMin = yMax = 0;
    }
};

class KCode {
  public:
    KHeader header;
    short* pX;
    short* pY;
    short* pZ;
    int* pTime;

    KCode() {
      reset();
    }
  
    ~KCode() {
      reset();
    }

    void reset() {
    header.reset();
    delete pX;
    delete pY;
    delete pZ;
    delete pTime;
    
    pX = NULL;
    pY = NULL;
    pZ = NULL;
    pTime = NULL;
  }

  void init(byte* message, unsigned int length) {
    char msg[200];
    sprintf(msg, "Init from %d bytes", length);
    Serial.println(msg);    
    reset();
    
    // Check we're good with the number of rows
    int numActualRows = (length - sizeof(KHeader)) / (sizeof(short) * 3 + sizeof(unsigned int));
    
    if (length <= sizeof(KHeader)) {
      Serial.println("KCode shorter than the header. Aborting!");
      return;
    }

    KHeader *pHead = (KHeader *) message;
    header = *pHead;

    if ((numActualRows <= 0) || (numActualRows != header.numRows)) {
      sprintf(msg, "Expected %d rows by header, got %d rows in payload. Aborting!", header.numRows, numActualRows);
      Serial.println(msg);
      return;
    }

    pX = new short[numActualRows];
    pY = new short[numActualRows];
    pZ = new short[numActualRows];
    pTime = new int[numActualRows];

    if (pX == NULL || pY == NULL || pZ == NULL || pTime == NULL) {
      sprintf(msg, "Could not allocate %d rows for KCode. Aborting!", numActualRows);
      Serial.println(msg);
      return;
    }

    memcpy(pX, message + sizeof(KHeader), header.numRows * sizeof(*pX));
    memcpy(pY, message + sizeof(KHeader) + sizeof(*pX) * header.numRows, header.numRows * sizeof(*pY));
    memcpy(pZ, message + sizeof(KHeader) + (sizeof(*pX) + sizeof(*pY)) * header.numRows, header.numRows * sizeof(*pZ));
    memcpy(pTime, message + sizeof(KHeader) + (sizeof(*pX) + sizeof(*pY) + sizeof(*pZ)) * header.numRows, header.numRows * sizeof(*pTime));
  }

  bool valid() {
    return pX != NULL && pY != NULL && pZ != NULL && pTime != NULL;
  }
  
  void print() {
    char msg[200];
    sprintf(msg, "KCode: %d rows, X:[%d, %d], Y:[%d, %d]", header.numRows, header.xMin, header.xMax, header.yMin, header.yMax);
    Serial.println(msg);
    for (int i = 0; i < header.numRows; i ++)
    {
      sprintf(msg, "%10d %10d %10d %10d", pX[i], pY[i], pZ[i], pTime[i]);
      Serial.println(msg);
    }    
  }
  
};

KCode theCode;


void callback(char* topic, byte* message, unsigned int length) {
  if (String(topic) == KCODE_TOPIC) {
    //Write into Kcode buffer
    theCode.init(message, length);
  }
  else if (String(topic) == DEBUG_TOPIC) {
    // print the massage
    for (int i = 0; i < length; i++) {
      Serial.print((char)message[i]);
    }
  }
}

bool send(const char topic[], const byte message[], unsigned int length) {
  // send the bytes
  return client->publish(topic, message, length);
}

bool send(const char topic[], const char message[]) {
  // send the string
  return client->publish(topic, message);
}

void networkSetup(const char* ssid, const char* password, const char* mqtt_server) {    
    _ssid = ssid;
    _password = password;
    _mqtt_server = mqtt_server;
    Serial.print("MQTT Server: ");
    Serial.print(mqtt_server);
    client->setServer(_mqtt_server, 1883);
    client->setCallback(callback);

    delay(100);
    // We start by connecting to a WiFi network
    Serial.print("\nConnecting to ");
    Serial.print(_ssid);

    WiFi.begin(_ssid, _password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected");
}

// void desetup() {
//     free(client);
    
//     delete(_ssid);
//     delete(_password);
//     delete(_mqtt_server);

//     free(KcodeBuffer);
//     free(KcodeWritePointer);
// }

void reconnect() {
  Serial.println("Attempting MQTT connection...");
  // Attempt to connect
  if (client->connect("PrusaUga")) {
    Serial.println("MQTT Connected");
    // Subscribe
    client->subscribe(KCODE_TOPIC);
//    client->subscribe(DEBUG_TOPIC);
  }
}

unsigned long _time = 0;

void clientUpdate() {
  if (millis() - _time > 1000) {
    _time = millis();
    if (!client->connected()) {
      reconnect();
      return;
    }
    
    client->loop();
  }
}
