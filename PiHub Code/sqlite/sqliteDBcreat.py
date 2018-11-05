import sqlite3
import datetime




##
now=datetime.datetime(2012, 03, 29, 11, 30, 0, 0, None)
sensor=1
value=500

##
con = sqlite3.connect('lora.db')
c = con.cursor()

##
##c.execute('''CREATE TABLE Data
##            (ID integer primary key autoincrement, timeRecorded ts, SensorID integer, Value integer, foreign key(SensorID) references Device(Serial))''')


##c.execute('''CREATE TABLE fieldTest
##            (ID integer primary key autoincrement, timeRecorded ts, SensorID integer,
##            localRssi integer, localSnr real, latit real, direLat varchar(1), longit real,
##            direLon varchar[1], altit real, rssi integer, snr real, foreign key(SensorID) references Device(Serial))''')



##c.execute('''CREATE TABLE Device
##            (ID integer primary key autoincrement, Designation varchar(255), Description text, Serial integer UNIQUE)''')

##


##c.execute("INSERT INTO Data (timeRecorded, SensorID, Value) VALUES (?, ?, ?)", (now, sensor, value))
##
##c.execute("INSERT INTO Device (Designation, Description, Serial ) VALUES (?, ?, ?)", ("Gate2", "At x2 and y2 coord. near the redwood tree", 2))

##con.commit()
##
##
##con.close()

##c.execute("ALTER TABLE Device ADD CONSTRAINT UNIQUE (SensorID)")
##
##
##cur = con.cursor()
####
####cur.execute("DELETE FROM Data")
####con.commit()
##
##c.execute("select * from Device")
##a=list(c.fetchall())
##print a
##j=a[0]
##k=a[0][0]
##
##print j
##print k
##x=0
##li=[]
##
##for i in a:
##    print a[x][0]
##    li.append(a[x][0])
##    x=x+1
##
##print'print list'
##print li
##x=0
##while x<len(li):
##    print li[x]
##    x=x+1

    
##for i in a:
##    if int(i) ==j:
##        print(i)
##    else:
##        print' no print..'
##
##c.execute("drop table Device")

c.execute("select * from fieldTest")
a=list(c.fetchall())
print a
##c.execute("drop table fieldTest")

con.commit()
con.close()
