#include <wiringPi.h>
#include <stdlib.h>
#include <stdio.h>


int64_t current_ts = 0;
// Time slices size in microseconds
const int INCREMENTS=10;

struct Winch
{
    const int dir_pin;
    const int pulse_pin;
    // Number of microseconds between pulses
    int speed;
    // 1 or 0
    int direction;
    // Timestamp of the last pulse
    int64_t last_pulse;
    // 1=HIGH, 0=LOW
    int pulse_state;

    Winch(int dp, int pp) {
        dir_pin=dp;
        pulse_pin=pp;
        speed=0;
        direction=0;
        last_pulse=0;
        pulse_state=0;
        init();
    }

    void init(){
        pinMode(dir_pin, OUTPUT);
        pinMode(pulse_pin, OUTPUT);

        digitalWrite(dir,LOW);
        digitalWrite(pul,LOW);
        delayMicroseconds(200);
        digitalWrite(pul,HIGH);
        delayMicroseconds(200);
        digitalWrite(pul,LOW);
    }

    void switch_pulse_state(){
        pulse_state = 1- pulse_state;
        if(pulse_state==0)
            digitalWrite(pul,LOW);
        else
            digitalWrite(pul,HIGH);
    }
};


int main(int argc, char** argv){
    wiringPiSetup();

    Winch leftW(0,2);
    Winch rightW(21,3);

    Winch* winches = {leftW, rightW};
    int num_winches=2;

    if(argc<3) return 0;
	
    winches[0].speed = atoi(argv[1]);
    winches[1].speed = atoi(argv[2]);

    for(int i=0;i<num_winches;i++){
        Winch& w = winches[i];
        if(w.speed>0){
            if(current_ts>w.last_pulse+w.speed){
                w.last_pulse=current_ts;
            }
        }
        current_ts+= INCREMENTS;
        delayMicroseconds(INCREMENTS);
    }
}
