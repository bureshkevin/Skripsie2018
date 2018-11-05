#include <EEPROM.h>
#include <SPI.h>
#include <LoRa.h>
#include <TimeLib.h>
#include <SoftwareSerial.h>

#define eesize 1024
#define csPin 10
#define resetPin A0
#define gpsTx 6
#define gpsRx 5
#define irqPin 2
#define eeSpace 1020

SoftwareSerial gpsSerial(gpsRx, gpsTx);

uint8_t mode=0;
uint8_t packetSize=0;

uint8_t Hub = 0;
uint16_t recID = 0;
uint8_t msgRec = 0;

//LoRa Variables
uint16_t ID = 1;           //ID of Node
uint8_t msg = 0;               //Type of message being sent
uint8_t packetAmount = 0;     //Number of packets
uint8_t YM = 0;               //Year & Month byte (listed in that order)
uint8_t DH = 0;              //Day & Hour byte (listed in that order)
uint8_t Hm = 0;             //Hour & Minute byte
uint8_t data[] = {0, 0};    //Data bytes





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


char cmd;
int counter = 0;
int cOld = 2;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  while (!Serial);
  gpsSerial.begin(9600);

  eepromAddress();
  Serial.println("Previous Data:");
  Serial.println("# of Packets:");
  Serial.print(packetAmount, DEC);
  Serial.println("Read & Write byte: ");
  Serial.print(rb, DEC);
  Serial.println(wb, DEC);


  Serial.print("LoRa Mini #");
  Serial.println(ID);
  if (!LoRa.begin(868E6)) {
    Serial.println("LoRa has failed to start");
    while (true);
  }
  LoRa.setSyncWord(0x28);
  LoRa.setSpreadingFactor(7);

  pinMode(9, OUTPUT);
}


void eepromAddress() {                   //Only access EEPROM from 0 - 1019
  mode=EEPROM.read(EEPROM.length()-1);
  if(mode==0){
	packetSize=15;
  }
  else{
	packetSize=5;
  }
  for (int i = 0; i < eeSpace; i = i + packetSize) { //Only need to read up to 1015 as that accounts for bytes up to 1019
    eevalue = EEPROM.read(i);
    if (eevalue == 255) {
      rb = i;
    }
    Serial.println((i), DEC);
    Serial.println(eevalue, DEC);
    eevalue = EEPROM.read((i + 1));
    if (eevalue == 254) {
      wb = i;
    }
  }

  if (wb == 0) {
    wb = rb;
  }
  else if (wb >= rb) {
    packetAmount = abs(wb - rb) / packetSize;
  }
  else {
    packetAmount = abs(wb - rb);
    packetAmount = (eeSpace - packetAmount) / packetSize;
  }
}


void eepromUpdate() {
  if (wb == eeSpace) {
    flagRoll = 1;
    wb = 0;
  }
  if (!flagRoll || (flagRoll && (wb!=rb))) {
	if(mode!=0){
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
    }
	else{							//Currently 15 (4+1+5+1+4) = (long,dir,lat,dir,datetime)
	  if(wb+packetSize>=eeSpace){
		flagRoll=1;
		wb=0;
	  }
	  gpsRead();
	}
	packetAmount++;
	
  }
  else {
    Serial.println("Losing new data");
  }
}


void dataSplit() {
  byte Year = 0, Month = 0, Day = 0, Hour = 0, Min = 0;
  if(mode!=0){
	  for (int i = 0; i < (sizeof(Data) / 2); i++) {
		Year = (timeStamp[i] / 100) % 10;
		Month = (timeStamp[i] % 100);
		Day = int((stamp[i] / 1E4));
		Hour = (stamp[i] / 100) % 100;
		Min = (stamp[i] % 100);

		timeEncrypt(Year, Month, Day, Hour, Min);
		data[0] = Data[i] >> 8;
		data[1] = (Data[i] & 0b0000000011111111);
		eepromUpdate();
	  }
  }
  else{
	eepromUpdate();
  }
  if (rb != wb) {
    EEPROM.update((wb + 1), 254);
  }
}

