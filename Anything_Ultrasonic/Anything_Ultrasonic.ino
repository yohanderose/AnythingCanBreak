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

//The Arduino Wire library uses the 7-bit version of the address, so the code example uses 0x70 instead of the 8-bit 0xE0
#define SensorAddress byte(0x70)
//The sensors ranging command has a value of 0x51
#define RangeCommand byte(0x51)
//These are the two commands that need to be sent in sequence to change the sensor address
#define ChangeAddressCommand1 byte(0xAA)
#define ChangeAddressCommand2 byte(0xA5)

// Mac address of the slave
typedef struct message {
  int sensorID;
  long range;
  int motion;
};

int DEVICE_ID = 16;
int MOTION_SENSOR_PIN = 2;

struct message myMessage;
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
  pinMode(MOTION_SENSOR_PIN, INPUT);
  myMessage.sensorID = DEVICE_ID;
  myMessage.motion = LOW;
  myMessage.range = 0;

  WiFi.mode(WIFI_STA);

  Serial.begin(115200);  //Open serial connection at 115200 baud
  while (!Serial) {
    ;  // wait for serial port to connect. Needed for native USB port only
  }

  connectToWiFi();

  Wire.begin();
  changeAddress(SensorAddress, 0x40, 0);

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
  takeRangeReading();                  //Tell the sensor to perform a ranging cycle
  delay(1000);                         //Wait for sensor to finish
  myMessage.range = requestRange();    //Get the range from the sensor
  myMessage.motion = requestMotion();  // Get the motion from the sensor


  if (status == WL_CONNECTED) {
    sendToMaster();
  }

  /* Serial.println(range); */
  //analogWrite(9, (262.2857-0.3643*range));
  // changeAddress(0x70,0x20,0);

  // Serial.println("Send a new message");
  /* esp_now_send(NULL, (uint8_t *) &myMessage, sizeof(myMessage)); */
  delay(150);
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

  // Test http request to server
  /* while (1) { */
  /*   Serial.print("Starting connection to server..."); */
  /*   // if you get a connection, report back via serial: */
  /*   if (client.connect(HOST_NAME, 80)) { */
  /*     Serial.println("connected to server"); */
  /*     // Make a HTTP request: */
  /*     client.println("GET / HTTP/1.1"); */
  /*     client.println("Host: " + String(HOST_NAME)); */
  /*     client.println("Connection: close"); */
  /*     client.println(); */
  /*     break; */
  /*   } else { */
  /*     // if you didn't get a connection to the server: */
  /*     Serial.println("connection failed"); */
  /*   } */
  /*   // give the web browser time to receive the data */
  /*   delay(5000); */
  /* } */

  return 0;
}


int sendToMaster() {
  Serial.print("ID: ");
  Serial.println(myMessage.sensorID);
  Serial.print("Range: ");
  Serial.println(myMessage.range);

  String dataStr = "sensorID=" + String(myMessage.sensorID) + "&range=" + String(myMessage.range) + "&motion="  + String(myMessage.motion) ;
  String url = "/data?" + dataStr;
  Serial.println(url);

  Serial.print("Starting data transmission ... ");
  int port = 5000;
  HTTPClient http;
  http.begin(client, HOST_NAME, port, url, true);
  delay(500);
  int httpCode = http.GET();

  /* http.addHeader("Content-Type", "application/json"); */
  /* const size_t capacity = JSON_OBJECT_SIZE(2) + 60; */
  /* DynamicJsonDocument doc(capacity); */
  /* doc["sensorID"] = myMessage.sensorID; */
  /* doc["range"] = myMessage.range; */
  /* String serialized; */
  /* serializeJson(doc, serialized); */

  /* int httpCode = http.POST(serialized);   //Send the request */
  String payload = http.getString();  //Get the response payload

  Serial.println(httpCode);
  Serial.println(payload);

  return 0;
}

int requestMotion() {
  int state;
  int val = digitalRead(MOTION_SENSOR_PIN);  // read sensor value
  if (val == HIGH) {                         // check if the sensor is HIGH
    digitalWrite(LED_BUILTIN, HIGH);         // turn LED ON
    delay(500);                              // delay 100 milliseconds

    if (state == LOW) {
      Serial.println("Motion detected!");
      state = HIGH;  // update variable state to HIGH
    }
  } else {
    digitalWrite(LED_BUILTIN, LOW);  // turn LED OFF
    delay(500);                      // delay 200 milliseconds

    if (state == HIGH) {
      Serial.println("Motion stopped!");
      state = LOW;  // update variable state to LOW
    }
  }
  return state;
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

