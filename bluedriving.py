#!/usr/bin/python

# TODO
# - Hacer threads para que un thread este todo el tiempo preguntando por los dispositivos alrededor
# standar imports
import sys
import re
import getopt
import copy
import os
import time
import sqlite3
import bluetooth
import time
import gps
from gps import *;
import threading
import getCoordinatesFromAddress
from bluedrivingWebServer import createWebServer

vernum = '0.1'
debug = False
threadbreak = False
database = ""
gps_session= ""
GRE='\033[92m'
END='\033[0m'
RED='\033[91m'
CYA='\033[96m'


def version():
        """
        This function prints information about this utility
        """
	global RED
	global END

        print RED
        print "   "+ sys.argv[0] + " Version "+ vernum +" @COPYLEFT                    "
        print "   Authors: verovaleros, eldraco, nanojaus                               "
        print "   Bluedriver is a bluetooth warwalking utility.                        "
        print 
        print END
 
def usage():
        """
        This function prints the posible options of this program.
        """
        print "+----------------------------------------------------------------------+"
        print "| "+ sys.argv[0] + " Version "+ vernum +"                                      |"
        print "| This program is free software; you can redistribute it and/or modify |"
        print "| it under the terms of the GNU General Public License as published by |"
        print "| the Free Software Foundation; either version 2 of the License, or    |"
        print "| (at your option) any later version.                                  |"
        print "|                                                                      |"
        print "| Author: Veronica Valeros, vero.valeros@gmail.com                     |"
        print "+----------------------------------------------------------------------+"
        print
        print "\nUsage: %s <options>" % sys.argv[0]
        print "Options:"
        print "  -h, --help                           Show this help message and exit."
        print "  -D, --debug                          Debug mode"
        print "  -d, --database                       Name of the database to store the data"
        print "  -w, --webserver                      It runs a local webserver to visualize and interact with the collected information"
	print 
  


# Discovering function
def discovering():
	"""
	This function performs a continue discovering of the nearby bluetooth devices and then sends the list of devices to the lookupdevices function.
	"""

	global debug
	global threadbreak
	global database
	global gps_session
	global GRE
	global END

	try:
		if debug:
			print GRE+'[+] In discovering() function'+END
			
		while not threadbreak:
			try:
				location = ""
				try:
					if debug:
						print GRE+' - Discovering devices...'+END
					# Discovering devices
					devices = bluetooth.discover_devices(duration=3,lookup_names=True)
				except:
					if debug:
						print GRE+' - Exception in bluetooth.discover_devices(duration=3,lookup_names=True) function.'+END
					continue
				
				# If there is some device discovered, then we do this, else we try to discover again
				if devices:
					if debug:
						print GRE+' - Devices discovered: '+str(len(devices))+END
					# If there is a gps session opened then we try to get the current position
					if not gps_session:
						if debug:
							print GRE+' - Not GPS session found. Trying to get one. '+END
						try:
							gps_session = gps(mode=WATCH_ENABLE)
							gps_session.sock.settimeout(1)
							if debug:
								print GRE+' - GPS session found!'+END
						except:
							gps_session = False
							location = "GPS not available"
							if debug:
								print GRE+' - NOT GPS session found!'+END

					if gps_session:
						try:
							attemps = 0
							if debug:
								print GRE+' - Trying to get the location'+END
							while not location and attemps < 9:
								try:
									# This sometimes fail, so we try to get this a couple of times
									current = gps_session.next()
									location =  str(current['lat'])+','+str(current['lon'])
								except:
									pass
								attemps = attemps + 1

						except:
							location = ""
							if debug:
								print GRE+' - Location unavailable! Number of attemps: '+str(attemps)+END
						if not location:
							if debug:
								print GRE+' - Location not found. Number of attemps: '+str(attemps)+END
							location = "GPS not available"
						else: 
							if debug:
								print GRE+' - Location found after '+str(attemps)+' attemps.'+END

					# We set the time of the discovering
					date = time.asctime()
					if debug:
						print GRE+' - Date retrieved.'+END

					# We create a new thread to proccess the discovered devices and store the data to a bd
					threading.Thread(None,lookupdevices,args=(devices,location,date)).start()
					if debug:
						print GRE+' - A new thread has been created calling the function lookup devices.'+END
				else:
					if debug:
						print GRE+' - No devices discovered'+END

			except KeyboardInterrupt:
				print '\nKeyboard interrupt in discovering function(). Exiting.\n This may take a few seconds.'
				threadbreak = True
				gps_session.close()
				break
                        except Exception as inst:
				print 'Exception in while of discovering() function'
				threadbreak = True
				print 'Ending threads, exiting when finished'
                                print type(inst) # the exception instance
                                print inst.args # arguments stored in .args
                                print inst # _str_ allows args to printed directly
                                x, y = inst # _getitem_ allows args to be unpacked directly
                                print 'x =', x
                                print 'y =', y
				return False

		threadbreak = True
		return True
	except Exception as inst:
		print 'Exception in discovering() function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)



