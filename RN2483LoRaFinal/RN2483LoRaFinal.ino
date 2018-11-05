#include <SoftwareSerial.h>
#include <EEPROM.h>
#include <TimeLib.h>

#define gpsRx 8
#define gpsTx 9
#define eesize 1024
#define resetPin 2
#define eeSpace 1020


//SoftwareSerial gpsSerial(gpsRx, gpsTx);
SoftwareSerial myserial(11, 12);


//int a;
uint8_t Hub = 1;
uint16_t recID = 0;


//LoRa Variables
uint16_t ID = 3;           //ID of Node
uint8_t msg = 0;               //Type of message being sent
uint8_t packetAmount = 0;     //Number of packets
uint8_t YM = 0;               //Year & Month byte (listed in that order)
uint8_t DH = 0;              //Day & Hour byte (listed in that order)
uint8_t Hm = 0;             //Hour & Minute byte
uint8_t data[] = {0, 0};    //Data bytes


//uint8_t Year = 0;
//uint8_t Month = 0;
//uint8_t Day = 0;
//uint8_t Hour = 0;
//uint8_t Min = 0;


long timeStamp[] = {201104, 201902, 201612, 201705, 200009, 200203, 200307, 200603, 200512, 201903};
long stamp[] = {20931, 101810, 10243, 130115, 31140, 131459, 280133, 110559, 290830, 220245};
uint16_t Data[] = {2222, 2222, 2222, 2222, 2222, 4440, 4440, 4440, 4440, 4440};


int eevalue = 0;
int rb = 0;
int wb = 0;
int j = 0;
int diff;
int x = 0;
int flagRoll = 0;



char readmsg[65];
byte loramsg[255];
int indlo = 0; //index to loramsg
bool msgRec = false;
bool msgStore;
bool rxFlag;
int index = 0;
uint8_t packRec = 0;


/*GPS Variables*/


void setup() {
  /*Lora communications setup*/
  Serial.begin(57600);
  Serial.setTimeout(2000);
  while (!Serial);

  /*GPS setup*/

  //  gpsSerial.begin(9600);

  /*debugging setup*/
  myserial.begin(9600);
  delay(500);
  myserial.println("Hello, world setup?");

  ////////////Hard Reset//////////////
  pinMode(resetPin, OUTPUT);
  digitalWrite(resetPin, LOW);
  delay(500);
  digitalWrite(resetPin, HIGH);
  delay(1000);
  readserial();
  loraReset();

  ///////////Listen Mode////////////
  myserial.println("rx on");
  Serial.println("radio rx 0");
  Serial.readStringUntil('\n');
  delay(150);

  msgRec = false;
  msgStore = false;
  rxFlag = false;

  eepromAddress();
}

void loop() {
  readserial();
  delay(200);
  digitalWrite(13, LOW);
  if (rxFlag) {
    Serial.readStringUntil('\n');
    delay(50);
    Serial.readStringUntil('\n');
    Serial.println("radio rx 0");
    rxFlag = false;
  }
  //  gpsSerial.listen();
  //  gpsRead();

}

void loraReset() {
  myserial.println("sys reset dude");
  Serial.println("sys reset");
  Serial.readStringUntil('\n');
  delay(300);

  Serial.println("radio set wdt 0");
  Serial.readStringUntil('\n');
  delay(50);

  Serial.println("radio set pwr 14");
  Serial.readStringUntil('\n');
  delay(50);

  Serial.println("mac pause");
  Serial.readStringUntil('\n');
  delay(50);

  Serial.println("radio set freq 868000000");
  Serial.readStringUntil('\n');
  delay(50);

  Serial.println("radio set sync 28");
  Serial.readStringUntil('\n');
  delay(50);

  Serial.println("radio set sf sf7");
  Serial.readStringUntil('\n');
  delay(50);

  Serial.println("radio set crc off");
  Serial.readStringUntil('\n');
  delay(50);

  msgRec = false;

  myserial.println("end of setup");
}

