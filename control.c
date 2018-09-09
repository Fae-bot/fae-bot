#include <wiringPi.h>
#include <stdlib.h>
#include <stdio.h>


int64_t current_ts = 0;
// Time slices size in microseconds
const int INCREMENTS=10;

typedef struct Winch
{
    int dir_pin;
    int pulse_pin;
    // Number of microseconds between pulses
    int speed;
    // 1 or 0
    int direction;
    // Timestamp of the last pulse
    int64_t last_pulse;
    // 1=HIGH, 0=LOW
    int pulse_state;
} Winch;

void init_winch(Winch* w){
	pinMode(w->dir_pin, OUTPUT);
	pinMode(w->pulse_pin, OUTPUT);

	digitalWrite(w->dir_pin,LOW);
	digitalWrite(w->pulse_pin,LOW);
	delayMicroseconds(200);
	digitalWrite(w->pulse_pin,HIGH);
	delayMicroseconds(200);
	digitalWrite(w->pulse_pin,LOW);
	w->pulse_state=0;
	w->speed=0;
	w->direction=0;
	w->last_pulse = current_ts;
}

void set_direction(Winch* w){
	if(w->direction==1)
		digitalWrite(w->dir_pin, HIGH);
	else
		digitalWrite(w->dir_pin, LOW);
	}

void switch_pulse_state(Winch* w){
	w->pulse_state = 1- w->pulse_state;
	if(w->pulse_state==0)
		digitalWrite(w->pulse_pin,LOW);
	else
		digitalWrite(w->pulse_pin,HIGH);
}



int main(int argc, char** argv){
    wiringPiSetup();

	int num_winches=2;
    Winch* winches = (Winch*)(malloc(sizeof(Winch)*2));
    
    winches[0] = (Winch){.dir_pin=0, .pulse_pin=2};
	winches[1] = (Winch){.dir_pin=21, .pulse_pin=3};
    
    for(int i=0;i<num_winches;i++){
		init_winch(&winches[i]);
	}

    if(argc<3) return 0;

    for(int i=0;i<num_winches;i++){
		Winch* w = &winches[i];
		int speed = atoi(argv[i+1]);
		w->speed = abs(speed);
		if(speed>0) w->direction=1;
		else w->direction=0;
		set_direction(w);
	}
	

	while(1){
		for(int i=0;i<num_winches;i++){
			Winch* w = &winches[i];
			if(w->speed>0){
				if(current_ts>w->last_pulse+w->speed){
					switch_pulse_state(w);
					w->last_pulse=current_ts;
				}
			}
			current_ts+= INCREMENTS;
			delayMicroseconds(INCREMENTS);
		}
	}
}
