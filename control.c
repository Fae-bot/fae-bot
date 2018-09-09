#include <wiringPi.h>
#include <stdlib.h>
#include <stdio.h>

const int DIR1=0;
const int PUL1=2;
const int DIR2=21;
const int PUL2=3;

int main(int argc, char** argv){
	if(argc<3) return 0;
	
	int motornum = atoi(argv[1]);
	int value = atoi(argv[2]);
	if(value==0) return 0;
		
	int dir = DIR1;
	int pul = PUL1;
	
	if(motornum==1){
		dir = DIR1;
		pul = PUL1;
	}
	else if (motornum==2){
		dir = DIR2;
		pul = PUL2;
	}		
	else{ return 0;}
	
	wiringPiSetup();
	pinMode(dir, OUTPUT);
	pinMode(pul, OUTPUT);

	if(value>0)
	{
		printf("Moving %d steps forward\n", value);
		digitalWrite(dir,HIGH);
	}
	else
	{
		digitalWrite(dir,LOW);
		printf("Moving %d steps backward\n", value);
	}


  for (int i=0; i<abs(value); i++)
  {
    digitalWrite(pul,HIGH);
    delayMicroseconds(200);
    digitalWrite(pul,LOW);
    delayMicroseconds(200);
  }

}