def lookupdevices(devices,gpsInfo,date):
	"""
	This function perform a search of data of the list of devices received and call the setDeviceInformation function to store the data.
	"""
	global debug
	global RED
	global END

	try:
		if debug:
			print RED+'[+] Inside of lookupdevices() function'+END

		# We search information of all devices discovered
		for bdaddr,name in devices:
			address = ""
			info = ""
			coordinates = ""

			if debug:
				print RED+' - Processing device: '+str(bdaddr)+' ('+str(name)+')'+END
			Mac = bdaddr
			Name = name
			if Name == 'None':
				Name = bluetooth.lookup_name(Mac)
			if gpsInfo and gpsInfo != 'GPS not available':
				[coordinates,address] = getCoordinatesFromAddress.getCoordinates(gpsInfo) 
			address = address.encode("utf-8")

			print '  {:<24}\t{:<17}\t{:<30}\t{:<27}\t{:<30}'.format(date,Mac,Name,gpsInfo,address)

			if debug:
				print RED+' - Sending device information to setDeviceInformation() function.'+END

			result = setDeviceInformation(Mac,Name,date,gpsInfo,address,info)
			if debug and result:
				print RED+' - Information stored successfully.'+END

			if debug and not result:
				print RED+' - An error ocurred saving information to database.'+END

		return True
	except Exception as inst:
		print 'Exception in lookupdevices() function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def getDatabaseConnection(database):
	"""
	This function receives a database name and returns a connection to a database. 
	If the database does not exists, it creates it.
	"""
	global debug
	global CYA
	global END

	try:
		# Here we check if the database doesn\'t exists
		if not os.path.exists(database):
			if debug:
				print CYA+'- Database doesn\'t exists. Creating it.'+END
			# If it doesn't exists we create the database
		    	connection = sqlite3.connect(database)
		    	# Once created the database we create the tables
			connection.execute("CREATE TABLE Devices(Id INTEGER PRIMARY KEY AUTOINCREMENT, Mac TEXT , Info TEXT)")
			connection.execute("CREATE TABLE Locations(Id INTEGER, GPS TEXT, FirstSeen TEXT, LastSeen TEXT, Address TEXT, Name TEXT, PRIMARY KEY(Id,GPS))")
			connection.execute("CREATE TABLE Notes(Id INTEGER, Note TEXT)")
			if debug:
				print CYA+'- Database created and connection established successfully.'+END
		else:
			# If the database exists we use it
			connection = sqlite3.connect(database)
			if debug:
				print CYA+'- Database found!'+END
				print CYA+'- Connection established successfully.'+END

		return connection

	except Exception as inst:
		print 'Exception in getDatabaseConnection() function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def getLocationFromFile():
	"""
	"""
	global debug
	global CYA
	global END

	try:
		pass

	except Exception as inst:
		print 'Exception in getDatabaseConnection() function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def getDeviceId(connection,mac):
	"""
	This function receives a database name and returns a connection to a database. 
	If the database does not exists, it creates it.
	"""
	global debug
	global CYA
	global END

	try:
		macid = ""
		try:
			macid = connection.execute("SELECT Id FROM Devices WHERE Mac = \""+mac+"\" limit 1")

			macid = macid.fetchall()
			return macid[0][0]
		except:
			return False

	except Exception as inst:
		print 'Exception in getDeviceID() function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def addDevice(connection,Mac,Info):
	"""
	This function adds a new device to the table Devices
	"""
	global debug
	global threadbreak 
	global CYA
	global END

	try:
		try:
			connection.execute("INSERT INTO Devices (Mac,Info) VALUES (?,?)",(Mac,Info))
			return True
		except:
			return False

	except Exception as inst:
		print 'Exception in addDevice() function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def setDeviceInformation(Mac,Name,FirstSeen,GPS,Address,Info):
	"""
	This function stores all the information retrieved about a device and stores it in a sqlite database.
	"""
	global debug
	global database
	global threadbreak 
	global CYA
	global END

	connection = ""

	try:
		if debug:
			print CYA+'[+] In setDeviceInformation() function.'+END
		# We get a database connection
		connection = getDatabaseConnection(database)

		if not connection:
			print ' [!] Error in creating a database connection. Exiting.'
			threadbreak = True

		# Id of the database for web interaction
		deviceid = getDeviceId(connection,Mac)

		# If the device is not in the devices table then we add it
		if not deviceid:
			result = addDevice(connection,Mac,Info)
			if not result: 
				print ' [!] Error adding a new device. Exiting.'
				threadbreak = True
			try:
				deviceid = getDeviceId(connection,Mac)
			except:
				print 'Cant get deviceid'

		try:
			# This is the structure of the tables in the database
			#connection.execute("CREATE TABLE Devices(Id INTEGER PRIMARY KEY AUTOINCREMENT, Mac TEXT , Info TEXT)")
			#connection.execute("CREATE TABLE Locations(Id INTEGER, GPS TEXT, FirstSeen TEXT, LastSeen TEXT, Address TEXT, Name TEXT, PRIMARY KEY(Id,GPS))")
			#connection.execute("CREATE TABLE Notes(Id INTEGER, Note TEXT)")

			connection.execute("INSERT INTO Locations(Id, GPS, FirstSeen, LastSeen, Address, Name) VALUES (?, ?, ?, ?, ?, ?)", (int(deviceid), repr(GPS),repr(FirstSeen),repr(FirstSeen),repr(Address),repr(Name)))
			os.system('play new.ogg -q 2> /dev/null')
			if debug:
				print CYA+'- Information added successfully!'+END
		except:
			try:
				connection.execute("UPDATE Locations SET LastSeen=? WHERE Id=? and GPS=?", (repr(FirstSeen), repr(deviceid), repr(GPS)))
				os.system('play old.ogg -q 2> /dev/null')
				if debug:
					print CYA+'- A known device found. Information updated!'+END
			except Exception as inst:
				print CYA+'Error writing to the database'+END
				connection.commit()
				connection.close()
				threadbreak = True
				return False
		
		connection.commit()
		connection.close()
		if debug:
			print CYA+'- Data submitted and database connection  closed.'+END
		return True

	except Exception as inst:
		print 'Exception in setDeviceInformation() function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		return False