void readserial() {
  if (Serial.available()) {
    uint8_t packRec = 0;
    while (Serial.available() > 0) {
      char *pos;

      index = Serial.available();
      if (index == 63) {
        index = 62;
      }
      myserial.println("about to readbyte");
      Serial.readBytesUntil('\n', readmsg, index);
      if (readmsg[6] == 'r' && readmsg[7] == 'x' && !msgStore && readmsg[0] == 'r') {
        indlo = 0;
        if (readmsg[index - 2] == '\r') {
          packRec = (index - 12);
          readmsg[index - 2] = '\0';
          msgStore = false;
          msgRec = true;
        }
        else {
          packRec = (index - 10);
          //          myserial.print("package in else: ");
          //          myserial.println(packRec);
          msgStore = true;
          msgRec = false;
          readmsg[index] = '\0';
        }
        //        myserial.println(readmsg);
        pos = readmsg + 10;
        loraStore(pos, packRec);
      }
      else if (msgStore) {
        if (readmsg[index - 2] == '\r') {
          //          myserial.println("inside elseif if of msgstore");
          packRec = (index - 1);
          readmsg[index - 1] = '\0';
          msgStore = false;
          msgRec = true;
        }
        else {
          //          myserial.println("inside elseif else of msgstore");
          msgRec = false;
          packRec = index;
        }
        //        myserial.println("leaving elseif msgstore readserial");
        myserial.println(readmsg);
        pos = readmsg;
        loraStore(pos, packRec);
      }
      else {
        /*radio_err/busy/invalid_param/ok*/
        //        myserial.println("entering else of readserial");
        readmsg[index - 2] = '\0';
        myserial.println(readmsg);
        if (strcmp(readmsg, "ok")) {
          //          myserial.println("else in readserial, no reason to reset rx");
        }
        else {
          //          myserial.println("reseting rx next...");
          rxFlag = true;
        }
        packRec = index - 1;
        msgRec = false;
      }
      myserial.println("packet Received amount in while: ");
      myserial.println(packRec);
      myserial.println("readserial loop:");
      myserial.println(readmsg);
    }
  }
}


void loraStore(char *pos, uint8_t packRec) {
  char buf[3];
  int i = 0;
  //  myserial.println("packet size entering lorastore");
  //  myserial.println(packRec);
  //  myserial.println(packRec/2);
  while (i < (packRec / 2)) {
    buf[0] = *pos;
    pos += 1;
    buf[1] = *pos;
    pos += 1;
    buf[2] = '\0';
    if (buf[0] == '\0') {
      loramsg[indlo] = '\0';
    }
    else {
      loramsg[indlo] = strtoul(buf, NULL, 16);
    }
    //    myserial.println("loramsg: ");
    //    myserial.println(loramsg[indlo], DEC);
    indlo++;
    i++;
  }
  if (msgRec) {
    responseMessage();
    msgRec = false;
  }
  else {
    //    myserial.println("else loraStore");
    loraReset();
    Serial.println("radio rx 0");
    myserial.println(Serial.readStringUntil('\n'));
    //    myserial.println("loraStore over");

  }
}


void hexCheck(byte hex) {
  if (hex < 16) {
    Serial.print(0);
    Serial.print(hex, HEX);
    myserial.print(0);
    myserial.println(hex);
  }
  else {
    Serial.print(hex, HEX);
    myserial.println(hex);
  }
}

