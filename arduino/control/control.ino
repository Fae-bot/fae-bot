int run = 0;

int last_switch[] = {0,0,0,0};
int current_state[] = { LOW, LOW, LOW, LOW};
int cycle_length[]={0, 0, 0, 0};
int positions[] ={0,0,0,0};
int directions[] = {1,1,1,1};
int targets[16*4];
int cycle_targets[6*4];

int current_time=0;
int target_id=-1;
int cycle=-1;
int cycle_speed=0;
const int NUM_WINCHES = 4;
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
        positions[i] += directions[i];
      }
    }
    
    current_time+=INTERVAL;
    if(cycle==-1){
      if(target_id>-1 && target_id<16){
        for(int i=0;i<NUM_WINCHES;i++){
          if(targets[target_id*4+i]>positions[i]){
            directions[i]=1;
            digitalWrite(12-i*2, HIGH);
          }
          if(targets[target_id*4+i]<positions[i]){
            directions[i]=-1;
            digitalWrite(12-i*2, LOW);
          }
          if(targets[target_id*4+i]==positions[i]){
            cycle_length[i]=0;
          }
        }
      }
    }
    else
    {
      for(int i=0;i<NUM_WINCHES;i++){
        if(cycle_targets[cycle*4+i]>positions[i]){
          directions[i]=1;
          digitalWrite(12-i*2, HIGH);
        }
        if(cycle_targets[cycle*4+i]<positions[i]){
          directions[i]=-1;
          digitalWrite(12-i*2, LOW);
        }
        if(cycle_targets[cycle*4+i]==positions[i]){
          cycle_length[i]=0;
        }
      }
      int reached=1;
      for(int i=0;i<NUM_WINCHES;i++)
      {
        if(cycle_targets[cycle*4+i]!=positions[i]) reached=0;
      }
                      
      if(reached==1){ 
        cycle = (cycle+1)%6; 
        target_id=cycle;
        set_all_speeds(cycle_speed);
      }
    }
  }
  delayMicroseconds(INTERVAL);


  if(Serial.available() > 0){
    char c = Serial.read();
    if(c=='s') { run=0; target_id=-1; cycle =-1;}  // Stop
    if(c=='g') { run=1; target_id=-1; }  // Go
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
    if(c=='c') {          // Check target
      int tnum = Serial.parseInt();
      for(int i=0;i<NUM_WINCHES;i++){
        Serial.println(targets[tnum*4+i]);
      }
    }
    if(c=='n') {          // New target <ID>
      int tnum = Serial.parseInt();
      targets[tnum*4] = positions[0];
      targets[tnum*4+1] = positions[1];
      targets[tnum*4+2] = positions[2];
      targets[tnum*4+3] = positions[3];
  }
  if(c=='a') {           // Advance to target <ID> <speed>
      target_id = Serial.parseInt();
      int tspeed = Serial.parseInt();      
      /*for(int i=0;i<NUM_WINCHES;i++){
          cycle_length[i] = tspeed;
      }*/
      set_all_speeds(tspeed);
      run = 1;
  }
  if(c=='y') {           // cYcle between 4 first targets <speed>
      int tspeed = Serial.parseInt();        
      int t1[4];
      int t2[4];
      t1[0] = targets[0];
      t1[1] = targets[1];
      t1[2] = targets[2];
      t1[3] = targets[3];
 
      t2[0] = targets[4];
      t2[1] = targets[5];
      t2[2] = targets[6];
      t2[3] = targets[7];
 
      cycle_targets[0] = t1[0]-4000;
      cycle_targets[1] = t1[1]-4000;
      cycle_targets[2] = t1[2]-4000;
      cycle_targets[3] = t1[3]-4000;      
      
      cycle_targets[4] = t1[0];
      cycle_targets[5] = t1[1];
      cycle_targets[6] = t1[2];
      cycle_targets[7] = t1[3];      
      
      cycle_targets[8] = t1[0]-4000;
      cycle_targets[9] = t1[1]-4000;
      cycle_targets[10] = t1[2]-4000;
      cycle_targets[11] = t1[3]-4000;      
      
      cycle_targets[12] = t2[0]-4000;
      cycle_targets[13] = t2[1]-4000;
      cycle_targets[14] = t2[2]-4000;
      cycle_targets[15] = t2[3]-4000;      
      
      cycle_targets[16] = t2[0];
      cycle_targets[17] = t2[1];
      cycle_targets[18] = t2[2];
      cycle_targets[19] = t2[3];      
      
      cycle_targets[20] = t2[0]-4000;
      cycle_targets[21] = t2[1]-4000;
      cycle_targets[22] = t2[2]-4000;
      cycle_targets[23] = t2[3]-4000;      
      
      cycle = 0;
      target_id = 2;
      run = 1;
      set_all_speeds(tspeed);
      cycle_speed = tspeed/2;
    }
  }
}

void set_all_speeds(int s){
    for(int i=0;i<NUM_WINCHES;i++){
      cycle_length[i] = s;
    }
}
