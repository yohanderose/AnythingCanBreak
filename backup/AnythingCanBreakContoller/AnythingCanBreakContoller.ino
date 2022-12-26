#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>
#include <BleKeyboard.h>

BleKeyboard bleKeyboard;
//int activeNumber = 0;
int noiseThreshold = 5;
int activeRange = 70;
bool speaker1 = false;
bool speaker2 = false;
bool speaker3 = false;
bool speaker4 = false;
bool speaker5 = false;
bool speaker6 = false;
bool speaker7 = false;
bool speaker8 = false;
bool speaker9 = false;
bool speaker10 = false;
bool speaker11 = false;
bool speaker12 = false;
bool speaker13 = false;
bool speaker14 = false;
bool speaker15 = false;
bool speaker16 = false;
int speaker1count = 0;
int speaker2count = 0;
int speaker3count = 0;
int speaker4count = 0;
int speaker5count = 0;
int speaker6count = 0;
int speaker7count = 0;
int speaker8count = 0;
int speaker9count = 0;
int speaker10count = 0;
int speaker11count = 0;
int speaker12count = 0;
int speaker13count = 0;
int speaker14count = 0;
int speaker15count = 0;
int speaker16count = 0;

typedef struct message {
  int sensorID;
  long range;
};
 
struct message myMessage;
 
