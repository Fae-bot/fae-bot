#include <Servo.h>

Servo myservo;
const int OPEN = 16;
const int CLOSED = 60;

int pos = 65;

void setup() {
  myservo.attach(9);
  Serial.begin(57600);
}

void loop() {
    //Serial.println(pos);
    myservo.write(pos);    
    delay(15);                       
  if (Serial.available() > 0) {
    int value = Serial.parseInt();
    pos = value;
    while (Serial.available() > 0) {
      char c = Serial.read();
    }
    
  }
}

