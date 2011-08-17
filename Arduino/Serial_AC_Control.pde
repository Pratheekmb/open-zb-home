#include <IRremote.h>


unsigned int c = 0;

//IR sequence to toggle A/C power.
unsigned int ac_toggle_code[] = {
  3150,3700,2000,800,1050,1800,1950,850,1050,850,1050,850,1050,850,1000,850,1050,850,1050,850,1000,850,1050,1800,1950,850,1050,850,1000,850,1050,850,1050,850,1000,900,1000,850,1050,850,1000,850,1050,850,1000,1800,1950,1800,1050,850,1050,850,1950,1800,1950,850,1050,850,1050,850,1050,850,1000,850,1050,1800,1950,850,2950};

unsigned int fan_01_code[] = {
  3150,2800,1050,850,1050,850,1000,1800,1950,850,1050,850,1050,850,1000,850,1050,850,1050,850,1000,850,1050,850,1050,800,1050,1800,1950,850,1050,850,1050,850,1050,800,1050,850,1050,850,1000,850,1050,850,1050,1800,1950,1750,1050,900,1000,850,1950,1800,1050,850,1950,850,1050,850,1050,850,1050,850,1000,850,1050,1800,1950,850,3000};

unsigned int fan_02_code[] = {
  3100,2750,1050,900,1000,850,1050,1800,1950,1750,2000,850,1050,850,1050,850,1000,850,1050,850,1050,850,1000,850,1050,1800,1950,850,1050,850,1000,900,1000,850,1050,850,1000,850,1050,850,1050,850,1000,1800,1950,1800,1050,850,1050,850,1950,1800,1050,850,1950,850,1050,850,1000,850,1050,850,1050,800,1050,1800,2000,800,3000};

unsigned int fan_03_code[] = {
  3100,2850,1000,850,1050,850,1000,1800,1050,850,1950,850,1050,850,1050,850,1000,900,1000,850,1050,850,1000,850,1050,850,1050,1800,1950,850,1050,850,1000,850,1050,850,1000,850,1050,850,1050,850,1000,850,1050,1800,1950,1800,1050,850,1050,850,1950,1750,1100,850,1950,850,1050,850,1000,850,1050,850,1050,850,1000,1800,1950,850,3000};

unsigned int fan_04_code[] = {
  3150,2800,1000,900,1000,850,1050,1750,1050,850,1050,850,1950,850,1050,850,1050,850,1000,850,1050,850,1050,850,1000,850,1050,1800,1950,850,1050,850,1050,850,1000,850,1050,850,1050,800,1050,850,1050,850,1000,1800,1950,1800,1050,850,1050,850,1950,1800,1050,850,1950,850,1050,850,1050,850,1000,850,1050,850,1000,1800,1950,850,3000};


IRsend irsend;


unsigned long timer_start_time = millis();
int timer_status = 0;
unsigned int timer_duration=0;
char buff[128];
int count;
int timerval;
unsigned long now;


void setup()
{
  Serial.begin(57600);
}



void loop()
{
  IRTimerCheck();

  //The following block parses serial in for bits between '[' and ']', ignored everything else. 
  if(Serial.available()>0){
    if(Serial.read()=='[') {          // wait for frame start char.
      now = millis();
      count=0;
      while ((millis()-now)<100){     // timeout
        if (Serial.available()>0){
          buff[count]=Serial.read();  // store frame in the global buffer.
          if (buff[count]==']') {     // untill frame end char.
            buff[count] = '\0';
            break;
          } 
          count++;
        }
      } 
      parse(buff, count);
    }
  }    
}


/*
 * Parse commands, eg:
 * "o" sends ON/OFF
 * "t3" sets timer for 3 minutes
 * "f1" sets fan speed to 1.
*/
void parse(char* buff, int count) {

  switch (buff[0]) {
  case 'o':
    sendIR();
    timer_status=0; // Override timer.
    break;
  case 't':
    Serial.print("TIMER:");
    Serial.println(atoi(&buff[1]), DEC);
    IRTimerSet(atoi(&buff[1])); 
    break;
  case 'f':
    switch (buff[1]) {
    case '1':
      Serial.println("Fan set to 1"); 
      sendIRCode(&fan_01_code[0], sizeof(fan_01_code)/sizeof(int)); 
      break;
    case '2':
      Serial.println("Fan set to 2"); 
      sendIRCode(&fan_02_code[0], sizeof(fan_02_code)/sizeof(int)); 
      break;
    case '3':
              Serial.println("Fan set to 3"); 
      sendIRCode(&fan_03_code[0], sizeof(fan_03_code)/sizeof(int)); 
      break;
    case 'A':
      Serial.println("Fan set to Auto"); 
      sendIRCode(&fan_04_code[0], sizeof(fan_04_code)/sizeof(int)); 
      break;
    default:  
      break;
    }          
  default:  
    break;
  }
}



void IRTimerSet (unsigned int mins) {
  timer_duration=mins;
  if (mins==0){
    timer_status=0;
  } 
  else {
    if (!timer_status)  sendIR(); //extends timer if it is already on.
    timer_status=1;
    timer_start_time = millis();
  }
}


void IRTimerCheck (void) {
  if (timer_status==1 && ((millis()-timer_start_time)>((unsigned long)timer_duration*1000*60))){
    sendIR();
    timer_status=0; 
  }
}


void sendIR (void) {
  //Send IR code in 3 repeat bursts to increase transfer chance.
  irsend.sendRaw(ac_toggle_code, sizeof(ac_toggle_code)/sizeof(int), 38);
  delayMicroseconds(30);
  irsend.sendRaw(ac_toggle_code, sizeof(ac_toggle_code)/sizeof(int), 38);
  delayMicroseconds(30);
  irsend.sendRaw(ac_toggle_code, sizeof(ac_toggle_code)/sizeof(int), 38);
  Serial.println("ON/OFF SENT");
}

void sendIRCode (unsigned int* code, int code_size) {
  //Send IR code in 3 repeat bursts to increase transfer chance.
  irsend.sendRaw(code,code_size, 38);
  delayMicroseconds(30);
  irsend.sendRaw(code,code_size, 38);
  delayMicroseconds(30);
  irsend.sendRaw(code,code_size, 38);

  Serial.println("SENT IR"); 

}