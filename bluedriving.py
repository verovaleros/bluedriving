#!/usr/bin/python
# UPDATES:
#  - Cache the requested coordinates and addresses to save bandwith
#  - Cache the device information to avoid extra queries to the database

# TODO
# Redesign the whole program. 
# Fix crashing when multiple threads try to write in the database
# Improve readme of github
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
import pygame

# Global variables
vernum = '0.1'
debug = False
threadbreak = False
global_location = ""
flag_sound = True
flag_internet = True
flag_gps = True
flag_lookup_services = True
list_devices = {}
queue_devices = ""

address_cache = {}
deviceservices = {}

GRE='\033[92m'
END='\033[0m'
RED='\033[91m'
CYA='\033[96m'

# End global variables

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
        print "  \t-D, --debug                          Debug mode ON. Prints debug information on the screen."
        print "  \t-d, --database-name                  Name of the database to store the data."
        print "  \t-w, --webserver                      It runs a local webserver to visualize and interact with the collected information."
        print "  \t-s, --not-sound                      Do not play the beautiful discovering sounds. Are you sure you wanna miss this?"
        print "  \t-i, --not-internet                   If you dont have internet use this option to save time while getting coordinates and addresses from the web."
        print "  \t-l, --not-lookup-services            Use this option to not lookup for services for each device. It make the discovering a little faster."
        print "  \t-g, --not-gps            		Use this option when you want to run the bluedriving withouth a gpsd connection."
        print "  \t-f, --fake-gps            		Fake gps position. Useful when you don't have a gps but know your location from google maps. Example: -f '38.897388,-77.036543'"
	print 
        print END
 

