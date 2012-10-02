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

vernum = '0.1'
debug = False
threadbreak = False
database = ""
gps_session= ""

# Print help information and exit:
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

	try:
		if debug:
			print 'In discovering() function'
		# We set a timeout to GPS data retrievement.
		gps_session.sock.settimeout(1)
		
		while not threadbreak:
			try:
				try:
					# Discovering devices
					devices = bluetooth.discover_devices(duration=3,lookup_names=True)
				except:
					continue
				
				# If there is some device discovered, then we do this, else we try to discover again
				if devices:
					# If there is a gps session opened then we try to get the current position
					if not gps_session:
						try:
							gps_session = gps(mode=WATCH_ENABLE)
						except:
							gps_session = ""

					try:
						attemps = 0
						location = ""
						while not location and attemps < 9:
							try:
								# This sometimes fail, so we try to get this a couple of times
								current = gps_session.next()
								location =  str(current['lat'])+','+str(current['lon'])
							except:
								pass
							attemps = attemps + 1

					except:
						location = "GPS not available"
					if not location:
						location = "GPS not available"

					# We set the time of the discovering
					date = time.asctime()

					# We create a new thread to proccess the discovered devices and store the data to a bd
					threading.Thread(None,lookupdevices,args=(devices,location,date)).start()

			except KeyboardInterrupt:
				threadbreak = True
				gps_session.close()
				break
                        except Exception as inst:
				print 'Exception in while of discovering() function'
				threadbreak = True
				gps_session.close()
				print 'Ending threads, exiting when finished'
                                print type(inst) # the exception instance
                                print inst.args # arguments stored in .args
                                print inst # _str_ allows args to printed directly
                                x, y = inst # _getitem_ allows args to be unpacked directly
                                print 'x =', x
                                print 'y =', y
				return False

		threadbreak = True
		gps_session.close()
		return True
	except Exception as inst:
		print 'Exception in discovering() function'
		threadbreak = True
		gps_session.close()
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)



def lookupdevices(devices,location,date):
	"""
	This function perform a search of data of the list of devices received and call the persistence function to store the data.
	"""
	global debug

	try:
		if debug:
			print 'Inside of lookupdevices() function'

		# We search information of all devices discovered
		for bdaddr,name in devices:
			Mac = bdaddr
			Name = name
			if Name == 'None':
				Name = bluetooth.lookup_name(Mac)
			print '  {}\t{}\t{}\t\t{}'.format(date,Mac,location,Name)
			persistence(Mac,Name,date,location)

		return True
	except Exception as inst:
		print 'Exception in lookupdevices() function'
		threadbreak = True
		gps_session.close()
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def persistence(Mac,Name,FirstSeen,GpsInfo):
	"""
	This function stores all the information retrieved about a device and stores it in a sqlite database.
	"""
	global debug
	global database

	try:
		if debug:
			print 'In persistence() function'

		# Here we check if the database doesn\'t exists
		if not os.path.exists(database):
			if debug:
				print '[+] Creating database'
			# If it doesn't exists we create the database
		    	connection = sqlite3.connect(database)
		    	# Once created the database we create the tables
			#connection.execute("CREATE TABLE Devices(Mac TEXT, Name TEXT, FirstSeen TEXT, LastSeen TEXT, GpsInfo TEXT)")
			connection.execute("CREATE TABLE Devices(Id INTEGER, Mac TEXT , Name TEXT, FirstSeen TEXT, LastSeen TEXT, GpsInfo TEXT, PRIMARY KEY(Mac,GpsInfo))")
			connection.execute("CREATE TABLE Details(Mac TEXT , TEXT, FirstSeen TEXT, LastSeen TEXT, GpsInfo TEXT, PRIMARY KEY(Mac,GpsInfo))")
			if debug:
				print '[+] Connecting to database'
		else:
			# If the database exists we use it
			connection = sqlite3.connect(database)

		# Id of the database for web interaction
		lastid = connection.execute('select Id from Devices order by Id desc limit 1')
		unique_id_database = lastid.fetchall()
		if unique_id_database:
			Id = unique_id_database[0][0] + 1
		else:
			Id = 1
		try:
			connection.execute("INSERT INTO Devices(Id, Mac, Name, FirstSeen, LastSeen, GpsInfo) VALUES (?, ?, ?, ?, ?, ?)", (int(Id), repr(Mac), repr(Name), repr(FirstSeen), '-',repr(GpsInfo)))
			os.system('play new.ogg -q 2> /dev/null')
		except:
			try:
				connection.execute("UPDATE Devices SET LastSeen=? WHERE Mac=? and GpsInfo=?", (repr(FirstSeen), repr(Mac), repr(GpsInfo)))
				os.system('play new.ogg -q 2> /dev/null')
			except Exception as inst:
				print 'Error writing to the database'
		
		connection.commit()
		connection.close()

	except Exception as inst:
		print 'Exception in persistence() function'
		threadbreak = True
		gps_session.close()
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)



##########
# MAIN
##########
def main():
        global debug
	global threadbreak
	global database
	global gps_session

	database = "bluedriving.db"
        gps_session = ""
        connection = ""

	try:
                # By default we crawl a max of 5000 distinct URLs
                opts, args = getopt.getopt(sys.argv[1:], "hDd:", ["help","debug","database="])


        except getopt.GetoptError: usage()

        for opt, arg in opts:
                if opt in ("-h", "--help"): usage();sys.exit()
                if opt in ("-D", "--debug"): debug = True
                if opt in ("-d", "--database"): database = arg
        try:
		

		try:
			# GPS session
			gps_session = gps(mode=WATCH_ENABLE)
		except:
			print '\n No GPS session found'
			gps_session = False

		print '  DATE\t\t\t\tMAC ADDRESS\t\tGLOBAL POSITION\t\t\t\tNAME'
		print '  -----------------------------------------------------------------------------------------------------------'
		startTime = time.time()
		threading.Thread(target = discovering).start()

		while True:
			k = raw_input()
			if k == 'Q' or k == 'q':
				break

		threadbreak = True
		gps_session.close()
		print '\n[+] Exiting'
        except KeyboardInterrupt:
                # CTRL-C pretty handling
                print 'Exiting. It will take a few seconds to bluedriver to exit.'
		threadbreak = True
		gps_session.close()
		sys.exit(1)

	except Exception as inst:
		print 'Error in main() function'
		print 'Ending threads, exiting when finished'
		threadbreak = True
		gps_session.close()
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)


if __name__ == '__main__':
        main()

