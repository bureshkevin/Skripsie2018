import sqlite3
import mysql.connector
from mysql.connector import Error
import os
import time


setup = {
    'host': 'db4free.net',
    'database': 'skripsie2018',
    'user': 'kevinb',
    'password': 'finalyear1'
}


class lora_sqlite(object):
    def __init__(self):
        self.curDir= os.path.join(os.getcwd(), 'sqlite', 'lora' + '.db')
        self.con=sqlite3.connect(self.curDir)
        self.con.close()
    def connect_lite(self, arg):
        self.curDir= os.path.join(os.getcwd(), 'sqlite', arg + '.db')
        self.con=sqlite3.connect(self.curDir)
    def update_device_lite(self, desig, descr, serial):
        db=self.con.cursor()
        db.execute('INSERT INTO Device (Designation, Description, Serial) VALUES (?,?,?)', (desig, descr, serial))
        self.con.commit()
    def update_data_lite(self, date, ID, value):
        db=self.con.cursor()
        db.execute('INSERT INTO Data (timeRecorded, SensorID, Value) VALUES (?,?,?)', (date, ID, value))
        self.con.commit()
    def field_lite(self, date, ID, localRssi, localSnr, latit, direLat, longit, direLon, altit, rssi, snr):
        db=self.con.cursor()
        db.execute('''INSERT INTO fieldTest (timeRecorded, SensorID, localRssi, localSnr,
                    latit, direLat, longit, direLon, altit, rssi, snr)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                   (date, ID, localRssi, localSnr, latit, direLat, longit, direLon, altit, rssi, snr))
        self.con.commit()
    def pull_devices(self, choice):
        db=self.con.cursor()
        if choice:
            db.execute("select Serial from Device")
        else:
            db.execute("select * from Device")
        device_lite = db.fetchall()
        self.con.close()
        return device_lite
    def pull_data(self):
        db=self.con.cursor()
        db.execute("select * from Data")
        data_lite = db.fetchall()
        self.con.close()
        return data_lite
    def delete_data(self):
        self.curDir= os.path.join(os.getcwd(), 'sqlite', 'lora' + '.db')
        db=self.con.cursor()
        db.execute("DELETE from Data")
        self.con.commit()
        self.con.close()
    def close_lite(self):
        self.con.close()
        
class lora_my(object):
    def __init__(self):
        self.timer=0
        self.connectFlag=False
    
    def connect_mySQL(self):
        print 'connect_mySQL called'
        try:
            self.connection = mysql.connector.connect(**setup)
            print 'about to check if connected'
            if self.connection.is_connected():
                db_Info = self.connection.get_server_info()
                print("Connected to MySQL database... MySQL Server version on ", db_Info)
                self.cursor = self.connection.cursor()
                self.cursor.execute("select database();")
                record = self.cursor.fetchone()
                print("Your connected to - ", record)
                self.connectFlag=True
        except Error as e:
            print("Error while connecting to MySQL", e)
            
    def update_mySQL(self, data):
        self.timer=0
        if not self.connectFlag:
            print 'not initially connected, trying to connect again'
            while self.timer<1:
                if self.connectFlag:
                    break
                self.connect_mySQL()
                time.sleep(5)
                self.timer=self.timer+1
        else:
            print 'connected already'
        if self.connectFlag:
            print 'about to insert. . .'
            for item in data:
                insert_sensor_data = ("INSERT INTO Data" "(timeRecorded, SensorID, Value)" "VALUES (%s, %s, %s)")
                sensor_data = (item[1], item[2], item[3])
                print 'sensor data is: {}' .format(sensor_data)
                self.cursor.execute(insert_sensor_data, sensor_data)
                self.connection.commit()
                
    def close_mySQL(self):
        # closing database connection.
        if (self.connectFlag):
            self.cursor.close()
            self.connection.close()
            self.connectFlag=False
            print("MySQL connection is closed")

def query_mySQL(cur, con):
    connect_mySQL(con)
    cur = con.cursor()
    query = "SELECT " \
        "DeviceTable.ID AS Device, " \
        "DeviceTable.Designation AS Location, " \
        "Data.id AS Entry, Data.Value AS value, " \
        "Data.TimeStamp AS TimeRecord FROM DeviceTable RIGHT JOIN Data ON DeviceTable.ID = Data.SensorID"

    cur.execute(query)
    result=cur.fetchall()

    for x in result:
        print(x)
    close_mySQL(cur, con)
    