void timeEncrypt(byte Year, byte Month, byte Day, byte Hour, byte Min) {
  YM = byte(Month);
  YM = YM | (byte(Year) << 4);


  Hm = byte(Min);
  Hm = Hm | (byte(Hour) << 6);

  DH = byte(Hour >> 2);
  DH = DH | (byte(Day) << 3);
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
        Serial.println();
        Serial.println("I'm still 250 swifty");
        Serial.println();
      }
      packetAmount = diff / packetSize;
      LoRa.beginPacket();
      LoRa.write((ID >> 8));
      LoRa.write((ID & 0b0000000011111111));
      LoRa.write(msg);
      LoRa.write(packetAmount);     // # of data packets to send (essentially total size of message)
      Serial.println();
      Serial.print("Packet Amount:");
      Serial.print(packetAmount);
      Serial.println();
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
          Serial.println("for loop j: ");
          Serial.println(j, DEC);
		  for(int i=0; i<packetSize; i++){
		    LoRa.write(EEPROM.read(j+i));
		  }
          j = j + packetSize;
        }
      }
      Serial.println();
      Serial.println(diff, DEC);
      Serial.println();
      diff = abs(wb - j);
      flagRoll = 0;
      LoRa.endPacket();            //Data sent
      delay(2000);
    }                             //END OF WHILE LOOP DIF!=0
    rb = wb;
    EEPROM.write((rb), 255);
    EEPROM.write((rb + 1), 254);
    packetAmount = 0;
  }

  else {
    Serial.println("Nothing new to send");
  }
}

void receiveMessage(int msgSize) {
  if (msgSize == 0)  return;
  Serial.println("Message Received loud and clear");
  uint8_t loramsg[msgSize];
  uint8_t pack = 0;
  Serial.print("LoRa Message Received: ");
  while (LoRa.available()) {
    loramsg[pack] = LoRa.read();
    Serial.print(loramsg[pack]);
    pack++;
  }
  Serial.println();
  Serial.print("RSSI: ");
  Serial.println(LoRa.packetRssi());
  Serial.print("Snr: ");
  Serial.println(LoRa.packetSnr());

  Hub = loramsg[0];
  recID = ((loramsg[1]) << 8);
  recID = (recID | (loramsg[2]));

  if (Hub == 1 && recID == ID) {
    msgRec = loramsg[3];
    switch (msgRec) {
	  case 0:
		if(msgSize>5){
          if(loramsg[5]==0){			
		    modeChange(loramsg[4], false);
		  }
		  else if(loramsg[5] == 1){
			modeChange(loramsg[4], true);
		  }
		}
	    break;
      case 3:					
        Serial.println("All good");
        digitalWrite(9, HIGH);
        msg = 3;
        packetAmount = 7;
        LoRa.beginPacket();
        LoRa.write((ID >> 8));
        LoRa.write((ID & 0b0000000011111111));
        LoRa.write(msg);
        LoRa.write(packetAmount);     // # of data packets to send (essentially total size of message)
        LoRa.write(9);
        LoRa.write(1);
        LoRa.write(1);
        LoRa.endPacket();
        delay(500);
        break;
      case 1:					//Send data Stored in EEPROM
        Serial.println(msg);
        Serial.println("case 1");
        LoRaSend();
        break;
      case 2:
        msg = 0;				//Add data to EEPROM
        Serial.println("case 2");
        dataSplit();
		break;
      case 5:					//Field Test Operations (Reception Mapper)
        digitalWrite(9, HIGH);
        packetAmount = 22;
//        Serial.println("Test field message sendback loop");
        msg = 5;
        LoRa.beginPacket();
        LoRa.write((ID >> 8));
        LoRa.write((ID & 0b0000000011111111));
        LoRa.write(msg);
        LoRa.write(packetAmount);     // # of data packets to send (essentially total size of message)
        digitalWrite(9, LOW);
        gpsRead();

        //        while(snr[j]!='\0'){
        //          hexCheck(snr[j])
        //        }
        digitalWrite(9, HIGH);
        Serial.println("Ending packet...");
        LoRa.endPacket();
        delay(500);
        break;
    }
  }

}