def get_coordinates_from_gps():
        """
        """
        global debug
        global global_location
	global threadbreak

	counter = 0
	gps_session = ""
        try:
		while True:
                        if gps_session:
                                while True:
					if counter < 10:
						try:
							gpsdata = gps_session.next()
							global_location =  str(gpsdata['lat'])+','+str(gpsdata['lon'])
						except Exception, e:
							try:
								gpsdata = gps_session.next()
								global_location =  str(gpsdata['lat'])+','+str(gpsdata['lon'])
							except Exception,e:
								#print "misc. exception (runtime error from user callback?):", e
								global_location = False
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
		print 'Exiting. It may take a few seconds.'
		threadbreak = True
	except Exception as inst:
		print 'Exception in get_coordinates_from_gps'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def get_address_from_gps(location_gps):
	global debug
	global verbose
	global address_cache
	global flag_internet
	global threadbreak
	
	coordinates = ""
	address = ""
	try:
		if location_gps:
			if debug:
				print 'Coordinates: {}'.format(location_gps)
			try:
				# If the location is already stored, we get it.
				address = address_cache[location_gps]
			except:
				if flag_internet:
					[coordinates,address] = getCoordinatesFromAddress.getCoordinates(location_gps)
					address = address.encode('utf-8')
					if debug:
						print 'Coordinates: {} Address: {}'.format(coordinates,address)
					
					address_cache[location_gps] = address
				else:
					address = "Internet deactivated"
		return address

	except KeyboardInterrupt:
		print 'Exiting. It may take a few seconds.'
		threadbreak = True
	except Exception as inst:
		print 'Exception in get_address_from_gps()'
		print 'Received coordinates: {}'.format(location_gps)
		print 'Retrieved coordinates: {}'.format(coordinates)
		print 'Retrieved Address: {}'.format(address)
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
def bluetooth_discovering():
	"""
	This function performs a continue discovering of the nearby bluetooth devices and then sends the list of devices to the lookupdevices function.
	"""
	global debug
	global verbose
	global threadbreak

	try:
		if debug:
			print '[+] In bluetooth_discovering() function'
			
		while not threadbreak:
			data = ""

			try:
				try:
					if debug:
						print 'Discovering devices...'
					# Discovering devices
					data = bluetooth.bluez.discover_devices(lookup_names=True)
					#data = bluetooth.discover_devices(duration=3,lookup_names=True)
					if debug:
						print data
					
					if data:
						# We start a new thread that process the information retrieved 
						process_device_information_thread = threading.Thread(None,target = process_devices,args=(data,))
						process_device_information_thread.setDaemon(True)
						process_device_information_thread.start()
					else: 
						print '  -'
				except:
					if debug:
						print 'Exception in bluetooth.discover_devices(duration=3,lookup_names=True) function.'
					continue
			except KeyboardInterrupt:
				print 'Exiting. It may take a few seconds.'
				threadbreak = True
                        except Exception as inst:
				print 'Exception in while of bluetooth_discovering() function'
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
	except KeyboardInterrupt:
		print 'Exiting. It may take a few seconds.'
		threadbreak = True
	except Exception as inst:
		print 'Exception in bluetooth_discovering() function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def process_devices(device_list):
	global debug
	global verbose
	global threadbreak
	global flag_gps
	global flag_internet
	global flag_sound
	global global_location
	global list_devices
	global queue_devices

	location_gps = "NO GPS DATA"
	location_address = "NO ADDRESS RETRIEVED"
	ftime = ""
	flag_new_device = False
	try:
		if device_list:
			for d in device_list:
				flag_new_device = False
				try:
					list_devices[d[0]]
					flag_new_device = False
				except:
					list_devices[d[0]]=d[1]
					flag_new_device = True
					if debug:
						print 'New device found'
				ftime = time.asctime()

				# We get location's related information
				if flag_gps:
					location_gps = global_location
					if flag_internet:
						location_address = get_address_from_gps(location_gps)

				# We try to lookup more information about the device
				device_services = []
				if flag_lookup_services:
					services_data = lightblue.findservices(d[0])
					if services_data:
						for i in services_data:
							device_services.append(i[2])

				if len(device_services) > 1:
					print '  {:<24}  {:<17}  {:<30}  {:<27}  {:<30}  {:<20}'.format(ftime,d[0],d[1],location_gps,location_address.split(',')[0],device_services[0])
					for service in device_services[1:]:
						print '  {:<24}  {:<17}  {:<30}  {:<27}  {:<30}  {:<20}'.format('','','','','',service)
						#print '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{:<30}'.format(service)
				else:
					print '  {:<24}  {:<17}  {:<30}  {:<27}  {:<30}  {:<20}'.format(ftime,d[0],d[1],location_gps,location_address.split(',')[0],device_services)
					
				if flag_sound:
					if flag_new_device:
						pygame.mixer.music.load('new.ogg')
						pygame.mixer.music.play()
					else:
						pygame.mixer.music.load('old.ogg')
						pygame.mixer.music.play()

				queue_devices.put([ftime,d[0],d[1],location_gps,location_address,device_services])

				if debug:
					print 'Data loaded to queue'
				time.sleep(0.5)
	except KeyboardInterrupt:
		print 'Exiting. It may take a few seconds.'
		threadbreak = True
	except Exception as inst:
		print 'Exception in process_devices() function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def db_create_database(database_name):
	global debug
	global verbose
	global threadbreak

	try:
		# We check if the database exists
		if not os.path.exists(database_name):
			if debug:
				print 'Creating database'
			# Creating database
		    	connection = sqlite3.connect(database_name)
			# Creating tables
			connection.execute("CREATE TABLE Devices(Id INTEGER PRIMARY KEY AUTOINCREMENT, Mac TEXT , Info TEXT)")
			connection.execute("CREATE TABLE Locations(Id INTEGER PRIMARY KEY AUTOINCREMENT, MacId INTEGER, GPS TEXT, FirstSeen TEXT, LastSeen TEXT, Address TEXT, Name TEXT, UNIQUE(MacId,GPS))")
			connection.execute("CREATE TABLE Notes(Id INTEGER, Note TEXT)")
			connection.execute("CREATE TABLE Alarms(Id INTEGER, Alarm TEXT)")
			if debug:
				print 'Database created'
		else:
			if debug:
				print 'Database already exist'

	except KeyboardInterrupt:
		print 'Exiting. It may take a few seconds.'
		threadbreak = True
	except Exception as inst:
		print 'Exception in db_create_database(database_name) function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def db_get_database_connection(database_name):
	"""
	"""
	global debug
	global verbose
	global threadbreak

	try:
		if not os.path.exists(database_name):
			db_create_database(database_name)
		connection = sqlite3.connect(database_name)
		if debug:
			print 'Database connection retrieved'
		return connection

	except KeyboardInterrupt:
		print 'Exiting. It may take a few seconds.'
		threadbreak = True
	except Exception as inst:
		print 'Exception in get_database_connection(database_name) function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def db_get_device_id(connection,bdaddr,device_information):
	"""
	Receives a device address and returns a device id from the database. If device does not exists in database, it adds it.
	"""
	global debug
	global verbose
	global threadbreak

	try:
		mac_id = ""
		try:
			mac_id = connection.execute("SELECT Id FROM Devices WHERE Mac = \""+bdaddr+"\" limit 1")
			mac_id = mac_id.fetchall()

			if not mac_id:
				db_add_device(connection,bdaddr,device_information)
				mac_id = connection.execute("SELECT Id FROM Devices WHERE Mac = \""+bdaddr+"\" limit 1")
				mac_id = mac_id.fetchall()

			if debug:
				print 'Macid in db_get_device_id() function: {}'.format(mac_id)
			return mac_id[0][0]
		except:
			print 'Device Id could not be retrieved. BDADDR: {}'.format(bdaddr)
			return False

	except KeyboardInterrupt:
		print 'Exiting. It may take a few seconds.'
		threadbreak = True
	except Exception as inst:
		print 'Exception in db_get_device_id() function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def db_add_device(connection,bdaddr,device_information):
	"""
	"""
	global debug
	global verbose
	global threadbreak

	try:
		try:
			connection.execute("INSERT INTO Devices (Mac,Info) VALUES (?,?)",(bdaddr,repr(device_information)))
			connection.commit()
			if debug:
				print 'New device added'
			return True
		except:
			if debug:
				print 'Device already exists'
			return False
		
	except KeyboardInterrupt:
		print 'Exiting. It may take a few seconds.'
		threadbreak = True
	except Exception as inst:
		print 'Exception in db_add_device() function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def db_update_device(connection,device_id,device_information):
	"""
	"""
	global debug
	global verbose
	global threadbreak

	try:
		try:
			connection.execute("UPDATE Devices SET Info=? WHERE Id=?", (repr(device_information), repr(device_id)))
			connection.commit()
			if debug:
				print 'Device information updated'
			return True
		except:
			if debug:
				print 'Device information not updated'
				print 'Device ID: {}'.format(device_id)
				print 'Device Information: {}'.format(device_information)
			return False

	except KeyboardInterrupt:
		print 'Exiting. It may take a few seconds.'
		threadbreak = True
	except Exception as inst:
		print 'Exception in db_update_device() function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def db_add_location(connection,device_id,location_gps,first_seen,location_address,device_name):
	"""
	"""
	global debug
	global verbose
	global threadbreak

	try:
		try:
			connection.execute("INSERT INTO Locations(MacId, GPS, FirstSeen, LastSeen, Address, Name) VALUES (?, ?, ?, ?, ?, ?)",(int(device_id), repr(location_gps),repr(first_seen),repr(first_seen),repr(location_address),repr(device_name)))
			connection.commit()
			if debug:
				print 'Location added'
		except:
			if debug:
				print 'Location not added'
				print 'Device ID: {}'.format(device_id)
				print 'Device Name: {}'.format(device_name)
				print 'GPS Location: {}'.format(location_gps)
				print 'First seen: {}'.format(first_seen)
				print 'Last seen: {}'.format(first_seen)
			return False

	except KeyboardInterrupt:
		print 'Exiting. It may take a few seconds.'
		threadbreak = True
	except Exception as inst:
		print 'Exception in db_add_location() function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)

