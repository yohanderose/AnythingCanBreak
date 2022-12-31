/*
	PRO MINI-----------GYUS42
	VCC ---------- 5V    VCC>5V 
	GND  --------- GND   GND>GND
	A5 -------- RC (SCL) CR>D3
	A4 -------- TD (SDA) DT>D4


	287377 bytes (27%) with delay
*/
#include "Wire.h"
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

//The Arduino Wire library uses the 7-bit version of the address, so the code example uses 0x70 instead of the 8-bit 0xE0
#define SensorAddress byte(0x70)
//The sensors ranging command has a value of 0x51
#define RangeCommand byte(0x51)
//These are the two commands that need to be sent in sequence to change the sensor address
#define ChangeAddressCommand1 byte(0xAA)
#define ChangeAddressCommand2 byte(0xA5)
#define APPROX_CEIL_HEIGHT 240    // cm
#define CONTIGUOUS_ALLOWANCE 100  // cm

struct Message {
  int sensorID = 0;
  long lastRange[3] = { APPROX_CEIL_HEIGHT, APPROX_CEIL_HEIGHT, APPROX_CEIL_HEIGHT };
  long range = 0;
  int motion = 0;
};

const int deviceID = 1;
const bool transmitData = true;
const uint8_t motionSensorPin = D2;
Message myMessage;

WiFiClient client;
char ssid[] = "anythingcanbreaknet";  // your network SSID (name)
char pass[] = "48881722";             // your network password
char HOST_NAME[] = "192.168.0.99";    // hostname of web server:
int status = WL_IDLE_STATUS;          // the Wifi radio's status

void onSent(uint8_t *mac_addr, uint8_t sendStatus) {
  // Serial.println("Status:");
  // Serial.println(sendStatus);
}

/* int main() { */
/*   pinMode(LED_BUILTIN, OUTPUT); */
/*   pinMode(motionSensorPin, INPUT); */
/*   myMessage.sensorID = deviceID; */
/*   Wire.begin(); */

/*   Serial.begin(115200);  //Open serial connection at 115200 baud */

/*   while (!Serial) { */
/*     ;  // wait for serial port to connect. Needed for native USB port only */
/*   } */

/*   if (transmitData) { */
/*     WiFi.mode(WIFI_STA); */
/*     connectToWiFi(); */
/*   } */

/*   while (true) { */
/* 	  initRangeRead(); */

/* 	  for (long i = 0; i < 50000; i++) { */
/* 		  asm(""); */
/* 	  } */
/* 	  /1* requestMotion(); *1/ */
/* 	  requestRange(); */

/* 	  // Smoothing filter to avoid echo interference ~5cm threshold */
/* 	  sendToMaster(); */
/*   } */
/* } */

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(motionSensorPin, INPUT);
  myMessage.sensorID = deviceID;
  Wire.begin();

  Serial.begin(115200);  //Open serial connection at 115200 baud

  while (!Serial) {
    ;  // wait for serial port to connect. Needed for native USB port only
  }

  if (transmitData) {
    WiFi.mode(WIFI_STA);
    connectToWiFi();
  }
}

void loop() {

  initRangeRead();
  delay(70);
  requestRange();
  /* requestMotion(); */

  sendToMaster();
}

void sendToMaster() {
  String dataStr = "sensorID=" + String(myMessage.sensorID) + "&range=" + String(myMessage.range) + "&motion=" + String(myMessage.motion);
  String url = "/data?" + dataStr;
  Serial.println(url);

  if (status == WL_CONNECTED && transmitData) {

    Serial.print("Starting data transmission ... ");
    int port = 5000;
    HTTPClient http;
    http.begin(client, HOST_NAME, port, url, true);

    int httpCode = http.GET();
    String payload = http.getString();  //Get the response payload

    Serial.println(httpCode);
    Serial.println(payload);
  }
}

int requestMotion() {
  int val = digitalRead(motionSensorPin);  // read sensor value

  if (val == HIGH) {                  // check if the sensor is HIGH
    digitalWrite(LED_BUILTIN, HIGH);  // turn LED ON
    if (myMessage.motion == LOW) {
      Serial.println("Motion detected!");
      myMessage.motion = HIGH;  // update variable myMessage.motion to HIGH
    }
    return 0;
  }

  digitalWrite(LED_BUILTIN, LOW);  // turn LED OFF
  if (myMessage.motion == HIGH) {
    Serial.println("Motion stopped!");
    myMessage.motion = LOW;  // update variable myMessage.motion to LOW
  }
  return 0;
}
//Commands the sensor to take a range reading
void initRangeRead() {
  Wire.beginTransmission(SensorAddress);  //Start addressing
  Wire.write(RangeCommand);               //send range command
  Wire.endTransmission();                 //Stop and do something else now
}

//Gets recently determined range in centimeters. Returns -1 if no communication.
void requestRange() {
  Wire.requestFrom(SensorAddress, byte(2));
  if (Wire.available() >= 2) {         //Sensor responded with the two bytes
    int range_highbyte = Wire.read();  //Read the high byte back
    int range_lowbyte = Wire.read();   //Read the low byte back
                                       // Update state
    myMessage.lastRange[0] = myMessage.lastRange[1];
    myMessage.lastRange[1] = myMessage.lastRange[2];
    myMessage.lastRange[2] = (range_highbyte * 256) + range_lowbyte;  //Make a 16-bit word out of the two bytes for the range

    myMessage.range = (abs(myMessage.lastRange[0] - myMessage.lastRange[1]) < CONTIGUOUS_ALLOWANCE && abs(myMessage.lastRange[1] - myMessage.lastRange[2]) < CONTIGUOUS_ALLOWANCE) ? myMessage.lastRange[2] : 0;
  }
}


/* Commands a sensor at oldAddress to change its address to newAddress
oldAddress must be the 7-bit form of the address that is used by Wire
7BitHuh determines whether newAddress is given as the new 7 bit version or the 8 bit version of the address
If true, if is the 7 bit version, if false, it is the 8 bit version
*/
void changeAddress(byte oldAddress, byte newAddress, boolean SevenBitHuh) {
  Wire.beginTransmission(oldAddress);  //Begin addressing
  Wire.write(ChangeAddressCommand1);   //Send first change address command
  Wire.write(ChangeAddressCommand2);   //Send second change address command
  byte temp;
  if (SevenBitHuh) { temp = newAddress << 1; }  //The new address must be written to the sensor
  else {
    temp = newAddress;
  }                  //in the 8bit form, so this handles automatic shifting
  Wire.write(temp);  //Send the new address to change to
  Wire.endTransmission();
}

int connectToWiFi() {

  // check for the presence of the shield:
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue:
    while (true)
      ;
  }

  // attempt to connect to Wifi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network:
    status = WiFi.begin(ssid, pass);
    delay(5000);
  }

  // you're connected now, so print out the data:
  Serial.println("You're connected to the network");

  return 0;
}

