import sqlite3
import datetime


setup = {
    'host': 'db4free.net',
    'database': 'skripsie2018',
    'user': 'kevinb',
    'password': 'finalyear1'
}
##
now=datetime.datetime(2012, 03, 29, 11, 30, 0, 0, None)
sensor=1
value=500

##
con = sqlite3.connect('lora.db')
c = con.cursor()

choice=int(raw_input('Choose 0 for Local Database or 1 for MySQL Database:'))

if choice is 0:
	print("Operations available Below:")
	print("Press 0 to create Data Table")
	print("Or 1 to create Device Table")
	print("Or 2 to create fieldTest Table")

	print("Or 3 to query Data Table")
	print("Or 4 to query Device Table")
	print("Or 5 to query fieldTest Table")

	choice=int(raw_input('What would you like to perform?:'))

	if choice is 0:
		c.execute('''CREATE TABLE Data
			   (ID integer primary key autoincrement, timeRecorded ts, SensorID integer, Value integer, foreign key(SensorID) references Device(Serial))''')
	elif choice is 2:
		c.execute('''CREATE TABLE fieldTest
					(ID integer primary key autoincrement, timeRecorded ts, SensorID integer,
					localRssi integer, localSnr real, latit real, direLat varchar(1), longit real,
					direLon varchar[1], altit real, rssi integer, snr real, foreign key(SensorID) references Device(Serial))''')
	elif choice is 1:
		c.execute('''CREATE TABLE Device
					(ID integer primary key autoincrement, Designation varchar(255), Description text, Serial integer UNIQUE)''')
	elif choice is 3:
		c.execute("select * from Data")
		a=list(c.fetchall())
		print a
	elif choice is 4:
		c.execute("select * from Device")
		a=list(c.fetchall())
		print a
	elif choice is 5:
		c.execute("select * from fieldTest")
		a=list(c.fetchall())
		print a
elif choice is 1:
	print 'connect_mySQL called'
	


con.commit()
con.close()


##c.execute("INSERT INTO Data (timeRecorded, SensorID, Value) VALUES (?, ?, ?)", (now, sensor, value))
##
##c.execute("INSERT INTO Device (Designation, Description, Serial ) VALUES (?, ?, ?)", ("Gate2", "At x2 and y2 coord. near the redwood tree", 2))

##cur = con.cursor()
####
####cur.execute("DELETE FROM Data")
####con.commit()
##

    
##for i in a:
##    if int(i) ==j:
##        print(i)
##    else:
##        print' no print..'
##
##c.execute("drop table Device")


##c.execute("drop table fieldTest")
