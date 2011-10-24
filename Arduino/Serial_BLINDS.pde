char buff[128]; //receive incoming commands via UART.
int count;      //count for length of incoming commands

unsigned long now = 0, interval = 0;
boolean stopped=false;

#define  UPIN   7
#define  DOWNIN 8

#define  UP   9
#define  DOWN 10

void setup()
{

  pinMode(UP, OUTPUT);
  digitalWrite(UP,LOW);

  pinMode(DOWN, OUTPUT);
  digitalWrite(DOWN,LOW);

  pinMode(UPIN, INPUT);
  pinMode(DOWNIN, INPUT);
  digitalWrite(UPIN,HIGH);    //pull-up
  digitalWrite(DOWNIN,HIGH);  //pull-up

  Serial.begin(9600);
  Serial.println("BLINDS ONLINE");
}



void loop()
{
  /*
 *The following block parses serial in for bits between '[' and ']', ignored everything else.
   *The contents are passed on to be processed by parse(..). 
   */
  if(Serial.available()>0){
    if(Serial.read()=='[') {          // wait for frame start char.
      now = millis();
      count=0;
      while ((millis()-now)<100){     // timeout
        if (Serial.available()>0){
          buff[count]=Serial.read();  // store frame in the global buffer.
          if (buff[count]==']') {     // untill frame end char.
            buff[count] = 0;
            break;
          } 
          count++;
        }
      } 
      parse(buff, count);
    }
  }
  if (   ((millis()-now) > 20000)  || ( interval && ((millis()-now) > interval)  ))    halt(); 


  // Debounce hardware over-ride switches
  if (!digitalRead(UPIN)){
    delay(20);
    if (!digitalRead(UPIN)) {
      up();
      while (!digitalRead(UPIN)){}
      halt();
    }
  }

  if (!digitalRead(DOWNIN)){
    delay(20);
    if (!digitalRead(DOWNIN)) {
      down();
      while (!digitalRead(DOWNIN)){}
      halt();
    }
  }

}


/*
 * Parse commands
 */
void parse(char* buff, int count) {

  switch (buff[0]) {
  case 'p':
    Serial.println("BLINDS ONLINE");
    break;
  case 'U':
    up();
    break;
  case 'D':
    down();
    break;
  case 'S':
    halt();
    break;
  default:  
    break;
  }

  switch (buff[1]) {
  case 0:
    interval=0;
    break;
  default:
    interval = 100*atoi(&buff[1]);  //eg command: [D15] rolls blinds down for 1.5 seconds. 
    break;
  }

}

void up(){
  if(!stopped) halt(); 
  Serial.println("BLINDS UP");
  digitalWrite(DOWN,LOW);    //This should always be low from halt anyway, just a precaution to never have both UP/DOWN high together.
  delay(50);
  stopped=false; 
  digitalWrite(UP,HIGH);
  now=millis();
}

void down(){
  if(!stopped) halt(); 
  Serial.println("BLINDS DOWN");
  digitalWrite(UP,LOW);
  delay(50);
  stopped=false; 
  digitalWrite(DOWN,HIGH);
  now=millis();
}

void halt(){
  if (!stopped) {
    digitalWrite(UP,LOW); 
    digitalWrite(DOWN,LOW);
    stopped=true;
    Serial.println("BLINDS STOPPED");
    delay(200);
  }
}