void loop() {
  // put your main code here, to run repeatedly:
  if (cOld != counter) {
    Serial.print("Packets sent: #");
    Serial.print(counter, DEC);
    Serial.println();
  }
  cOld = counter;

  receiveMessage(LoRa.parsePacket());
  digitalWrite(9, LOW);

  if (Serial.available()) {
    cmd = Serial.read();
    switch (cmd) {
      case 'w':
        dataSplit();
        break;

      case 's':
        Serial.println("Sending LoRa #: ");
        Serial.print(counter, DEC);
        LoRaSend();
        counter++;
        break;

      case 'i':
        if (ID == 1) {
          ID = 3;
        }
        else {
          ID = 1;
        }
        Serial.println("ID= ");
        Serial.println(ID, DEC);
        break;

      case 'm':
        Serial.println(msg, DEC);
        msg = 2;
        break;

      case 'l':
        msg = 1;
        Serial.println(msg, DEC);
        break;

      case 'p':
        msg = 0;
        Serial.println(msg, DEC);
        break;

      case 'r':
        for (int i; i < 1024; i++) {
          Serial.println(EEPROM.read(i), DEC);
        }
        Serial.print(rb, DEC);
        Serial.println(wb, DEC);
        break;
    }
  }


}

void modeChange(uint8_t value, bool send){
  if(send){
    LoRaSend();
  }
  EEPROM.update((EEPROM.length()-1), value);
  if(mode==0){
	packetSize=15;
  }
  else{
	packetSize=5;
  }
  wb=0;
  rb=0;
}

void modeWrite(uint8_t value){
  if(mode==0){
	EEPROM.update(wb, value);
	wb++;
  }
  else{
	LoRa.write(value);
  }
}


