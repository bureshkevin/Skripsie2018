import sqlite3
import mysql.connector
import os


setup = {
    'host': 'db4free.net',
    'database': 'skripsie2018',
    'user': 'kevinb',
    'password': 'finalyear1'
}


class lora_sqlite(object):
    def __init__(self):
        self.curDir= os.path.join(os.getcwd(), 'sqlite', 'LoRa' + '.db')
        self.con=sqlite3.connect(self.curDir)
        self.con.close()
    def connect_lite(self, arg):
        self.curDir= os.path.join(os.getcwd(), 'sqlite', arg + '.db')
        self.con=sqlite3.connect(self.curDir)
    def update_data_lite(self,value, ID, date):
        db=self.con.cursor()
        db.execute('INSERT INTO Data VALUES (?,?,?)', (value, ID, date))
        self.con.commit()
##        con.close()
    def pull_data(self):
        db=self.con.cursor()
        db.execute("select * from Data")
        data_lite = db.fetchall()
        self.con.close()
        return data_lite
    def delete_data(self):
        self.curDir= os.path.join(os.getcwd(), 'sqlite', 'LoRa' + '.db')
        db=self.con.cursor()
        db.execute("DELETE from Data")
        self.con.commit()
        self.con.close()
    def close_lite(self):
        self.con.close()

def connect_mySQL(connection):
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
        
def update_mySQL(cur, con):
    connect_mySQL(con)
    cur = con.cursor()
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
        date.append(datetime.datetime(yearAdd(timeStamp[0]), timeStamp[1], 
                                     timeStamp[2], timeStamp[3], timeStamp[4])) 
        insert_sensor_data = ("INSERT INTO Data1" "(Value, SensorID, timeRecorded)" "VALUES (%s, %s, %s)")
        sensor_data = (value[i/5], ID, date[i/5])

        cur.execute(insert_sensor_data, sensor_data)
        con.commit()

def close_mySQL(cursor, connection):
    # closing database connection.
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

def query_mySQL(cur, con):
    connect_mySQL(con)
    cur = con.cursor()
    query = "SELECT " \
        "DeviceTable.ID AS Device, " \
        "DeviceTable.Designation AS Location, " \
        "Data1.id AS Entry, Data1.Value AS value, " \
        "Data1.TimeStamp AS TimeRecord FROM DeviceTable RIGHT JOIN Data1 ON DeviceTable.ID = Data1.SensorID"

    cur.execute(query)
    result=cur.fetchall()

    for x in result:
        print(x)
    close_mySQL(cur, con)
    
