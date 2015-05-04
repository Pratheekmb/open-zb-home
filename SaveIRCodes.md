# How I saved the IR codes. #

Using [Ken Shirriff's Arduino IR Library](http://www.arcfn.com/2009/08/multi-protocol-infrared-remote-library.html),
I modified the raw code dump function in the libraries source code to create an array output which I could easily copy into code to replay:
```
Serial.println("");
  Serial.print("Raw (");
  Serial.print(count, DEC);
  Serial.print("): {");

  for (int i = 1; i < count; i++) {
    if ((i % 2) == 1) {
      Serial.print(results->rawbuf[i]*USECPERTICK, DEC);
    } 
    else {
      Serial.print((int)results->rawbuf[i]*USECPERTICK, DEC);
    }
    if(i<count-1) Serial.print(",");
  }
  Serial.println("};");
```


This gives me an output which i can hard code, eg:
```
unsigned int ac_toggle_code[] = 
{ 3050,3800 ,1850,950 ,950,1900 ,1850,950 ,950,950 ,950,950 ,950,950 ,900,950 ,950,950 ,900,1000 ,900,1900 ,950,950 ,900,950 ,1850,950 ,950,950 ,950,950 ,950,950 ,900,950 ,950,950 ,950,950 ,900,950 ,950,950 ,950,950 ,900,1900 ,950,950 ,900,1000 ,1850,900 ,1000,950 ,900,950 ,950,950 ,950,950 ,900,950 ,950,950 ,900,950 ,950,1900 ,1850,950 ,2900,3850 ,1850};
```

and then used (look at my AC code for sendIRCode):

```
sendIRCode(&ac_toggle_code[0], sizeof(ac_toggle_code)/sizeof(int));
```