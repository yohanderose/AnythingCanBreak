#define GY_US42 0x70              //7-bit I2C address of the US-42 sensor
#define GY_US42_CMD 0x00          //Command register
#define GY_US42_DATA 0x02         //Data register
#define GY_US42_CMD_MEASURE 0x51  //Measure command
#define GY_US42_CMD_READ 0x52     //Read command
#define GY_US42_CMD_RESET 0x00    //Reset command

#include <Wire.h>


void setup() {
  Serial.begin(115200);
  Wire.begin(); //SDA, SCL
}

void loop() {

  Serial.print("Distance: ");
  Serial.print(getDistance1());
  Serial.println(" cm");

  delay(1000);
}

int getDistance1() {
  int distance = -1;

  Wire.beginTransmission(GY_US42);
  Wire.write(GY_US42_CMD);
  Wire.write(GY_US42_CMD_MEASURE);
  Wire.endTransmission();
  delay(100);
  Wire.beginTransmission(GY_US42);
  Wire.write(GY_US42_CMD);
  Wire.write(GY_US42_CMD_READ);
  Wire.endTransmission();
  delay(100);
  Wire.requestFrom(GY_US42, 2);
  if (Wire.available() == 2) {
    int distance = Wire.read();
    distance = distance << 8;
    distance += Wire.read();
  }
  return distance;
}

// Pulse mode
int getDistance2() {


}