void gpsRead() {
  char gpsinput[200] = {};
  char ident[7] = {}, altit[8] = {}, latit[11] = {}, longit[12] = {}, gpsTime[7] = {}, gpsDate[7] = {};
  bool Stop, gga = false, rmc = false;
  byte sec = 0, Hour = 0, Min = 0, Day = 0, Month = 0, Year = 0, temp1 = 0;
  int i, s;
  int rssi = LoRa.packetRssi();
  float snr = LoRa.packetSnr();
  while (!rmc || !gga) {
    while (gpsSerial.available()) {
      if (!rmc || !gga) {
        s = gpsSerial.readBytesUntil('\n', gpsinput, 200);
        gpsinput[s] = '\0';
        for (int i = 0; i < 6; i++) {
          ident[i] = gpsinput[i];
        }
        ident[6] = '\0';
      }
      else {
        /*Time & Date from GPS*/
        Hour = ((gpsTime[0] - 48) * 10) + (gpsTime[1] - 46);
        if (Hour == 24) {
          Hour = 0;
        }
        if (Hour == 25) {
          Hour = 1;
        }
        Min = ((gpsTime[2] - 48) * 10) + (gpsTime[3] - 48);
        sec = ((gpsTime[4] - 48) * 10) + (gpsTime[5] - 48);
        Day = ((gpsDate[0] - 48) * 10) + (gpsDate[1] - 48);
        Month = ((gpsDate[2] - 48) * 10) + (gpsDate[3] - 48);
        Year = (gpsDate[5] - 48);
        /*Send Date & Time from GPS*/
        timeEncrypt(Year, Month, Day, Hour, Min);
		
        modeWrite(YM);
        modeWrite(DH);
        modeWrite(Hm);
        modeWrite(sec);
		/*Send Latitude from GPS*/
        i = 0;
        while (i < strlen(latit) - 1) {
          if (i == 4) {
            i = 5;
          }
          temp1 = latit[i + 1] - 48;
          temp1 = temp1 | ((latit[i] - 48) << 4);
          modeWrite(temp1);
          i = i + 2;
        }

		modeWrite(latit[9]);
        /*Send Longitude from GPS*/
        i = 0;
        while (i < strlen(longit) - 1) {
          if (i == 4) {
            temp1 = longit[i + 2] - 48;
            temp1 = temp1 | ((longit[i] - 48) << 4);
            i++;
          }
          else if (i == 9) {
            temp1 = longit[i] - 48;
          }
          else {
            temp1 = longit[i + 1] - 48;
            temp1 = temp1 | ((longit[i] - 48) << 4);
          }
          i = i + 2;
		  modeWrite(temp1);
        }
		
        modeWrite(longit[10]);

        /*Send Altitude from GPS*/
		if(mode!=0){
			i = 0;
			while (altit[i] != '\0') {
			  if (altit[i + 1] != '\0') {
				temp1 = altit[i + 1] - 48;
				temp1 = temp1 | ((altit[i] - 48) << 4);
				LoRa.write(temp1);
				i = i + 2;
			  }
			  else {
				LoRa.write(altit[i] - 48);
				i++;
			  }
			}
			LoRa.write(',');
			if (rssi < 0) {
			  LoRa.write('-');
			}
			else {
			  LoRa.write('+');
			}
			LoRa.write(abs(rssi));
			LoRa.write(',');
			if (snr < 0) {
			  LoRa.write('-');
			}
			else {
			  LoRa.write('+');
			}
			LoRa.write(abs(int(snr)));
			temp1 = abs(snr * 10) % 10;
			LoRa.write(temp1);

			temp1 = abs(snr * 100) % 10;
			LoRa.write(temp1);
	//        Serial.println(temp1);
	//        Serial.println("results");
	//        Serial.println(gpsTime);
	//        Serial.println(gpsDate);
	//        Serial.println(latit);
	//        Serial.println(longit);
	//        Serial.println(altit);
		}
        break;

      }
      if (strcmp(ident, "$GNGGA") == 0) {
        Stop = false;
        i = 7;
        while (!Stop) {
          gpsTime[i - 7] = gpsinput[i];
          if (gpsTime[i - 7] == '.') {
            Stop = true;
            gpsTime[i - 7] = '\0';
          }
          i++;
        }
        Stop = false;
        i = 18;
        while (!Stop) {
          latit[i - 18] = gpsinput[i];
          if (latit[i - 18] == ',') {
            Stop = true;
            latit[i - 18] = gpsinput[i + 1];
            latit[i - 17] = '\0';
          }
          i++;
        }
        i = 30;
        Stop = false;
        while (!Stop) {
          longit[i - 30] = gpsinput[i];
          if (longit[i - 30] == ',') {
            Stop = true;
            longit[i - 30] = gpsinput[i + 1];
            longit[i - 29] = '\0';
          }
          i++;
        }
        Stop = false;
        i = 52;
        while (!Stop) {
          altit[i - 52] = gpsinput[i];
          if (altit[i - 52] == '.') {
            altit[i - 52] = gpsinput[i + 1];
            Stop = true;
            altit[i - 51] = '\0';
          }
          i++;
        }
        gga = true;

      }
      else if (strcmp(ident, "$GNRMC") == 0) {
        i = 0;
        int rm = 0;
        int place = 0;
        Stop = false;
        while (!Stop) {
          if (gpsinput[i] == ',') {
            rm++;
            if (rm == 9) {
              rm++;
              i++;
              place = i;
            }
            if (rm == 11) {
              gpsDate[i - place] = '\0';
              Stop = true;
            }
          }
          if (rm == 10) {
            gpsDate[i - place] = gpsinput[i];
          }
          i++;
        }
        rmc = true;
      }
    }
  }
}