void responseMessage() {

  recID = ((loramsg[1]) << 8);
  recID = (recID | (loramsg[2]));
  if (Hub == loramsg[0] && recID == ID) {
    //    myserial.println("Inside if response");
    //    myserial.print("Snr: ");
    char snr[5] = {0};
    int i;
    //    int j = 0;
    int temp = 0;

    Serial.println("radio get snr");
    myserial.println("reading snr....");
    temp = Serial.readBytesUntil('\r', snr, 5);
    snr[temp] = '\0';
    myserial.println(temp);
             //    snr[i] = Serial.read();
    myserial.println(snr);
    //    if (snr[i] != '-') {
    //      snr[i + 1] = snr[i];
    //      snr[i] = '+';
    //      i = 2;
    //    }
    //    //    i=1;
    //    while (Serial.available() > 0) {
    //      temp = Serial.read();
    //      if (temp != '\r' || temp != '\n') {
    //        snr[i] = temp;
    //        i++;
    //      }
    //      myserial.print(temp);
    //    }
    //    snr[i] = '\0';
    myserial.println();
    myserial.println("snr again:");
    //    myserial.println(snr);
    //    myserial.println(Serial.readStringUntil('\n'));
    loraReset();
    msg = loramsg[3];
    switch (msg) {
      case 3:
        //        myserial.println("inside case responseMessage");
        digitalWrite(13, HIGH);
        packetAmount = 7;
        Serial.print("radio tx ");
        startPacket();
        i=0;
        if(snr[i] =='-'){
          hexCheck(snr[i]);
          i++;
        }
        else{
          hexCheck('+');
        }
        while(snr[i]!='\0'){
          hexCheck(snr[i]-48);
          i++;
        }
        Serial.println();
        myserial.println(Serial.readStringUntil('\n'));
        delay(50);
        break;
      case 1:
        //        myserial.println("LoRa Send inside response message");
        LoRaSend();
        break;
      case 2:
        msg = 0;
        //        myserial.println("adding time.....");
        timeSplit();
        break;
      case 4:
        msg = 1;
        break;
      case 5:
        packetAmount = 7;
        digitalWrite(13, HIGH);
        myserial.println("Test field message sendback loop");
        msg = 5;
        Serial.print("radio tx ");
        startPacket();
        i=0;
        if(snr[i] =='-'){
          hexCheck(snr[i]);
          i++;
        }
        else{
          hexCheck('+');
        }
        while(snr[i]!='\0'){
          hexCheck(snr[i]-48);
          i++;
        }
        Serial.println();
        myserial.println(Serial.readStringUntil('\n'));
        delay(500);
        break;
    }
  }
  else{
    delay(50);
    Serial.readStringUntil('\n');
  }
  Serial.println("radio rx 0");
  myserial.println(Serial.readStringUntil('\n'));
  myserial.println("end of responseMessage");
}

void eepromAddress() {                   //Only access EEPROM from 0 - 1019
  for (int i = 0; i < eeSpace; i = i + 5) { //Only need to read up to 1015 as that accounts for bytes up to 1019
    eevalue = EEPROM.read(i);
    if (eevalue == 255) {
      rb = i;
    }
    eevalue = EEPROM.read((i + 1));
    if (eevalue == 254) {
      wb = i;
    }
  }
  if (wb == 0) {
    wb = rb;
  }
  else if (wb >= rb) {
    packetAmount = abs(wb - rb) / 5;
  }
  else {
    packetAmount = abs(wb - rb);
    packetAmount = (eeSpace - packetAmount) / 5;
  }
}

void eepromUpdate() {
  if (wb == eeSpace) {
    flagRoll = 1;
    wb = 0;
  }
  if (!flagRoll) {
    EEPROM.update(wb, YM);
    wb++;
    EEPROM.update(wb, DH);
    wb++;
    EEPROM.update(wb, Hm);
    wb++;
    EEPROM.update(wb, data[0]); //always takes up two bytes
    wb++;
    EEPROM.update(wb, data[1]);
    wb++;
    packetAmount++;
  }
  else if (flagRoll && (wb != rb)) {
    EEPROM.update(wb, YM);
    wb++;
    EEPROM.update(wb, DH);
    wb++;
    EEPROM.update(wb, Hm);
    wb++;
    EEPROM.update(wb, data[0]); //always takes up two bytes
    wb++;
    EEPROM.update(wb, data[1]);
    wb++;
    packetAmount++;
  }
  else {
  }
}

/*Sensor Style Time/Data Split*/
void timeSplit() {
  byte Year = 0, Month = 0, Day = 0, Hour = 0, Min = 0;
  for (int i = 0; i < (sizeof(Data) / 2); i++) {
    Year = (timeStamp[i] / 100) % 10;
    Month = (timeStamp[i] % 100);
    Day = (stamp[i] / 1E4);
    Hour = (stamp[i] / 100) % 100;
    Min = (stamp[i] % 100);

    timeEncrypt(Year, Month, Day, Hour, Min);
    dataSplit(i);
    eepromUpdate();
  }
  if (rb != wb) {
    EEPROM.update((wb + 1), 254);
  }
}