##########
# MAIN
##########
def main():
        global debug
	global threadbreak
	global database
	global gps_session
	global GRE
	global CYA
	global END

	database = "bluedriving.db"
        gps_session = ""
        connection = ""
	runwebserver = False

	try:
                # By default we crawl a max of 5000 distinct URLs
		opts, args = getopt.getopt(sys.argv[1:], "hDd:w", ["help","debug","database=","webserver"])


        except getopt.GetoptError: usage()

        for opt, arg in opts:
                if opt in ("-h", "--help"): usage();sys.exit()
                if opt in ("-D", "--debug"): debug = True
                if opt in ("-d", "--database"): database = arg
                if opt in ("-w", "--webserver"): runwebserver = True
        try:
		
		version()

		try:
			# GPS session
			gps_session = gps(mode=WATCH_ENABLE)
			if gps_session:
				# We set a timeout to GPS data retrievement.
				gps_session.sock.settimeout(1)
				if debug:
					print GRE+' - GPS socket timeout set to 1.'+END
		except:
			gps_session = False

		print '  {:<24}\t{:<17}\t{:<30}\t{:<27}\t{:<30}'.format("Date","MAC address","Device name","Global Position","Aproximate address")
		print '  {:<24}\t{:<17}\t{:<30}\t{:<27}\t{:<30}'.format("----","-----------","-----------","---------------","------------------")

		startTime = time.time()
		threading.Thread(target = discovering).start()
		if runwebserver:
			port = 8000
			webserver = threading.Thread(None,createWebServer,"WebServer",args=(port,))
			webserver.setDaemon(True)
			webserver.start()

		k = ""
		while True:
			k = raw_input()
			if k == 'Q' or k == 'q':
				break

		threadbreak = True
		if gps_session:
			gps_session.close()
		for thread in threading.enumerate():
			try:
				thread.stop()
			except:
				pass
		print '\n[+] Exiting'
        except KeyboardInterrupt:
                # CTRL-C pretty handling
                print '\nExiting. It will take a few seconds to bluedriver to exit.'
		threadbreak = True
		if gps_session:
			gps_session.close()
		for thread in threading.enumerate():
			try:
				thread.stop_now()
			except:
				pass

		sys.exit(1)

	except Exception as inst:
		print 'Error in main() function'
		print 'Ending threads, exiting when finished'
		threadbreak = True
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)


if __name__ == '__main__':
        main()

