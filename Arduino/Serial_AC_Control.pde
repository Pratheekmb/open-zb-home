#include <IRremote.h>


unsigned int c = 0;

#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);


IRsend irsend;




char buff[128]; //receive incoming commands via UART.
int count;      //count the length of incoming commands

String temp_start = "Temperature (AC Module): ";
size_t temp_start_size = temp_start.length();
char temp[30]; //for the convrsion of the temperature float.
unsigned long last_reading = 0;
unsigned long now = 0;
unsigned long interval;
int cyclic_read = 0;  


void setup()
{
  char byte1, byte2;

  Serial.begin(57600);

  sensors.begin();
  
  /* Send AT continually untill OK received. unlikely? but depending on timing, hangle KO too */
  while(true){
    Serial.print("AT");  
    delay(100);
    if(Serial.available()>1){
      byte1=Serial.read();
      byte2=Serial.read();
      if ((byte1=='O' || byte1=='K') && (byte2=='O' || byte2=='K')){
        Serial.flush();
        break;
      }
    }
    delay(500);
  }
  Serial.println("AC IR MODULE ONLINE");
  getTemp();
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

  if (cyclic_read && ( (millis() -  last_reading) > interval) ){
    getTemp(); 
  }

}


/*
 * Parse commands, eg:
 * "p" sends 'ping'
 * "C" sends implicit command for IR.  
 * "t" gets single temperature reading. "t1" sets interval to 100ms. "t0" stops cyclic temp reading.
 */
void parse(char* buff, int count) {

  switch (buff[0]) {
  case 'p':
    Serial.println("AC IR MODULE ONLINE");
    getTemp();
    break;
  case 'C':
    Serial.print("Sent implicit IR code:");
    Serial.println(&buff[1]);
    sendIRCode(&buff[1]); 
    break;
  case 't':
    switch (buff[1]) {
    case 0:      //no time specified (end of cmd string), single reading.
      getTemp();
      break;
    default:
      interval = atoi(&buff[1]);
      if (interval) {
        getTemp();
        cyclic_read = 1;
        interval=100*interval; 
      } 
      else {
        cyclic_read = 0; 
      }
      break;
    }
    break;
  default:  
    break;
  }
}

void getTemp() {
  float reading;

  for (int attempts=10; attempts!=0; attempts--){
    sensors.setWaitForConversion(false);  // makes it async
    sensors.requestTemperatures();
    sensors.setWaitForConversion(true);
    delay(94);
    reading=sensors.getTempCByIndex(0);
    //Attempt to get a non error or startup values. 
    if ((int)(reading*1000)==0 || reading == 85.00 || (int)reading == -127) {
      continue;
      delay(100); 
    }
    else {
      dtostrf(sensors.getTempCByIndex(0), 3, 2, temp);  //convert float to char array in temp
      Serial.println(temp_start.substring(0,temp_start_size).concat(String(temp)));
      delay(3);  //allow time for xbee to packetize. 
      last_reading=millis();
      return;
    }
  }
    Serial.println(temp_start.substring(0,temp_start_size).concat(String("ERROR")));
    return;  
}

/*
 * I've found that my AC sends commands in 2 main ways, repeating the main code 3 times.
 * for a power toggling command (in my ASCII format): mzCOMMANDkzCOMMANDkzCOMMAND~
 * for a non p toggling command (in my ASCII format): miCOMMANDkiCOMMANDkiCOMMAND~
 * Therefor, I just send either zCOMMAND or iCOMMAND and this takes care of the repeating
 * Also note that the command itself may differ, refer to the communication.js
 */
void sendIRCode (char* code) {

  irsend.enableIROut(38);

  code[-1]='m';                  //this is OK cause it used to be '[' from the frame.
  sendMyRaw(&code[-1]);
  code[-1]='k';
  sendMyRaw(&code[-1]);
  code[-1]='k';
  sendMyRaw(&code[-1]);
  sendMyRaw("~");
  irsend.space(0); // Just to be sure

  delayMicroseconds(4000);
}

/*
 * This is a modified version of IRremote libraries sendRaw. Instead of receiving a 
 * buffer of delay times, it receives ASCII chars. See my modified raw decoder for the other
 * side of this (how to encode into ASCII string)
 */
void sendMyRaw(char buf[])
{
  for (int i = 0; buf[i]!=0; i++) {
    if (i & 1) {
      irsend.space(((byte)buf[i]-48)*50);    
    } 
    else {
      irsend.mark(((byte)buf[i]-48)*50);
    }
  }
}


