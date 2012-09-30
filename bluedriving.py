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

vernum = '0.1'
debug = False

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
  

# Bluedrive function
def bluedrive(cursor,session):
	global debug

	try:
		if debug:
			print 'In Bluedrive() function'
		
		print '  DATE\t\t\t\tMAC ADDRESS\t\tGLOBAL POSITION\t\t\t\tNAME'
		print '  -----------------------------------------------------------------------------------------------------------'
		
		while True:
			try:
				try:
					devices = bluetooth.discover_devices()
				except:
					continue

				for bdaddr in devices:
					location = "Global position not found"
					mac = bdaddr
					name = bluetooth.lookup_name(mac)
					if session:
						try:
							current = session.next()
							location =  str(current['lat'])+','+str(current['lon'])
						except:
							current = session.next()
							try:
								location =  str(current['lat'])+','+str(current['lon'])
							except:
								location = "Global position not found"
					date = time.asctime()
					print '  '+date+'\t'+mac+'\t'+location+'\t\t'+name
					try:
						cursor.execute("INSERT INTO Devices(MAC, Name, FirstSeen, LastSeen, gpsInfo) VALUES (?, ?, ?, ?, ?)", (mac,name,date,'-',location))
					except:
						cursor.execute("UPDATE Devices SET LastSeen=? WHERE MAC=? and gpsInfo=?", (date,mac,location))
						pass
			except KeyboardInterrupt:
				break
			except:
				print '\nError, trying to continue. Hit CTRL-C to exit.'
				pass
		print '\n[+] Exiting'
		cursor.connection.commit()
		cursor.close()

	except:
		print 'Error in bluedrive() function'
                sys.exit(1)

##########
# MAIN
##########
def main():
        global debug

	database = "bluedriving.db"
        session = ""

	try:
                # By default we crawl a max of 5000 distinct URLs
                opts, args = getopt.getopt(sys.argv[1:], "hDd:", ["help","debug","database="])


        except getopt.GetoptError: usage()

        for opt, arg in opts:
                if opt in ("-h", "--help"): usage()
                if opt in ("-D", "--debug"): debug = True
                if opt in ("-d", "--database"): database = arg
        try:
		# Here we check if the database doesn\'t exists
		if not os.path.exists(database):
			if debug:
				print '[+] Creating database'
			# If it doesn't exists we create the database
		    	connection = sqlite3.connect(database)
		    	# Once created the database we create the tables
			#connection.execute("CREATE TABLE Devices(MAC TEXT, Name TEXT, FirstSeen TEXT, LastSeen TEXT, gpsInfo TEXT)")
			connection.execute("CREATE TABLE Devices(MAC TEXT , Name TEXT, FirstSeen TEXT, LastSeen TEXT, gpsInfo TEXT, PRIMARY KEY(MAC,gpsInfo))")
		else:
			if debug:
				print '[+] Connecting to database'
			# If the database exists we use it
		    	connection = sqlite3.connect(database)
		
		# Database cursor 
		cursor = connection.cursor()

		try:
			# GPS session
			session = gps(mode=WATCH_ENABLE)
		except:
			print '\n No GPS session found'
			session = False

		bluedrive(cursor,session)

        except KeyboardInterrupt:
                # CTRL-C pretty handling
                print 'Keyboard Interruption!. Exiting.'
                sys.exit(1)
	except:
		print 'Error in main() function'
                sys.exit(1)


if __name__ == '__main__':
        main()