void timeEncrypt(byte Year, byte Month, byte Day, byte Hour, byte Min) {
  YM = Month;
  YM = YM | (Year << 4);


  Hm = Min;
  Hm = Hm | (Hour << 6);

  DH = Hour >> 2;
  DH = DH | (Day << 3);
}

void dataSplit(int i) {
  data[0] = Data[i] >> 8;
  data[1] = (Data[i] & 0b0000000011111111);
}

void buildMessage() {
  hexCheck(YM);
  hexCheck(DH);
  hexCheck(Hm);
  hexCheck(data[0]);
  hexCheck(data[1]);
}

void startPacket() {
  hexCheck((ID >> 8));
  hexCheck((ID & 0b0000000011111111));
  hexCheck(msg);
  hexCheck(packetAmount);
}


void LoRaSend() {
  if ((wb != rb) || flagRoll) {
    if (wb > rb) {
      diff = abs(wb - rb);
    }
    else {
      diff = (eeSpace - rb) + wb;
    }
    if (diff == 0) {
      diff = eeSpace;
    }
    x = rb;
    j = x;
    while (diff != 0) {
      if (diff > 250) {
        diff = 250;
        //        Serial.println();
        //        Serial.println("I'm still 250 swifty");
        //        Serial.println();
      }
      packetAmount = diff / 5;
      myserial.print("radio tx ");
      Serial.print("radio tx ");
      startPacket();
      myserial.println();
      myserial.println(packetAmount, HEX);
      myserial.println(msg, HEX);
      myserial.println("test over");


      //      Serial.println();
      //      Serial.print("Packet Amount:");
      //      Serial.print(packetAmount);
      //      Serial.println();
      flagRoll = 1;
      x = j;
      while (flagRoll != 0) {
        if ( j >= (diff + x) ) {
          flagRoll = 0;
        }
        else {
          if (j == eeSpace) {
            diff = diff - j + x;
            x = 0;
            j = 0;
          }
          //          Serial.println("for loop j: ");
          //          Serial.println(j, DEC);
          YM = EEPROM.read(j);
          DH = EEPROM.read(j + 1);
          Hm = EEPROM.read(j + 2);
          data[0] = EEPROM.read(j + 3);
          data[1] = EEPROM.read(j + 4);
          buildMessage();
          j = j + 5;
        }
      }
      //      Serial.println();
      //      Serial.println(diff, DEC);
      //      Serial.println();
      diff = abs(wb - j);
      flagRoll = 0;
      Serial.println();            //Data sent
      delay(2000);
    }                             //END OF WHILE LOOP DIF!=0
    rb = wb;
    EEPROM.write((rb), 255);
    EEPROM.write((rb + 1), 254);
    packetAmount = 0;
  }

  else {
    //    Serial.println("Nothing new to send");
  }
}
//
//void gpsRead() {
//  char kmph[8] = {};
//
//  char ident[6] = {}; //Identifier
//  char latit[10] = {};
//  char longit[11] = {};
//  char gpsTime[6] = {};
//  char gpsDate[6] = {};
//  char altit[8] = {};     //format: 1039.5
//  byte sec = 0, Hour = 0, Min = 0, Day = 0, Month = 0, Year = 0;
//  byte temp1 = 0;
//
//  if(gpsSerial.isListening()){
//    digitalWrite(13, HIGH);
//  }
//  while (gpsSerial.available()>0) {
//    myserial.println("i am alive");
//    gpsSerial.readBytesUntil(',', ident, 7);
//
//    if (strcmp(ident, "$GNGGA") == 0) {
//      gpsSerial.readStringUntil(',');
//      gpsSerial.readStringUntil(',');
//      gpsSerial.readStringUntil(',');
//      gpsSerial.readStringUntil(',');
//      gpsSerial.readStringUntil(',');
//      gpsSerial.readStringUntil(',');
//      gpsSerial.readStringUntil(',');
//      gpsSerial.readStringUntil(','); //Ready to read altitude
//
//      temp1 = gpsSerial.readBytesUntil(',', altit, 8);
//      altit[temp1] = '\0';
//      gpsSerial.readStringUntil('\n');
//    }
//
//    else if (strcmp(ident, "$GNRMC") == 0) {
//      /*Time from GPS*/
//      gpsSerial.readBytesUntil('.', gpsTime, 6);
//      Hour = ((gpsTime[0] - 48) * 10) + (gpsTime[1] - 46);
//      if (Hour == 24) {
//        Hour = 0;
//      }
//      if (Hour == 25) {
//        Hour = 1;
//      }
//      Min = ((gpsTime[2] - 48) * 10) + (gpsTime[3] - 48);
//      sec = ((gpsTime[4] - 48) * 10) + (gpsTime[5] - 48);
//      gpsSerial.readStringUntil(',');
//      gpsSerial.readStringUntil(',');
//      /*Latitude from GPS, S/N at the end*/
//      gpsSerial.readBytesUntil(',', latit, 10);
//      latit[9] = gpsSerial.read();
//      gpsSerial.read();
//      /*Longitude */
//      gpsSerial.readBytesUntil(',', longit, 11);
//      longit[10] = gpsSerial.read();
//      gpsSerial.read();
//      /*Speed (Default is knots)*/
//      gpsSerial.readBytesUntil(',', kmph, 8);
//
//      gpsSerial.readStringUntil(',');
//      /*Get Date from GPS*/
//      gpsSerial.readBytesUntil(',', gpsDate, 7);
//      Day = ((gpsDate[0] - 48) * 10) + (gpsDate[1] - 48);
//      Month = ((gpsDate[2] - 48) * 10) + (gpsDate[3] - 48);
//      Year = (gpsDate[5] - 48);
//      gpsSerial.readStringUntil('\n');
//
//      /*Send Date & Time from GPS*/
//      timeEncrypt(Year, Month, Day, Hour, Min);
//      hexCheck(YM);
//      hexCheck(DH);
//      hexCheck(Hm);
//      hexCheck(sec);
//
//      /*Send Latitude from GPS*/
//      int i = 0;
//      while (i < strlen(latit) - 1) {
//        if (i == 4) {
//          i = 5;
//        }
//        temp1 = latit[i + 1] - 48;
//        temp1 = temp1 | ((latit[i] - 48) << 4);
//        hexCheck(temp1);
//        i = i + 2;
//      }
//      hexCheck(latit[9]);
//      /*Send Longitude from GPS*/
//      i = 0;
//      while (i < strlen(longit) - 1) {
//        if (i == 4) {
//          temp1 = longit[i + 2] - 48;
//          temp1 = temp1 | ((longit[i] - 48) << 4);
//          i++;
//        }
//        else if (i == 9) {
//          temp1 = longit[i] - 48;
//        }
//        else {
//          temp1 = longit[i + 1] - 48;
//          temp1 = temp1 | ((longit[i] - 48) << 4);
//        }
//        i = i + 2;
//        hexCheck(temp1);
//      }
//      hexCheck(longit[10]);
//
//      /*Send Altitude from GPS*/
//      i = 0;
//      while (altit[i] != '\0') {
//        if (altit[i] == '.') {
//          hexCheck(altit[i+1] - 48);
//          i = i + 2;
//        }
//        else if (altit[i + 1] == '.') {
//          temp1 = altit[i + 2] - 48;
//          temp1 = temp1 | ((altit[i] - 48) << 4);
//          hexCheck(temp1);
//          i = i + 3;
//        }
//        else {
//          temp1 = altit[i + 1] - 48;
//          temp1 = temp1 | ((altit[i] - 48) << 4);
//          hexCheck(temp1);
//          i = i + 2;
//        }
//      }
//    }
//
//    else {
//      gpsSerial.readStringUntil('\n');
//    }
//  }
//
//}
//

