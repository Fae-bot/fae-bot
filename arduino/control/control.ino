// TODO: uses types with explicit bit length

int run = 0;
int mode = 0;

unsigned long last_switch[] = {0,0,0,0};
int current_state[] = { LOW, LOW, LOW, LOW};
unsigned long cycle_length[]={0, 0, 0, 0};
long positions[] ={0,0,0,0};
int directions[] = {1,1,1,1};
long targets[4];

unsigned long current_time=0;
int reset_counts=0;
unsigned long last_feedback=0;
unsigned long feedback_period=200000; // 200 ms




const int NUM_WINCHES = 4;

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
  Serial.begin(1000000);
}

void all_dirs(int dir){
  digitalWrite(8, dir);
  digitalWrite(6, dir);
  digitalWrite(4, dir);
  digitalWrite(2, dir);
}


void loop() {
  current_time=micros();
  if(feedback_period>0){
      if(current_time-last_feedback>feedback_period){
          for(int i=0;i<NUM_WINCHES;i++){
            Serial.print(positions[i]);
            Serial.print(' ');
          }
          Serial.print('\n');
          last_feedback = current_time;
      }
  }
    
  if(run==1){
    
    for(int i=0;i<NUM_WINCHES;i++){
      if(cycle_length[i]==0) continue;
      if(current_time-last_switch[i] > cycle_length[i]){
        if(current_state[i]==LOW) current_state[i]=HIGH; else current_state[i]=LOW;
        digitalWrite(9-i*2, current_state[i]);
        last_switch[i] = current_time;
        positions[i] += directions[i];
      }
    }


    if(mode==1){  // Are we in target mode?
        for(int i=0;i<NUM_WINCHES;i++){
          if(targets[i]>positions[i]){
            directions[i]=1;
            digitalWrite(8-i*2, HIGH);         // Not necessary every cycle
          }
          if(targets[i]<positions[i]){
            directions[i]=-1;
            digitalWrite(128-i*2, LOW);          // Not necessary every cycle
          }
          if(targets[i]==positions[i]){
            cycle_length[i]=0;
          }
        }
    }
  }

  while(Serial.available() > 0){
    char c = Serial.read();
    if(c=='s') { run=0; }  // Stop
    if(c=='g') { run=1; }  // Go
    if(c=='m') {           // Motor <ID> <speed>
      int mnum = Serial.parseInt() -1;
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
    if(c=='z') {          // Resets positionx
      for(int i=0;i<NUM_WINCHES;i++){
        positions[i]=0;
      }
    }
    if(c=='p') {          // Position
      for(int i=0;i<NUM_WINCHES;i++){
        Serial.print(positions[i]);
        Serial.print(' ');
      }
      Serial.print('\n');
    }
    if(c=='e') {          // Check speed
      for(int i=0;i<NUM_WINCHES;i++){
        Serial.println(cycle_length[i]);
      }
    }
    if(c=='c') {          // Check target
      for(int i=0;i<NUM_WINCHES;i++){
        Serial.println(targets[i]);
      }
    }
    if(c=='n') {          // New target <winch1> <winch2> <winch3> <winch4>
      long w1 = Serial.parseInt();
      long w2 = Serial.parseInt();
      long w3 = Serial.parseInt();
      long w4 = Serial.parseInt();
      targets[0] = w1;
      targets[1] = w2;
      targets[2] = w3;
      targets[3] = w4;
    }
    if(c=='r') {          // Check resets
      Serial.print(current_time);
      Serial.println(reset_counts);
    }
    if(c=='p') {     
      mode = Serial.parseInt();
      if(mode!=0) mode=1;
    }
    if(c=='f') {     
      feedback_period = Serial.parseInt()*1000;
    }
  }
}