def db_update_location(connection,device_id,location_gps,first_seen):
	"""
	"""
	global debug
	global verbose
	global threadbreak

	try:
		try:
			connection.execute("UPDATE Locations SET LastSeen=? WHERE Id=? AND GPS=?", (repr(first_seen), repr(device_id), repr(location_gps)))
			connection.commit()
			if debug:
				print 'Location updated'
		except:
			if debug:
				print 'Location not updated'
				print 'Device ID: {}'.format(device_id)
				print 'GPS Location: {}'.format(location_gps)
				print 'Last seen: {}'.format(first_seen)
			return False

	except KeyboardInterrupt:
		print 'Exiting. It may take a few seconds.'
		threadbreak = True
	except Exception as inst:
		print 'Exception in db_update_location() function'
		threadbreak = True
		print 'Ending threads, exiting when finished'
		print type(inst) # the exception instance
		print inst.args # arguments stored in .args
		print inst # _str_ allows args to printed directly
		x, y = inst # _getitem_ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		sys.exit(1)


def store_device_information(database_name):
	global debug
	global verbose
	global queue_devices
	global threadbreak

	connection = ""
	try:
		# We create a database connection
		connection = db_get_database_connection(database_name)
		while not threadbreak:
			while not queue_devices.empty():
				# We clear the variables to use
				device_id = ""
				device_bdaddr = ""
				device_name = ""
				device_information = ""
				location_gps = ""
				location_address = ""
				first_seen = ""
				last_seen = ""

				if not queue_devices.empty():
					# We extract the device from the queue
					temp = queue_devices.get()

					# We load the information
					first_seen = temp[0]
					last_seen = temp[0]
					device_bdaddr = temp[1]
					device_name = temp[2]
					location_gps = temp[3]
					location_address = temp[4]
					device_information = temp[5]
					
					device_id = db_get_device_id(connection,device_bdaddr,device_information)

					if device_id:
						# If we have a device information, then we update the information for the device
						result = db_update_device(connection,device_id,device_information)
						if not result:
							print 'Device information could not be updated'
						# We try to store a new location
						result = db_add_location(connection,device_id,location_gps,first_seen,location_address,device_name)

						# If the location has not changed, result will be False. We update the last seen field into locations.
						if not result:
							result = db_update_location(connection,device_id,location_gps,first_seen)

					#print '  {:<24}  {:<17}  {:<30}  {:<27}  {:<30}  {:<20}'.format(temp[0],temp[1],temp[2],temp[3],temp[4],temp[5])
			time.sleep(2)

	except KeyboardInterrupt:
		print 'Exiting. It may take a few seconds.'
		threadbreak = True
	except Exception as inst:
		print 'Exception in store_device_information() function'
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
	global flag_sound
	global flag_internet
	global flag_gps
	global flag_lookup_services
	global queue_devices
	global GRE
	global CYA
	global END
	global global_location

	database_name = "bluedriving.db"
	flag_run_webserver = False
	fake_gps = ''

	try:
                # By default we crawl a max of 5000 distinct URLs
		opts, args = getopt.getopt(sys.argv[1:], "hDd:wsilgf:", ["help","debug","database-name=","webserver","disable-sound","not-internet","not-lookup-services","-not-gps","fake-gps="])


        except getopt.GetoptError: usage()

        for opt, arg in opts:
                if opt in ("-h", "--help"): usage(); sys.exit()
                if opt in ("-D", "--debug"): debug = True
                if opt in ("-d", "--database-name"): database_name = arg
                if opt in ("-w", "--webserver"): flag_run_webserver = True
                if opt in ("-s", "--disable-sound"): flag_sound = False
                if opt in ("-i", "--not-internet"): flag_internet = False
                if opt in ("-l", "--not-lookup-services"): flag_lookup_services = False
                if opt in ("-g", "--not-gps"): flag_gps = False; flag_internet = False
                if opt in ("-f", "--fake-gps"): fake_gps = arg
        try:
		
		version()
		queue_devices = Queue.Queue()
		startTime = time.time()

		# We print the header for printing results on console
		print '  {:<24}  {:<17}  {:<30}  {:<27}  {:<30}  {:<20}'.format("Date","MAC address","Device name","Global Position","Aproximate address","Info")
		print '  {:<24}  {:<17}  {:<30}  {:<27}  {:<30}  {:<20}'.format("----","-----------","-----------","---------------","------------------","----")

		# Here we start the thread to get gps location		
		if flag_gps and not fake_gps:
			gps_thread = threading.Thread(None,target=get_coordinates_from_gps)
			gps_thread.setDaemon(True)
			gps_thread.start()
		elif fake_gps:
			# Verify fake_gps
			if debug:
				print 'Using the fake gps address: {0}'.format(fake_gps)
			global_location = fake_gps
		
		# Here we start the web server
		if flag_run_webserver:
			port = 8000
			webserver_thread = threading.Thread(None,createWebServer,"web_server",args=(port,))
			webserver_thread.setDaemon(True)
			webserver_thread.start()

		# Here we start the discovering devices threads
		bluetooth_discovering_thread = threading.Thread(None,target = bluetooth_discovering)
		bluetooth_discovering_thread.setDaemon(True)
		bluetooth_discovering_thread.start()

		# Here we start the thread that will continuosly store data to the database
		store_device_information_thread = threading.Thread(None,target = store_device_information,args=(database_name,))
		store_device_information_thread.setDaemon(True)
		store_device_information_thread.start()

		# Initializating sound
		if flag_sound:
			pygame.init()

		# This options are for live-options interaction
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
				if flag_sound == True:
					flag_sound = False
					print GRE+'Sound desactivated'+END
				else:
					pygame.init()
					flag_sound = True
					print GRE+'Sound activated'+END
			if k == 'i':
				if flag_internet == True:
					flag_internet = False
					print GRE+'Internet desactivated'+END
				else:
					flag_internet = True
					print GRE+'Internet activated'+END
			if k == 'l':
				if flag_lookup_services == True:
					flag_lookup_services = False
					print GRE+'Look up services desactivated'+END
				else:
					flag_lookup_services = True
					print GRE+'Look up services activated'+END
			if k == 'g':
				if flag_gps == True:
					flag_gps = False
					flag_internet = False
					print GRE+'GPS desactivated'+END
					print GRE+'Internet desactivated'+END
				else:
					flag_gps = True
					print GRE+'GPS activated'+END

			if k == 'Q' or k == 'q':
				break

		threadbreak = True
		print '\n[+] Exiting'

	except KeyboardInterrupt:
		print 'Exiting. It may take a few seconds.'
		threadbreak = True
		time.sleep(1)
		for thread in threading.enumerate():
			try:
				thread.stop_now()
			except:
				pass
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

