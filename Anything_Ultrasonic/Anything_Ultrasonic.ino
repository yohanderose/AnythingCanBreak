/*
PRO MINI-----------GYUS42
VCC ---------- 5V    VCC>5V 
GND  --------- GND   GND>GND
A5 -------- RC (SCL) CR>D3
A4 -------- TD (SDA) DT>D4
*/
#include "Wire.h"
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <SPI.h>


//The Arduino Wire library uses the 7-bit version of the address, so the code example uses 0x70 instead of the 8-bit 0xE0
#define SensorAddress byte(0x70)
//The sensors ranging command has a value of 0x51
#define RangeCommand byte(0x51)
//These are the two commands that need to be sent in sequence to change the sensor address
#define ChangeAddressCommand1 byte(0xAA)
#define ChangeAddressCommand2 byte(0xA5)

// Mac address of the slave
typedef struct Message {
  int sensorID = 0;
  long range = 0;
  int motion = 0;
};


const int deviceID = 1;
const bool transmitData = true;
const uint8_t motionSensorPin = D2;
Message myMessage;

WiFiClient client;
char ssid[] = "anythingcanbreaknet";       // your network SSID (name)
char pass[] = "48881722";        // your network password
char HOST_NAME[] = "192.168.0.101";  // hostname of web server:
int status = WL_IDLE_STATUS;       // the Wifi radio's status

void onSent(uint8_t *mac_addr, uint8_t sendStatus) {
  // Serial.println("Status:");
  // Serial.println(sendStatus);
}

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
  delay(100);
  requestMotion();
  requestRange();

  sendToMaster();

  delay(200);
}

int sendToMaster() {
  Serial.print("ID: ");
  Serial.println(myMessage.sensorID);
  Serial.print("Range: ");
  Serial.println(myMessage.range);
  Serial.print("Motion: ");
  Serial.println(myMessage.motion);

  if (status == WL_CONNECTED && transmitData) {

    String dataStr = "sensorID=" + String(myMessage.sensorID) + "&range=" + String(myMessage.range) + "&motion=" + String(myMessage.motion);
    String url = "/data?" + dataStr;
    Serial.println(url);

    Serial.print("Starting data transmission ... ");
    int port = 5000;
    HTTPClient http;
    http.begin(client, HOST_NAME, port, url, true);

    delay(500);
    int httpCode = http.GET();
    String payload = http.getString();  //Get the response payload

    Serial.println(httpCode);
    Serial.println(payload);
  }

  return 0;
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
int requestRange() {
  Wire.requestFrom(SensorAddress, byte(2));
  if (Wire.available() >= 2) {                           //Sensor responded with the two bytes
    int range_highbyte = Wire.read();                    //Read the high byte back
    int range_lowbyte = Wire.read();                     //Read the low byte back
    myMessage.range = (range_highbyte * 256) + range_lowbyte;  //Make a 16-bit word out of the two bytes for the range
    return 0;
  } else {
    return -1;
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
    // wait 10 seconds for connection:
    delay(10000);
  }

  // you're connected now, so print out the data:
  Serial.println("You're connected to the network");

  return 0;
}

