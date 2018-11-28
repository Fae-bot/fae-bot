int run = 0;

int last_switch[] = {0,0,0,0};
int current_state[] = { LOW, LOW, LOW, LOW};
int cycle_length[]={0, 0, 0, 0};
long positions[] ={0,0,0,0};
int directions[] = {1,1,1,1};
int targets[4];

int current_time=0;

const int NUM_WINCHES = 4;
const int INTERVAL=1;
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
      
          for(int i=0;i<NUM_WINCHES;i++){
            last_switch[i] -= current_time;
      }
      current_time = 0;
    }
    
    for(int i=0;i<NUM_WINCHES;i++){
      if(cycle_length[i]==0) continue;
      if(last_switch[i]+cycle_length[i]<current_time){
        if(current_state[i]==LOW) current_state[i]=HIGH; else current_state[i]=LOW;
        digitalWrite(13-i*2, current_state[i]);
        last_switch[i]=current_time;
        positions[i] += directions[i];
      }
    }
    
    current_time+=INTERVAL;

    for(int i=0;i<NUM_WINCHES;i++){
      if(targets[i]>positions[i]){
        directions[i]=1;
        digitalWrite(12-i*2, HIGH);         // Not necessary every cycle
      }
      if(targets[i]<positions[i]){
        directions[i]=-1;
        digitalWrite(12-i*2, LOW);          // Not necessary every cycle
      }
      if(targets[i]==positions[i]){
        cycle_length[i]=0;
      }
    }
  }
  delayMicroseconds(INTERVAL);


  if(Serial.available() > 0){
    char c = Serial.read();
    if(c=='s') { run=0; }  // Stop
    if(c=='g') { run=1; }  // Go
    if(c=='m') {           // Motor <ID> <speed>
      int mnum = Serial.parseInt() -1;
      int mspeed = Serial.parseInt();
      if(mspeed<0){
        cycle_length[mnum] = -mspeed;
        digitalWrite(12-mnum*2, LOW);
        directions[mnum]=-1;
      }
      else{
        cycle_length[mnum] = mspeed;
        digitalWrite(12-mnum*2, HIGH);
        directions[mnum]=1;        
      }
    }
    if(c=='z') {          // Zero
      for(int i=0;i<NUM_WINCHES;i++){
        positions[i]=0;
      }
    }
    if(c=='p') {          // Position
      for(int i=0;i<NUM_WINCHES;i++){
        Serial.println(positions[i]);
      }
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
      int w1 = Serial.parseInt();
      int w2 = Serial.parseInt();
      int w3 = Serial.parseInt();
      int w4 = Serial.parseInt();
      targets[0] = w1;
      targets[1] = w2;
      targets[2] = w3;
      targets[3] = w4;
    }
  }
}

