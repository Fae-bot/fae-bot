int run = 0;

int last_switch[] = {0,0,0,0};
int current_state[] = { LOW, LOW, LOW, LOW};
int cycle_length[]={0, 0, 0, 0};

int current_time=0;
const int INTERVAL=10;
const int RESET_INTERVAL=10000000;

void setup() {
  pinMode(13, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(6, OUTPUT);
  digitalWrite(12, HIGH);
  Serial.begin(9600);
}

void all_dirs(int dir){
  digitalWrite(12, dir);
  digitalWrite(10, dir);
  digitalWrite(8, dir);
  digitalWrite(6, dir);
}


void loop() {
  if(run==1){
    if(current_time>RESET_INTERVAL){
      
          for(int i=0;i<4;i++){
            last_switch[i] -= current_time;
      }
      current_time = 0;
    }
    
    for(int i=0;i<4;i++){
      if(cycle_length[i]==0) continue;
      if(last_switch[i]+cycle_length[i]<current_time){
        if(current_state[i]==LOW) current_state[i]=HIGH; else current_state[i]=LOW;
        digitalWrite(13-i*2, current_state[i]);
        last_switch[i]=current_time;
      }
    }
    
    current_time+=INTERVAL;
  }
  delayMicroseconds(INTERVAL);


  if(Serial.available() > 0){
    char c = Serial.read();
    Serial.println(c);
    if(c=='s') { run=0; }
    if(c=='g') { run=1; }
    if(c=='m') { 
      int mnum = Serial.parseInt() -1;
      int mspeed = Serial.parseInt();
      if(mspeed<0){
        cycle_length[mnum] = -mspeed;
        digitalWrite(12-mnum*2, LOW);
      }
      else{
        cycle_length[mnum] = mspeed;
        digitalWrite(12-mnum*2, HIGH);
      }
    } 
  }
}
