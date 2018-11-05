import PyLora
import time
import datetime
import mysql.connector
from mysql.connector import Error

from sqlite_functions10Sept import lora_sqlite, connect_mySQL, update_mySQL, close_mySQL, query_mySQL

class piLora(object):
    
    def __init__(self):
        PyLora.init()
        PyLora.set_frequency(868000000)
        self.stop_listen = False
        self.stop_send=True
        self.kill_send=False
        self.lite=lora_sqlite()
        self.updateNodes=True
        self.hub=1
        self.msg=0
        self.node=0
        self.node_list=[]
    def testNode(self):
        while True:
            time.sleep(2)
            while not self.stop_send:
                message=str(self.hub) + '0' + str(self.node) + '3'
                print '{}'.format(message)
                PyLora.send_packet(message)
                self.stop_send=True
                PyLora.receive()
            if(self.kill_send):
                break
            
        

    def listen(self):
        timeStamp = [0, 0, 0, 0, 0]
        value = [0]
        valueTemp = 0
        date = [datetime.datetime(2012, 03, 29, 11, 30, 0, 0, None)]
        ID = 0
        self.msg=0
        while not self.stop_listen:
            PyLora.receive()
            while not PyLora.packet_available():
                time.sleep(2)
                if self.updateNodes:
                    self.lite.connect_lite('lora')
##                    self.lite.update_device_lite
                    list_temp=self.lite.pull_devices(self.updateNodes)
                    x=0
                    for i in list_temp:
                        self.node_list.append(list_temp[x][0])
                        x=x+1
                    self.updateNodes=False
            rec = PyLora.receive_packet()
            ########  Time Decryption  #########

            
            ID = (rec[0]<<8)                                 #ID
            ID = (ID | rec[1])                              #ID
            self.msg = rec[2]
            packetAmount = rec[3]                       #Number of packets sent
            numPackets=packetAmount*5
            date=[]
            value=[]

            if ID in self.node_list and (self.msg==0 or self.msg==1 or self.msg==2 or self.msg==3):
                
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
                    if(packetAmount==7):
                        print'Node #: {}' .format(ID)
                        print'Msg type: {}' .format(self.msg)
                        print'Number of packets: {} ' .format(packetAmount)
                        print'package: {}{}{}' .format(rec[4], rec[5], rec[6])
                    else:
                        print'Error in receiving packet'

                elif self.msg==1:
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
                elif msg==2:
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
        print'Stop Listening'
