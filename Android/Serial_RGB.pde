#define  LEDR 9      // the pin that the LED is attached to
#define  LEDG 10      // the pin that the LED is attached to
#define  LEDB 11      // the pin that the LED is attached to
#define LIGHTPIN 13


#define MAX_BUFF_SIZE 128
#define MAXVAL 254        //8 bit PWM max value.
#define FADE_DELAY 20


char buff[MAX_BUFF_SIZE];
int count;
unsigned long now;

unsigned int red = 0;
unsigned int green = 0;
unsigned int blue = 0;


void setup()
{
  // initialize the serial communication:
  Serial.begin(57600);
  // initialize the pins for output:
  pinMode(LEDR, OUTPUT);
  pinMode(LEDG, OUTPUT);
  pinMode(LEDB, OUTPUT);
  pinMode(LIGHTPIN, OUTPUT);

}

void loop() {
  //The following block parses serial in for bits between '[' and ']', ignored everything else. 
  if(Serial.available()>0){
    if(Serial.read()=='[') {
      now = millis();
      count=0;
      while ((millis()-now)<100){
        if (Serial.available()>0){
          buff[count]=Serial.read();
          if (buff[count]==']') {
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


void parse(char* buff, int count) {

  switch (buff[0]) {
  case 'c':
    if (count==7) {
      setLed(&buff[1]);
    }
    break;
  case 'f':
    fade(random(0,MAXVAL),random(0,MAXVAL),random(0,MAXVAL));
    break;
  case 'l':
    switch (buff[1]) {
    case '1':
      Serial.println("LIGHT ON");
      digitalWrite(LIGHTPIN, HIGH);
      break;
    case '0':
      Serial.println("LIGHT OFF");
      digitalWrite(LIGHTPIN, LOW); 
      break;
    default:  
      break;
    }
    break;    
  default:  
    break;
  }
}


void setLed (char* buff) {
  analogWrite(LEDR, red = hexToDec(buff[0],buff[1]));
  analogWrite(LEDG, green = hexToDec(buff[2],buff[3]));
  analogWrite(LEDB, blue = hexToDec(buff[4],buff[5]));
}



void fade (int r, int g, int b) {
  while (r!=red && g!=green && b!=blue){
    if (r != red)   analogWrite(LEDR, r > red   ? red += 1 : red -= 1);
    if (g != green) analogWrite(LEDG, g > green ? green += 1 : green -= 1);
    if (b != blue)  analogWrite(LEDB, b > blue  ? blue += 1 : blue -= 1);
    delay(FADE_DELAY);
  }
}



char hexToDec(char a, char b) {

  if (a >= '0' && a <= '9') {
    a -= '0';
  } 
  else if (a >= 'A' && a <= 'F') {
    a = a - 'A' + 10;
  }

  if (b >= '0' && b <= '9') {
    b -= '0';
  } 
  else if (b >= 'A' && b <= 'F') {
    b = b - 'A' + 10; 
  }
  return a*16+b;
}









