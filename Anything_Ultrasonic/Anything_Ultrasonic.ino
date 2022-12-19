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
#include <espnow.h>


// RNGFND1_TYPE = 2 for I2C
/* #define RNGFND1_TYPE 2 */
/* #define RNGFND1_ADDR GYUS42_ADDRESS */
/* #define RNGFND1_SCALING 12.12 */
/* #define RNGFND1_MIN_CM 20 */
/* #define RNGFND1_MAX_CM 500 */
#define ChangeAddressCommand1 byte(0xAA)
#define ChangeAddressCommand2 byte(0xA5)

// Mac address of the slave
typedef struct Message {
  int sensorID = 0;
  long range = 0;
  int motion = 0;
};


const int deviceID = 16;
const bool transmitData = false;
const uint8_t motionSensorPin = D2;
Message myMessage;

WiFiClient client;
char ssid[] = "yohan_phone";       // your network SSID (name)
char pass[] = "testing123";        // your network password
char HOST_NAME[] = "172.20.10.5";  // hostname of web server:
int status = WL_IDLE_STATUS;       // the Wifi radio's status

void onSent(uint8_t *mac_addr, uint8_t sendStatus) {
  // Serial.println("Status:");
  // Serial.println(sendStatus);
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(motionSensorPin, INPUT);

  Serial.begin(115200);  //Open serial connection at 115200 baud

  while (!Serial) {
    ;  // wait for serial port to connect. Needed for native USB port only
  }
  Wire.begin();
  /* changeAddress(GYUS42_ADDRESS, 0x40, 0); */

  if (transmitData) {
    WiFi.mode(WIFI_STA);
    connectToWiFi();
  }
}

void loop() {

  myMessage.motion = digitalRead(motionSensorPin);
  Serial.println(myMessage.motion);
  delay(100);

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

void requestMotion() {
  int val = digitalRead(motionSensorPin);  // read sensor value
  if (val == HIGH) {                       // check if the sensor is HIGH
    digitalWrite(LED_BUILTIN, HIGH);       // turn LED ON
    delay(500);                            // delay 100 milliseconds

    if (myMessage.motion == LOW) {
      Serial.println("Motion detected!");
      myMessage.motion = HIGH;  // update variable myMessage.motion to HIGH
    }
  } else {
    digitalWrite(LED_BUILTIN, LOW);  // turn LED OFF
    delay(500);                      // delay 200 milliseconds

    if (myMessage.motion == HIGH) {
      Serial.println("Motion stopped!");
      myMessage.motion = LOW;  // update variable myMessage.motion to LOW
    }
  }
  Serial.print("Motion: ");
  Serial.println(myMessage.motion);
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
