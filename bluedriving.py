#!/usr/bin/python
# UPDATES:
#  - Cache the requested coordinates and addresses to save bandwith
#  - Cache the device information to avoid extra queries to the database

# TODO
# Redesign the whole program. 
# Fix crashing when multiple threads try to write in the database
# 

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
import lightblue
import Queue

vernum = '0.1'
debug = False
threadbreak = False
database = ""
gps_session= ""
usegps = True
globallocation = ""
sound = True
internet = True
lookupservices = True
GRE='\033[92m'
END='\033[0m'
RED='\033[91m'
CYA='\033[96m'

addresses = {}
deviceservices = {}

def version():
        """
        This function prints information about this utility
        """
	global RED
	global END

        print RED
        print "   "+ sys.argv[0] + " Version "+ vernum +" @COPYLEFT                    "
        print "   Authors: verovaleros, eldraco, nanojaus                               "
        print "   Bluedriver is a bluetooth wardriving utility.                        "
        print 
        print END
 
def usage():
        """
        This function prints the posible options of this program.
        """
	global RED
	global END
        
	print RED
        print
	print "   "+ sys.argv[0] + " Version "+ vernum +" @COPYLEFT                    "
        print "   Authors: verovaleros, eldraco, nanojaus                               "
        print "   Bluedriver is a bluetooth wardriving utility.                        "
        print 
        print "\n   Usage: %s <options>" % sys.argv[0]
        print "   Options:"
        print "  \t-h, --help                           Show this help message and exit."
        print "  \t-D, --debug                          Debug mode."
        print "  \t-d, --database                       Name of the database to store the data."
        print "  \t-w, --webserver                      It runs a local webserver to visualize and interact with the collected information."
        print "  \t-s, --not-sound                      Do not play the beautiful discovering sounds. Are you sure you wanna miss this?"
        print "  \t-i, --not-internet                   If you dont have internet use this option to save time while getting coordinates and addresses from the web."
        print "  \t-l, --not-lookup-services            Use this option to not lookup for services for each device. It make the discovering a little faster."
        print "  \t-g, --not-gps            		Use this option when you want to run the bluedriving withouth a gpsd connection."
	print 
        print END
 

def getCoordinatesFromGPS():
        """
        """
        global debug
        global globallocation
	global gps_session

	counter = 0
        try:
		while True:
                        if gps_session:
                                while True:
					if counter < 10:
						try:
							gpsdata = gps_session.next()
							globallocation =  str(gpsdata['lat'])+','+str(gpsdata['lon'])
						except Exception, e:
							#print "misc. exception (runtime error from user callback?):", e
							globallocation = False
							counter = counter + 1
					else:
						try:
							try:
								gps_session.close()
							except: 
								pass
							gps_session = gps(mode=WATCH_ENABLE)
							gps_session.sock.settimeout(1)
							counter = 0
						except:
							pass
                        else:
				try:
					gps_session = gps(mode=WATCH_ENABLE)
					gps_session.sock.settimeout(1)
				except:
					time.sleep(10)
					pass

        except KeyboardInterrupt:
                # CTRL-C pretty handling.
                print "Keyboard Interruption!. Exiting."
                sys.exit(1)
	except Exception as inst:
		print 'Exception in getCoordinatesFromGPS'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

# Discovering function
def discovering():
	"""
	This function performs a continue discovering of the nearby bluetooth devices and then sends the list of devices to the lookupdevices function.
	"""

	global debug
	global threadbreak
	global database
	global gps_session
	global usegps
	global globallocation
	global addresses
	global GRE
	global END
	global g_devices

	try:
		if debug:
			print GRE+'[+] In discovering() function'+END
			
		while not threadbreak:
			try:
				try:
					if debug:
						print GRE+' - Discovering devices...'+END
					# Discovering devices
					data = bluetooth.discover_devices(duration=3,lookup_names=True)
					
					if data:
						for d in data:
							try:
								g_devices[d[0]]=d[1]
							except:
								if debug:
									print 'No new device found'
							ftime = time.asctime()
							print '  {:<24}  {:<17}  {:<30}  {:<27}  {:<30}  {:<20}'.format(ftime,d[0],d[1],"NO GPS","NO ADDRESS","NO INFO")
							g_devices.put([ftime,d[0],d[1],"NO GPS","NO ADDRESS","NO INFO"])
							if debug:
								print 'Data loaded to queue'
					else: 
						print '  -'

				except:
					if debug:
						print GRE+' - Exception in bluetooth.discover_devices(duration=3,lookup_names=True) function.'+END
					continue
				
			except KeyboardInterrupt:
				threadbreak = True
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
				sys.exit(1)

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

