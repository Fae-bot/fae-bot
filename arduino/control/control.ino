int run = 0;


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
    digitalWrite(13, HIGH);
    digitalWrite(11, HIGH);
    digitalWrite(9, HIGH);
    digitalWrite(7, HIGH);
    delayMicroseconds(100);
    digitalWrite(13, LOW);
    digitalWrite(11, LOW);
    digitalWrite(9, LOW);
    digitalWrite(7, LOW);
    delayMicroseconds(100);  
  }
  if(Serial.available() > 0){
    char c = Serial.read();
    Serial.println(c);
    if(c=='q') { run=0; }
    if(c=='a') { run=1; all_dirs(HIGH);}
    if(c=='z') { run=1; all_dirs(LOW);} 
  }
}
