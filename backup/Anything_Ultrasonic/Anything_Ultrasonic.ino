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
/* #include <espnow.h> */

//The Arduino Wire library uses the 7-bit version of the address, so the code example uses 0x70 instead of the 8-bit 0xE0
#define SensorAddress byte(0x70)
//The sensors ranging command has a value of 0x51
#define RangeCommand byte(0x51)
//These are the two commands that need to be sent in sequence to change the sensor address
#define ChangeAddressCommand1 byte(0xAA)
#define ChangeAddressCommand2 byte(0xA5)

// Mac address of the slave
uint8_t peer1[] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };

typedef struct message {
  int sensorID;
  long range;
};

struct message myMessage;

void onSent(uint8_t *mac_addr, uint8_t sendStatus) {
  // Serial.println("Status:");
  // Serial.println(sendStatus);
}

void setup() {
  Serial.begin(115200);  //Open serial connection at 115200 baud

  Wire.begin();
  // changeAddress(SensorAddress,0x40,0);

  WiFi.mode(WIFI_STA);
  // Get Mac Add
  // Serial.print("Mac Address: ");
  // Serial.print(WiFi.macAddress());
  // Serial.println("ESP-Now Sender");
  // Initializing the ESP-NOW
  /* if (esp_now_init() != 0) { */
  /*   Serial.println("Problem during ESP-NOW init"); */
  /*   return; */
  /* } */
  /* esp_now_set_self_role(ESP_NOW_ROLE_CONTROLLER); */
  /* // Register the peer */
  /* //Serial.println("Registering a peer"); */
  /* esp_now_add_peer(peer1, ESP_NOW_ROLE_SLAVE, 1, NULL, 0); */
  /* //Serial.println("Registering send callback function"); */
  /* esp_now_register_send_cb(onSent); */
}

void loop() {
  takeRangeReading();          //Tell the sensor to perform a ranging cycle
  delay(100);                  //Wait for sensor to finish
  int range = requestRange();  //Get the range from the sensor

  myMessage.sensorID = 16;
  myMessage.range = range;

  Serial.print("Range: ");
  Serial.println(range);  //Print to the user

  //Serial.println(range);
  //analogWrite(9, (262.2857-0.3643*range));
  // changeAddress(0x70,0x20,0);

  // Serial.println("Send a new message");
  /* esp_now_send(NULL, (uint8_t *)&myMessage, sizeof(myMessage)); */
  delay(150);
}

//Commands the sensor to take a range reading
void takeRangeReading() {
  Wire.beginTransmission(SensorAddress);  //Start addressing
  Wire.write(RangeCommand);               //send range command
  Wire.endTransmission();                 //Stop and do something else now
}

//Returns the last range that the sensor determined in its last ranging cycle in centimeters. Returns 0 if there is no communication.
int requestRange() {
  Wire.requestFrom(SensorAddress, byte(2));
  if (Wire.available() >= 2) {                           //Sensor responded with the two bytes
    int range_highbyte = Wire.read();                    //Read the high byte back
    int range_lowbyte = Wire.read();                     //Read the low byte back
    int range = (range_highbyte * 256) + range_lowbyte;  //Make a 16-bit word out of the two bytes for the range
    return range;
  } else {
    return (0);  //Else nothing was received, return 0
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