def create_database(database_name):
	global debug
	global verbose
	global CYA
	global END

	try:
		# We check if the database exists
		if not os.path.exists(database_name):
			if debug:
				print CYA+'Creating database'+END
			# Creating database
		    	connection = sqlite3.connect(database_name)
			# Creating tables
			connection.execute("CREATE TABLE Devices(Id INTEGER PRIMARY KEY AUTOINCREMENT, Mac TEXT , Info TEXT)")
			connection.execute("CREATE TABLE Locations(Id INTEGER PRIMARY KEY AUTOINCREMENT, MacId INTEGER, 
					     	GPS TEXT, FirstSeen TEXT, LastSeen TEXT, Address TEXT, Name TEXT, UNIQUE(MacId,GPS))")
			connection.execute("CREATE TABLE Notes(Id INTEGER, Note TEXT)")
			if debug:
				print CYA+'Database created'+END
		else:
			if debug:
				print CYA+'Database already exist'+END
	except Exception as inst:
		print 'Exception in create_database(database_name) function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def get_database_connection(database_name):
	global debug
	global verbose
	global CYA
	global END

	try:
		if not os.path.exists(database_name):
			create_database(database_name)
		connection = sqlite3.connect(database_name)
		if debug:
			print CYA+'Database connection retrieved'+END
		return connection
	except Exception as inst:
		print 'Exception in create_database(database_name) function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def add_device(connection,Mac,Info):
	global debug
	global verbose
	global CYA
	global END

	try:
		connection.execute("INSERT INTO Devices (Mac,Info) VALUES (?,?)",(Mac,repr(Info)))
		connection.commit()
	except Exception as inst:
		print 'Exception in connection.execute() function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)


def test():
	global g_devices

	try:
		while True:
			if not g_devices.empty():
				temp = g_devices.get()
				print '  {:<24}  {:<17}  {:<30}  {:<27}  {:<30}  {:<20}'.format(temp[0],temp[1],temp[2],temp[3],temp[4],temp[5])
			time.sleep(5)

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

##########
# MAIN
##########
def main():
        global debug
	global threadbreak
	global database
	global gps_session
	global sound
	global internet
	global usegps
	global lookupservices
	global g_devices
	global GRE
	global CYA
	global END

	database = "bluedriving.db"
        gps_session = ""
        connection = ""
	runwebserver = False

	try:
                # By default we crawl a max of 5000 distinct URLs
		opts, args = getopt.getopt(sys.argv[1:], "hDd:wsilg", ["help","debug","database=","webserver","disable-sound","not-internet","not-lookup-services","-not-gps"])


        except getopt.GetoptError: usage()

        for opt, arg in opts:
                if opt in ("-h", "--help"): usage();sys.exit()
                if opt in ("-D", "--debug"): debug = True
                if opt in ("-d", "--database"): database = arg
                if opt in ("-w", "--webserver"): runwebserver = True
                if opt in ("-s", "--disable-sound"): sound = False
                if opt in ("-i", "--not-internet"): internet = False
                if opt in ("-l", "--not-lookup-services"): lookupservices = False
                if opt in ("-g", "--not-gps"): usegps = False
        try:
		
		version()
		g_devices = Queue.Queue()

		if usegps:
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

			gpsthread = threading.Thread(None,target=getCoordinatesFromGPS)
			gpsthread.setDaemon(True)
			gpsthread.start()

		print '  {:<24}  {:<17}  {:<30}  {:<27}  {:<30}  {:<20}'.format("Date","MAC address","Device name","Global Position","Aproximate address","Info")
		print '  {:<24}  {:<17}  {:<30}  {:<27}  {:<30}  {:<20}'.format("----","-----------","-----------","---------------","------------------","----")

		startTime = time.time()
		discoveringthread = threading.Thread(target = discovering)
		discoveringthread.setDaemon(True)
		discoveringthread.start()

		test_thread = threading.Thread(target = test)
		test_thread.setDaemon(True)
		test_thread.start()

		if runwebserver:
			port = 8000
			webserverthread = threading.Thread(None,createWebServer,"WebServer",args=(port,))
			webserverthread.setDaemon(True)
			webserverthread.start()
		


		k = ""
		while True:
			k = raw_input()
			if k == 'd' or k == 'D':
				if debug == True:
					debug = False
					print GRE+'Debug mode desactivated'+END
				else:
					debug = True
					print GRE+'Debug mode activated'+END
	
			if k == 's':
				if sound == True:
					sound = False
					print GRE+'Sound desactivated'+END
				else:
					sound = True
					print GRE+'Sound activated'+END
			if k == 'i':
				if internet == True:
					internet = False
					print GRE+'Internet desactivated'+END
				else:
					internet = True
					print GRE+'Internet activated'+END
			if k == 'l':
				if lookupservices == True:
					lookupservices = False
					print GRE+'Look up services desactivated'+END
				else:
					lookupservices = True
					print GRE+'Look up services activated'+END
			if k == 'g':
				if usegps == True:
					usegps = False
					print GRE+'GPS desactivated'+END
				else:
					usegps = True
					print GRE+'GPS activated'+END

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

