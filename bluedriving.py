#!/usr/bin/python

# TODO
# Cache the requested coordinates and addresses to save bandwith
# Cache the device information to avoid extra queries to the database

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
        except Exception, e:
		print 'Exception in getCoordinatesFromGPS'
                print "misc. exception (runtime error from user callback?):", e

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

	try:
		if debug:
			print GRE+'[+] In discovering() function'+END
			
		while not threadbreak:
			try:
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
					location = ""
					if debug:
						print GRE+' - Devices discovered: '+str(len(devices))+END
					if usegps:
						# We try to get the coordinates from the gps 
						try:
							attemps = 0
							if debug:
								print GRE+' - Trying to get the location'+END
							while not location and attemps < 9:
								location = globallocation
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
					else:
						location = "Not using GPS"

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
	global internet
	global usegps
	global RED
	global END
	global addresses
	global lookupservices

	try:
		if debug:
			print RED+'[+] Inside of lookupdevices() function'+END

		# We search information of all devices discovered
		for bdaddr,name in devices:
			address = "Unknown"
			shortaddress = address
			Info = ""
			coordinates = ""

			if debug:
				print RED+' - Processing device: '+str(bdaddr)+' ('+str(name)+')'+END

			# We set the mac address and the name of the device
			Mac = bdaddr
			Name = name

			# If there is no name for the device we lookup for it
			if Name == 'None':
				if debug:
					print 'Trying to get bluetooth names.'
				Name = bluetooth.lookup_name(Mac)
				if debug:
					print 'End trying to get bluetooth names.'

			# If there is gps location, we try to get the cached address, else we look for it
			if internet and usegps:
				if gpsInfo and gpsInfo != 'GPS not available' and gpsInfo != 'Not using GPS':
					try:
						if debug:
							print 'addresses vector: {}'.format(addresses)
						address = addresses[str(gpsInfo)]
						
					except:
						[coordinates,address] = getCoordinatesFromAddress.getCoordinates(str(gpsInfo)) 
						address = address.encode("utf-8")
						addresses[str(coordinates)] = ""
						addresses[str(coordinates)] = address
						if debug:
							print 'gpsInfo: {}'.format(gpsInfo)
							print 'address: {}'.format(address)
							print 'coordinates: {}'.format(coordinates)
							print 'addresses vector: {}'.format(addresses)
				try:
					shortaddress = address.split(', ')[0]+', '+address.split(', ')[1]
				except:
					shortaddress = address

			# We try to discover the services of the device
			shortinfo=""
			if lookupservices:
				try:
					try:
						services = ""
						services = devicesservices[Mac]
					except:
						services = ""
					if not services:
						deviceservices[Mac] = []
						Info = []
						data = lightblue.findservices(Mac)
						if data:
							for i in data:
								Info.append(i[2])
						for i in Info:
							if i not in deviceservices[Mac]:
								deviceservices[Mac].append(i)
							if i:
								shortinfo = shortinfo+repr(i)+','
						#shortinfo = Info
						Info = deviceservices[Mac]
					else:
						Info = services
				except:
					pass
			
			print '  {:<24}  {:<17}  {:<30}  {:<27}  {:<30}  {:<20}'.format(date,Mac,Name,gpsInfo,shortaddress,shortinfo)

			if debug:
				print RED+' - Sending device information to setDeviceInformation() function.'+END

			result = setDeviceInformation(Mac,Name,date,gpsInfo,address,Info)
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
			if debug:
				print 'Macid in getDeviceID() function: {}'.format(macid)
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
	global deviceservices

	try:
		try:
			connection.execute("INSERT INTO Devices (Mac,Info) VALUES (?,?)",(Mac,repr(Info)))
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
	global sound
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
			deviceservices[Mac]=""
			deviceservices[Mac]=Info
			try:
				deviceid = getDeviceId(connection,Mac)
			except:
				print 'Cant get deviceid'

		if Info:
			try:
				connection.execute("UPDATE Devices SET Info=? WHERE Id=?", (repr(Info), repr(deviceid)))
			except:
				print 'could not update info'
		if deviceid:

			try:
				# This is the structure of the tables in the database
				#connection.execute("CREATE TABLE Devices(Id INTEGER PRIMARY KEY AUTOINCREMENT, Mac TEXT , Info TEXT)")
				#connection.execute("CREATE TABLE Locations(Id INTEGER, GPS TEXT, FirstSeen TEXT, LastSeen TEXT, Address TEXT, Name TEXT, PRIMARY KEY(Id,GPS))")
				#connection.execute("CREATE TABLE Notes(Id INTEGER, Note TEXT)")

				connection.execute("INSERT INTO Locations(Id, GPS, FirstSeen, LastSeen, Address, Name) VALUES (?, ?, ?, ?, ?, ?)", (int(deviceid), repr(GPS),repr(FirstSeen),repr(FirstSeen),repr(Address),repr(Name)))
				if sound:
					try:
						os.system('play new.ogg -q 2> /dev/null')
					except:
						pass
				if debug:
					print CYA+'- Information added successfully!'+END
			except:
				try:
					connection.execute("UPDATE Locations SET LastSeen=? WHERE Id=? and GPS=?", (repr(FirstSeen), repr(deviceid), repr(GPS)))
					if sound:
						try:
							os.system('play old.ogg -q 2> /dev/null')
						except:
							pass
					if debug:
						print CYA+'- A known device found. Information updated!'+END
				except Exception as inst:
					print CYA+'Error writing to the database'+END
					print type(inst) # the exception instance
					print inst.args # arguments stored in .args
					print inst # _str_ allows args to printed directly
					connection.commit()
					connection.close()
					threadbreak = True
					return False
		else:
			if debug:
				print 'Not device id could be retrieved for this mac: {}'.format(Mac)
		
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
	global sound
	global internet
	global usegps
	global lookupservices
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

		if runwebserver:
			port = 8000
			webserverthread = threading.Thread(None,createWebServer,"WebServer",args=(port,))
			webserverthread.setDaemon(True)
			webserverthread.start()
		


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