void onDataReceiver(const uint8_t * mac, const uint8_t *incomingData, int len) {
  // We don't use mac to verify the sender
  // Let us transform the incomingData into our message structure
 memcpy(&myMessage, incomingData, sizeof(myMessage));
  //Serial.println("=== Data ===");
  //Serial.print("Mac address: ");
 //for (int i = 0; i < 6; i++) {
   //   Serial.print("0x");
     // Serial.print(mac[i], HEX);
      //Serial.print(":");
 //}
 //if (myMessage.sensorID == 11){
 //Serial.print("\nSensorID: ");
 //Serial.println(myMessage.sensorID);
 //Serial.print("range: ");
 //Serial.println(myMessage.range);
 //}
 
 // Serial.println();
 // 
  if (myMessage.sensorID == 1){
     if (myMessage.range < activeRange && speaker1 == false) {
          Serial.print("Speaker 1 count");
          Serial.println(speaker1count);
          speaker1count=speaker1count+1;
          if(speaker1count == noiseThreshold){
            bleKeyboard.press('1');
            delay(100);
            bleKeyboard.releaseAll();
            speaker1 = true;
            Serial.print("Speaker 1 on");
            Serial.println(myMessage.range);
            speaker1count=0;
          }
        } else if (myMessage.range >= activeRange && speaker1 == true) {
          speaker1count=speaker1count+1;
          Serial.print("Speaker 1 count");
          Serial.println(speaker1count);
          if(speaker1count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('1');
            delay(100);
            bleKeyboard.releaseAll();
            speaker1 = false;
            speaker1count=0;
            Serial.print("Speaker 1 off");
            Serial.println(myMessage.range);
          }
       }
  }
//
  if (myMessage.sensorID == 2){
     if (myMessage.range < activeRange && speaker2 == false) {
          Serial.print("Speaker 2 count");
          Serial.println(speaker2count);
          speaker2count=speaker2count+1;
          if(speaker2count == noiseThreshold){
            bleKeyboard.press('2');
            delay(100);
            bleKeyboard.releaseAll();
            speaker2 = true;
            Serial.print("Speaker 2 on");
            Serial.println(myMessage.range);
            speaker2count=0;
          }
        } else if (myMessage.range >= activeRange && speaker2 == true) {
          speaker2count=speaker2count+1;
          Serial.print("Speaker 2 count");
          Serial.println(speaker2count);
          if(speaker2count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('2');
            delay(100);
            bleKeyboard.releaseAll();
            speaker2 = false;
            speaker2count=0;
            Serial.print("Speaker 2 off");
            Serial.println(myMessage.range);
          }
       }
  }
  //
  if (myMessage.sensorID == 3){
     if (myMessage.range < activeRange && speaker3 == false) {
          Serial.print("Speaker 3 count");
          Serial.println(speaker3count);
          speaker3count=speaker3count+1;
          if(speaker3count == noiseThreshold){
            bleKeyboard.press('3');
            delay(100);
            bleKeyboard.releaseAll();
            speaker3 = true;
            Serial.print("Speaker 3 on");
            Serial.println(myMessage.range);
            speaker3count=0;
          }
        } else if (myMessage.range >= activeRange && speaker3 == true) {
          speaker3count=speaker3count+1;
          Serial.print("Speaker 3 count");
          Serial.println(speaker3count);
          if(speaker3count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('3');
            delay(100);
            bleKeyboard.releaseAll();
            speaker3 = false;
            speaker3count=0;
            Serial.print("Speaker 3 off");
            Serial.println(myMessage.range);
          }
       }
  }
//
 if (myMessage.sensorID == 4){
     if (myMessage.range < activeRange && speaker4 == false) {
          Serial.print("Speaker 4 count");
          Serial.println(speaker4count);
          speaker4count=speaker4count+1;
          if(speaker4count == noiseThreshold){
            bleKeyboard.press('4');
            delay(100);
            bleKeyboard.releaseAll();
            speaker4 = true;
            Serial.print("Speaker 4 on");
            Serial.println(myMessage.range);
            speaker4count=0;
          }
        } else if (myMessage.range >= activeRange && speaker4 == true) {
          speaker4count=speaker4count+1;
          Serial.print("Speaker 4 count");
          Serial.println(speaker4count);
          if(speaker4count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('4');
            delay(100);
            bleKeyboard.releaseAll();
            speaker4 = false;
            speaker4count=0;
            Serial.print("Speaker 4 off");
            Serial.println(myMessage.range);
          }
       }
  }
//
//
 if (myMessage.sensorID == 5){
     if (myMessage.range < activeRange && speaker5 == false) {
          Serial.print("Speaker 5 count");
          Serial.println(speaker5count);
          speaker5count=speaker5count+1;
          if(speaker5count == noiseThreshold){
            bleKeyboard.press('5');
            delay(100);
            bleKeyboard.releaseAll();
            speaker5 = true;
            Serial.print("Speaker 5 on");
            Serial.println(myMessage.range);
            speaker5count=0;
          }
        } else if (myMessage.range >= activeRange && speaker5 == true) {
          speaker5count=speaker5count+1;
          Serial.print("Speaker 5 count");
          Serial.println(speaker5count);
          if(speaker5count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('5');
            delay(100);
            bleKeyboard.releaseAll();
            speaker5 = false;
            speaker5count=0;
            Serial.print("Speaker 5 off");
            Serial.println(myMessage.range);
          }
       }
  }
//
//
 if (myMessage.sensorID == 6){
     if (myMessage.range < activeRange && speaker6 == false) {
          Serial.print("Speaker 6 count");
          Serial.println(speaker6count);
          speaker6count=speaker6count+1;
          if(speaker6count == noiseThreshold){
            bleKeyboard.press('6');
            delay(100);
            bleKeyboard.releaseAll();
            speaker6 = true;
            Serial.print("Speaker 6 on");
            Serial.println(myMessage.range);
            speaker6count=0;
          }
        } else if (myMessage.range >= activeRange && speaker6 == true) {
          speaker6count=speaker6count+1;
          Serial.print("Speaker 6 count");
          Serial.println(speaker6count);
          if(speaker6count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('6');
            delay(100);
            bleKeyboard.releaseAll();
            speaker6 = false;
            speaker6count=0;
            Serial.print("Speaker 6 off");
            Serial.println(myMessage.range);
          }
       }
  }
//
 if (myMessage.sensorID == 7){
     if (myMessage.range < activeRange && speaker7 == false) {
          Serial.print("Speaker 7 count");
          Serial.println(speaker7count);
          speaker7count=speaker7count+1;
          if(speaker7count == noiseThreshold){
            bleKeyboard.press('7');
            delay(100);
            bleKeyboard.releaseAll();
            speaker7 = true;
            Serial.print("Speaker 7 on");
            Serial.println(myMessage.range);
            speaker7count=0;
          }
        } else if (myMessage.range >= activeRange && speaker7 == true) {
          speaker7count=speaker7count+1;
          Serial.print("Speaker 7 count");
          Serial.println(speaker7count);
          if(speaker7count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('7');
            delay(100);
            bleKeyboard.releaseAll();
            speaker7 = false;
            speaker7count=0;
            Serial.print("Speaker 7 off");
            Serial.println(myMessage.range);
          }
       }
  }
//
//
 if (myMessage.sensorID == 8){
     if (myMessage.range < activeRange && speaker8 == false) {
          Serial.print("Speaker 8 count");
          Serial.println(speaker8count);
          speaker8count=speaker8count+1;
          if(speaker8count == noiseThreshold){
            bleKeyboard.press('8');
            delay(100);
            bleKeyboard.releaseAll();
            speaker8 = true;
            Serial.print("Speaker 8 on");
            Serial.println(myMessage.range);
            speaker8count=0;
          }
        } else if (myMessage.range >= activeRange && speaker8 == true) {
          speaker8count=speaker8count+1;
          Serial.print("Speaker 8 count");
          Serial.println(speaker8count);
          if(speaker8count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('8');
            delay(100);
            bleKeyboard.releaseAll();
            speaker8 = false;
            speaker8count=0;
            Serial.print("Speaker 8 off");
            Serial.println(myMessage.range);
          }
       }
  }
//
 if (myMessage.sensorID == 9){
     if (myMessage.range < activeRange && speaker9 == false) {
          Serial.print("Speaker 9 count");
          Serial.println(speaker9count);
          speaker9count=speaker9count+1;
          if(speaker9count == noiseThreshold){
            bleKeyboard.press('9');
            delay(100);
            bleKeyboard.releaseAll();
            speaker9 = true;
            Serial.print("Speaker 9 on");
            Serial.println(myMessage.range);
            speaker9count=0;
          }
        } else if (myMessage.range >= activeRange && speaker9 == true) {
          speaker9count=speaker9count+1;
          Serial.print("Speaker 9 count");
          Serial.println(speaker9count);
          if(speaker9count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('9');
            delay(100);
            bleKeyboard.releaseAll();
            speaker9 = false;
            speaker9count=0;
            Serial.print("Speaker 9 off");
            Serial.println(myMessage.range);
          }
       }
  }
//
//
 if (myMessage.sensorID == 10){
     if (myMessage.range < activeRange && speaker10 == false) {
          Serial.print("Speaker 10 count");
          Serial.println(speaker10count);
          speaker10count=speaker10count+1;
          if(speaker10count == noiseThreshold){
            bleKeyboard.press('0');
            delay(100);
            bleKeyboard.releaseAll();
            speaker10 = true;
            Serial.print("Speaker 10 on");
            Serial.println(myMessage.range);
            speaker10count=0;
          }
        } else if (myMessage.range >= activeRange && speaker10 == true) {
          speaker10count=speaker10count+1;
          Serial.print("Speaker 10 count");
          Serial.println(speaker10count);
          if(speaker10count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('0');
            delay(100);
            bleKeyboard.releaseAll();
            speaker10 = false;
            speaker10count=0;
            Serial.print("Speaker 10 off");
            Serial.println(myMessage.range);
          }
       }
  }
//
//
 if (myMessage.sensorID == 11){
     if (myMessage.range < activeRange && speaker11 == false) {
          Serial.print("Speaker 11 count");
          Serial.println(speaker11count);
          speaker11count=speaker11count+1;
          if(speaker11count == noiseThreshold){
            bleKeyboard.press('q');
            delay(100);
            bleKeyboard.releaseAll();
            speaker11 = true;
            Serial.print("Speaker 11 on");
            Serial.println(myMessage.range);
            speaker11count=0;
          }
        } else if (myMessage.range >= activeRange && speaker11 == true) {
          speaker11count=speaker11count+1;
          Serial.print("Speaker 11 count");
          Serial.println(speaker11count);
          if(speaker11count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('q');
            delay(100);
            bleKeyboard.releaseAll();
            speaker11 = false;
            speaker11count=0;
            Serial.print("Speaker 11 off");
            Serial.println(myMessage.range);
          }
       }
  }
//
//
 if (myMessage.sensorID == 12){
     if (myMessage.range < activeRange && speaker12 == false) {
          Serial.print("Speaker 12 count");
          Serial.println(speaker12count);
          speaker12count=speaker12count+1;
          if(speaker12count == noiseThreshold){
            bleKeyboard.press('w');
            delay(100);
            bleKeyboard.releaseAll();
            speaker12 = true;
            Serial.print("Speaker 12 on");
            Serial.println(myMessage.range);
            speaker12count=0;
          }
        } else if (myMessage.range >= activeRange && speaker12 == true) {
          speaker12count=speaker12count+1;
          Serial.print("Speaker 12 count");
          Serial.println(speaker12count);
          if(speaker12count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('w');
            delay(100);
            bleKeyboard.releaseAll();
            speaker12 = false;
            speaker12count=0;
            Serial.print("Speaker 12 off");
            Serial.println(myMessage.range);
          }
       }
  }
//
//
 if (myMessage.sensorID == 13){
     if (myMessage.range < activeRange && speaker13 == false) {
          Serial.print("Speaker 13 count");
          Serial.println(speaker13count);
          speaker13count=speaker13count+1;
          if(speaker13count == noiseThreshold){
            bleKeyboard.press('e');
            delay(100);
            bleKeyboard.releaseAll();
            speaker13 = true;
            Serial.print("Speaker 13 on");
            Serial.println(myMessage.range);
            speaker13count=0;
          }
        } else if (myMessage.range >= activeRange && speaker13 == true) {
          speaker13count=speaker13count+1;
          Serial.print("Speaker 13 count");
          Serial.println(speaker13count);
          if(speaker13count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('e');
            delay(100);
            bleKeyboard.releaseAll();
            speaker13 = false;
            speaker13count=0;
            Serial.print("Speaker 13 off");
            Serial.println(myMessage.range);
          }
       }
  }
//
//
 if (myMessage.sensorID == 14){
     if (myMessage.range < activeRange && speaker14 == false) {
          Serial.print("Speaker 14 count");
          Serial.println(speaker14count);
          speaker14count=speaker14count+1;
          if(speaker14count == noiseThreshold){
            bleKeyboard.press('r');
            delay(100);
            bleKeyboard.releaseAll();
            speaker14 = true;
            Serial.print("Speaker 14 on");
            Serial.println(myMessage.range);
            speaker14count=0;
          }
        } else if (myMessage.range >= activeRange && speaker14 == true) {
          speaker14count=speaker14count+1;
          Serial.print("Speaker 14 count");
          Serial.println(speaker14count);
          if(speaker14count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('r');
            delay(100);
            bleKeyboard.releaseAll();
            speaker14 = false;
            speaker14count=0;
            Serial.print("Speaker 14 off");
            Serial.println(myMessage.range);
          }
       }
  }
//
//
 if (myMessage.sensorID == 15){
     if (myMessage.range < activeRange && speaker15 == false) {
          Serial.print("Speaker 15 count");
          Serial.println(speaker15count);
          speaker15count=speaker15count+1;
          if(speaker15count == noiseThreshold){
            bleKeyboard.press('t');
            delay(100);
            bleKeyboard.releaseAll();
            speaker15 = true;
            Serial.print("Speaker 15 on");
            Serial.println(myMessage.range);
            speaker15count=0;
          }
        } else if (myMessage.range >= activeRange && speaker15 == true) {
          speaker15count=speaker15count+1;
          Serial.print("Speaker 15 count");
          Serial.println(speaker15count);
          if(speaker15count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('t');
            delay(100);
            bleKeyboard.releaseAll();
            speaker15 = false;
            speaker15count=0;
            Serial.print("Speaker 15 off");
            Serial.println(myMessage.range);
          }
       }
  }
//
//
 if (myMessage.sensorID == 16){
     if (myMessage.range < activeRange && speaker16 == false) {
          Serial.print("Speaker 16 count");
          Serial.println(speaker16count);
          speaker16count=speaker16count+1;
          if(speaker16count == noiseThreshold){
            bleKeyboard.press('y');
            delay(100);
            bleKeyboard.releaseAll();
            speaker16 = true;
            Serial.print("Speaker 16 on");
            Serial.println(myMessage.range);
            speaker16count=0;
          }
        } else if (myMessage.range >= activeRange && speaker16 == true) {
          speaker16count=speaker16count+1;
          Serial.print("Speaker 16 count");
          Serial.println(speaker16count);
          if(speaker16count == noiseThreshold){
            bleKeyboard.press(KEY_LEFT_SHIFT);
            bleKeyboard.press('y');
            delay(100);
            bleKeyboard.releaseAll();
            speaker16 = false;
            speaker16count=0;
            Serial.print("Speaker 16 off");
            Serial.println(myMessage.range);
          }
       }
  }
}
 
void setup() {
 Serial.begin(115200);
 WiFi.mode(WIFI_STA);
 // Get Mac Add
bleKeyboard.begin();
 
 // Initializing the ESP-NOW
 if (esp_now_init() != 0) {
   return;
 }
 esp_now_register_recv_cb(onDataReceiver);
}
 
void loop() {
}
