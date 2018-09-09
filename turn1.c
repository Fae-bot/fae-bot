#include <wiringPi.h>
#include <stdlib.h>
#include <stdio.h>

const int ENA=11;
const int DIR=0;
const int PUL=2;

int main(int argc, char** argv){
	if(argc<2) return 0;
	
	int value = atoi(argv[1]);
	if(value==0) return 0;
		
	wiringPiSetup();
	pinMode(ENA, OUTPUT);
	pinMode(DIR, OUTPUT);
	pinMode(PUL, OUTPUT);

	digitalWrite(ENA,HIGH);

	if(value>0)
	{
		printf("Moving %d steps forward\n", value);
		digitalWrite(DIR,HIGH);
	}
	else
	{
		digitalWrite(DIR,LOW);
		printf("Moving %d steps backward\n", value);
	}


  for (int i=0; i<abs(value); i++)
  {
    digitalWrite(PUL,HIGH);
    delayMicroseconds(200);
    digitalWrite(PUL,LOW);
    delayMicroseconds(200);
  }

}
