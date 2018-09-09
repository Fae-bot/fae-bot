#include <wiringPi.h>
#include <stdlib.h>
#include <stdio.h>

const int ENA=11;
const int DIR=13;
const int PUL=3;

int main(int argc, char** argv){
		
	wiringPiSetup();
	pinMode(ENA, OUTPUT);
	pinMode(DIR, OUTPUT);
	pinMode(PUL, OUTPUT);

    digitalWrite(ENA,HIGH);


  for (int i=0; i<6400; i++)    //Forward 5000 steps
  {
    digitalWrite(DIR,LOW);
    digitalWrite(PUL,HIGH);
    delayMicroseconds(500);
    digitalWrite(PUL,LOW);
    delayMicroseconds(500);
  }
  for (int i=0; i<6400; i++)   //Backward 5000 steps
  {
    digitalWrite(DIR,HIGH);
    digitalWrite(PUL,HIGH);
    delayMicroseconds(500);
    digitalWrite(PUL,LOW);
    delayMicroseconds(500);
  }
}
