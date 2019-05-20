int run = 0;

long last_switch[] = {0,0,0,0};
int current_state[] = { LOW, LOW, LOW, LOW};
int cycle_length[]={0, 0, 0, 0};
int directions[] = {1,1,1,1};

long current_time=0;
int reset_counts=0;




const int NUM_WINCHES = 4;
const int INTERVAL=5;
const long RESET_INTERVAL=10000000;

void setup() {
  pinMode(9, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(2, OUTPUT);
  digitalWrite(8, HIGH);
  Serial.begin(9600);
}

void all_dirs(int dir){
  digitalWrite(8, dir);
  digitalWrite(6, dir);
  digitalWrite(4, dir);
  digitalWrite(2, dir);
}


void loop() {
  if(run==1){
    if(current_time>RESET_INTERVAL){
      
          for(int i=0;i<NUM_WINCHES;i++){
            last_switch[i] -= current_time;
      }
      current_time = 0;
      reset_counts++;
    }
    
    for(int i=0;i<NUM_WINCHES;i++){
      if(cycle_length[i]==0) continue;
      if(last_switch[i]+cycle_length[i]<current_time){
        if(current_state[i]==LOW) current_state[i]=HIGH; else current_state[i]=LOW;
        digitalWrite(9-i*2, current_state[i]);
        last_switch[i]=current_time;
      }
    }
    
    current_time+=INTERVAL;
  }
  delayMicroseconds(INTERVAL);


  while(Serial.available() > 0){
    char c = Serial.read();
    if(c=='s') { run=0; }  // Stop
    if(c=='g') { run=1; }  // Go
    if(c=='m') {           // Motor <ID> <speed>
      int mnum = Serial.parseInt() -1;
      if(mnum<0 || mnum>3 ) return;
      int mspeed = Serial.parseInt();
      if(mspeed<0){
        cycle_length[mnum] = -mspeed;
        digitalWrite(8-mnum*2, LOW);
        directions[mnum]=-1;
      }
      else{
        cycle_length[mnum] = mspeed;
        digitalWrite(8-mnum*2, HIGH);
        directions[mnum]=1;        
      }
    }
    if(c=='e') {          // Check speed
      for(int i=0;i<NUM_WINCHES;i++){
        Serial.println(cycle_length[i]);
      }
    }
    if(c=='r') {          // Check resets
      Serial.println(current_time);
      Serial.println(reset_counts);
    }    
  }
}
