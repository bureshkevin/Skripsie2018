import PyLora
import time
import datetime
import mysql.connector
from mysql.connector import Error

from sqlite_functionsOct11 import lora_sqlite, lora_my, query_mySQL

class piLora(object):
    
    def __init__(self):
        PyLora.init()
        PyLora.set_sync_word(0x28)
        PyLora.set_spreading_factor(7)
        PyLora.set_frequency(868000000)
        self.stop_listen = False
        self.stop_send=True
        self.lite=lora_sqlite()
        self.my=lora_my()
        self.updateNodes=True
        self.hub=1
        self.msg=0
        self.node=0
        self.node_list=[]
        self.designa='Default Designation'
        self.descrip='Default Description'
        self.updateMy=False
        self.field=False;
        self.ft=False;
        
    def mySqlUpload(self):
        while True:
            time.sleep(1)
            if self.updateMy:
                print 'accepted click'
                self.lite.connect_lite('lora')
                data=self.lite.pull_data()
                self.lite.close_lite()
                print'local is a-okay'
                self.my.connect_mySQL()
                print'i connected in listen'
                self.my.update_mySQL(data)
                print 'i updated in listen'
                self.my.close_mySQL()
                print 'i closed in listen'
                self.updateMy=False
                print'im done in listen'
            if self.field:
                time.sleep(2)
                if self.node is 1:
                    self.node=3
                else:
                    self.node=1
                self.ft=True
        

    def listen(self):
        timeStamp = [0, 0, 0, 0, 0, 0]
        value = [0]
        valueTemp = 0
        date = [datetime.datetime(2012, 03, 29, 11, 30, 0, 0, None)]
        ID = 0
        self.msg=0
        self.ft=False;
        while not self.stop_listen:
            PyLora.receive()
            while not PyLora.packet_available():
                time.sleep(0.5)

                if self.updateNodes:
                    self.lite.connect_lite('lora')
                    list_temp=self.lite.pull_devices(self.updateNodes)
                    x=0
                    for i in list_temp:
                        self.node_list.append(list_temp[x][0])
                        x=x+1
                    self.lite.close_lite()
                    self.updateNodes=False
                if not self.stop_send:
                  #####     Include check for if node is on the list        #####
                ############     Add full self.node (first and last byte)        #############                   
                    print
                    if self.msg is 3:
                        message=[self.hub,0,self.node,self.msg,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]#,26,27,28]#,29,30]
                        print '{}'.format(message)
                        PyLora.send_packet(message)
                    else:
                        message=[self.hub,0,self.node, self.msg]
                        print '{}'.format(message)
                        PyLora.send_packet(message)
                    self.stop_send=True
                    PyLora.receive()
                if self.ft:
                    self.msg=5
                    print"Entering Field Test LoRa Code:  "
                    message=[self.hub, 0, self.node, self.msg]
                    print 'Node {} Message: {}' .format(self.node, message)
                    PyLora.send_packet(message)
                    PyLora.receive()
                    self.ft=False;
                    

            rec = PyLora.receive_packet()
            ########  Time Decryption  #########
            ID=0
            self.msg=0
            print'message size: {}' .format(len(rec))
            print'raw LoRa packet:'
            for i in range (0, len(rec)):
                print'{} ' .format(rec[i]),
            if(len(rec)>4):
                ID = (rec[0]<<8)                                 #ID
                ID = (ID | rec[1])                              #ID
                self.msg = rec[2]
                packetAmount = rec[3]                       #Number of packets sent
                numPackets=packetAmount*5
                value=[]
                print''
                print 'ID: {} and msg: {}' .format(ID, self.msg)

                if ID in self.node_list and (self.msg==0 or self.msg==1 or self.msg==2 or self.msg==3 or self.msg==5):
                    
                    if self.msg==0:
                        print'Node #: {}' .format(ID)
                        print'Msg type: {}' .format(self.msg)
                        print'Number of packets: {} ' .format(packetAmount)
                        for i in range (0,numPackets, 5):
                            timeStamp[0] = (rec[4+i]>>4)                     #Year
                            timeStamp[1] = (rec[4+i]&0b00001111)             #Month
                            timeStamp[2] = (rec[5+i]>>3)                     #Day
                            timeStamp[3] = ((rec[5+i]<<2) & 0b00011100)     #Hour
                            timeStamp[3] = (timeStamp[3] | (rec[6+i]>>6))   #Hour
                            timeStamp[4] = (rec[6+i] & 0b00111111)        #Minutes
                            valueTemp = (rec[7+i]<<8)
                            valueTemp = (valueTemp | (rec[8+i]))
                            value.append(valueTemp)
                            print 'Y:{} M:{} D:{} H:{} m:{}' .format(timeStamp[0], timeStamp[1], timeStamp[2], timeStamp[3], timeStamp[4])
                            print 'Data: {}' .format(value[i/5])

                    elif self.msg==3:
                        print'Node #: {}' .format(ID)
                        print'Msg type: {}' .format(self.msg)
                        print'Number of packets: {} ' .format(packetAmount)
                        if len(rec) >= 7:
                            print'package: {}{}{}' .format(rec[4], rec[5], rec[6])
                            snr=rec[5]
                            i=6
                            while i < len(rec):
                                snr=snr*10 + rec[i]
                                i=i+1
                            if rec[4]==45:
                                snr=-snr
                            print'snr: {}' .format(snr)
                        else:
                            snr=rec[5]
                            i=6
                            while i < len(rec):
                                snr=snr*10 + rec[i]
                                i=i+1
                            if rec[4]==45:
                                snr=-snr
                            print'snr: {}' .format(snr)
                            print'Message not very big'
                    elif self.msg==5:
                        if ID ==1:
                            date=[]
                            print'Field Test Message: '
                            print'Number of packets: {} ' .format(packetAmount)
                            timeStamp[0] = (rec[4]>>4)                     #Year
                            timeStamp[1] = (rec[4]&0b00001111)             #Month
                            timeStamp[2] = (rec[5]>>3)                     #Day
                            timeStamp[3] = ((rec[5]<<2) & 0b00011100)     #Hour
                            timeStamp[3] = (timeStamp[3] | (rec[6]>>6))   #Hour
                            timeStamp[4] = (rec[6] & 0b00111111)        #Minutes
                            timeStamp[5] = rec[7]
                            print 'Y:{} M:{} D:{} H:{} m:{} s:{}' .format(timeStamp[0], timeStamp[1], timeStamp[2], timeStamp[3], timeStamp[4], timeStamp[5])
                            latit=((rec[8]>>4)*1000)
                            latit=latit+((rec[8]&0b00001111)*100)
                            latit=latit+((rec[9]>>4)*10)
                            latit=latit+(rec[9]&0b00001111)
                            latit=latit+(float((rec[10]>>4))/10)
                            latit=latit+(float((rec[10]&0b00001111))/100)
                            latit=latit+(float((rec[11]>>4))/1000)
                            latit=latit+(float((rec[11]&0b00001111))/10000)
                            direLat=rec[12]
                            print'latitude: {}{}' .format(latit, chr(direLat))
                            longit=((rec[13]>>4)*10000)
                            longit=longit+((rec[13]&0b00001111)*1000)
                            longit=longit+((rec[14]>>4)*100)
                            longit=longit+((rec[14]&0b00001111)*10)
                            longit=longit+((rec[15]>>4))
                            longit=longit+(float((rec[15]&0b00001111))/10)
                            longit=longit+(float((rec[16]>>4))/100)
                            longit=longit+(float((rec[16]&0b00001111))/1000)                        
                            longit=longit+(float(rec[17])/10000)
                            direLon=rec[18]
                            print'longitude: {}{}' .format(longit, chr(direLon))
                            size=len(rec)
                            print('size of lora msg: {}') .format(size)
                            size=size-19
                            i=0
                            while True:
                                print'{}' .format(rec[i+19])
                                i=i+1
                                if rec[i+19] == 44:
                                    break
                                if i == size:
                                    break
                            size=i
                            print'i={} size={}' .format(i, size)
                            altit=(float((rec[18+size]&0b00001111))/10)
                            if (rec[18+size]>9):
                                altit=altit+(rec[18+size]>>4)
                                double=True
                            else:
                                double=False
                            size=size-1
                            if size == 2:
                                if double:
                                    altit=altit+((rec[18+size]&0b00001111)*10)
                                    altit=altit+((rec[18+size]>>4)*100)
                                    size=size-1
                                    altit=altit+((rec[18+size]&0b00001111)*1000)
                                    altit=altit+((rec[18+size]>>4)*10000)
                                else:
                                    altit=altit+((rec[18+size]&0b00001111))
                                    altit=altit+((rec[18+size]>>4)*10)
                                    size=size-1
                                    altit=altit+((rec[18+size]&0b00001111)*100)
                                    altit=altit+((rec[18+size]>>4)*1000)
                                size=0
                            if size == 1:
                                if double:
                                    altit=altit+((rec[18+size]&0b00001111)*10)
                                    altit=altit+((rec[18+size]>>4)*100)
                                    size=size-1
                                else:
                                    altit=altit+((rec[18+size]&0b00001111))
                                    altit=altit+((rec[18+size]>>4)*10)
                                    size=size-1
                            print'altit: {}' .format(altit)
                            size=19+i+1
                            rssi=rec[size+1]
                            if rec[size] == 45:
                                rssi=-rssi
                            size = size+4
                            snr = rec[size]
                            if rec[size-1] == 45:
                                snr=-snr
                                snr=snr - float(rec[size+1])/10
                                snr=snr - float(rec[size+2])/100
                            else:
                                snr=snr + float(rec[size+1])/10
                                snr=snr + float(rec[size+2])/100
                            localRssi=PyLora.packet_rssi()
                            localSnr=PyLora.packet_snr()
                            print'Received: Rssi: {}  Snr: {}' .format(rssi, snr)
                            print'Local: Rssi: {} Snr: {}' .format(localRssi, localSnr)
                            print'last latitude test... {}' .format(latit)
                            self.lite.connect_lite('lora')
                            date.append(datetime.datetime(
                                (2010+timeStamp[0]), timeStamp[1], timeStamp[2],
                                timeStamp[3], timeStamp[4], timeStamp[5])) 
                            self.lite.field_lite(date[0], ID, localRssi, localSnr,
                                                 latit, direLat, longit, direLon,
                                                 altit, rssi, snr)
                            self.lite.close_lite()
                        elif ID ==3:
                            print'id 3'
                            snr=rec[5]
                            i=6
                            while i < len(rec):
                                snr=snr*10 + rec[i]
                                i=i+1
                            if rec[4]==45:
                                snr=-snr
                            rssi=0
                            localRssi=PyLora.packet_rssi()
                            localSnr=PyLora.packet_snr()
                            print'Received: Rssi: {}  Snr: {}' .format(rssi, snr)
                            print'Local: Rssi: {} Snr: {}' .format(localRssi, localSnr)
                            print'last latitude test... {}' .format(latit)
                            self.lite.connect_lite('lora')
                            self.lite.field_lite(date[0], ID, localRssi, localSnr,
                                                 latit, direLat, longit, direLon,
                                                 altit, 0, 0)
                            self.lite.close_lite()
                    elif self.msg==1:
                        date=[]
                        self.lite.connect_lite('lora')
                        print'# of packets {}' .format(numPackets)
                        for i in range (0,numPackets, 5):
                            timeStamp[0] = (rec[4+i]>>4)                     #Year
                            timeStamp[1] = (rec[4+i]&0b00001111)             #Month
                            timeStamp[2] = (rec[5+i]>>3)                     #Day
                            timeStamp[3] = ((rec[5+i]<<2) & 0b00011100)     #Hour
                            timeStamp[3] = (timeStamp[3] | (rec[6+i]>>6))   #Hour
                            timeStamp[4] = (rec[6+i] & 0b00111111)        #Minutes
                            valueTemp = (rec[7+i]<<8)
                            valueTemp = (valueTemp | (rec[8+i]))
                            value.append(valueTemp)

                            date.append(datetime.datetime((2010+timeStamp[0]), timeStamp[1], 
                                                 timeStamp[2], timeStamp[3], timeStamp[4])) 
                            self.lite.update_data_lite(date[i/5], ID, value[i/5])
                        self.lite.close_lite()
                    elif self.msg==2:
                        try:
                            connection = mysql.connector.connect(**setup)
                            if connection.is_connected():
                                db_Info = connection.get_server_info()
                                print("Connected to MySQL database... MySQL Server version on ", db_Info)
                                cursor = connection.cursor()
                                cursor.execute("select database();")
                                record = cursor.fetchone()
                                print("Your connected to - ", record)
                        except Error as e:
                            print("Error while connecting to MySQL", e)

                        cursor = connection.cursor()
                        for i in range (0,numPackets, 5):
                            timeStamp[0] = (rec[4+i]>>4)                     #Year
                            timeStamp[1] = (rec[4+i]&0b00001111)             #Month
                            timeStamp[2] = (rec[5+i]>>3)                     #Day
                            timeStamp[3] = ((rec[5+i]<<2) & 0b00011100)     #Hour
                            timeStamp[3] = (timeStamp[3] | (rec[6+i]>>6))   #Hour
                            timeStamp[4] = (rec[6+i] & 0b00111111)        #Minutes
                            valueTemp = (rec[7+i]<<8)
                            valueTemp = (valueTemp | (rec[8+i]))
                            value.append(valueTemp)
                            date.append(datetime.datetime((2010+timeStamp[0]), timeStamp[1], 
                                                         timeStamp[2], timeStamp[3], timeStamp[4])) 
                            insert_sensor_data = ("INSERT INTO Data1" "(Value, SensorID, timeRecorded)" "VALUES (%s, %s, %s)")
                            sensor_data = (value[i/5], ID, date[i/5])

                            cursor.execute(insert_sensor_data, sensor_data)
                            connection.commit()
                            
                        # closing database connection.
                        if (connection.is_connected()):
                            cursor.close()
                            connection.close()
                            print("MySQL connection is closed")
                
                else:

                    print 'Uknown device trying to upload data. . .'
            else:
                print 'Uknown device defeated by if statement'
        print'Stop Listening'
