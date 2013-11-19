#!/usr/bin/python
#  Copyright (C) 2009  Veronica Valeros, Juan Manuel Abrigo, Sebastian Garcia
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# Author:
# Veronica Valeros  vero.valeros@gmail.com
#
# Changelog
# - Added a function to list for a given mac the date, position, and name
#
# Description
# manageDB is a python tool to manage bluedriving database
#
# TODO
# - with -L if the device does not exists, output nothing.
# - For all the devices output all the locations with gps address and mac and vendor.
# - Given one date, print all the devices found that day, along with the gps and address.
# - When -L is used, check the address in the DB. If it exists, print it and do not search it again. If not, search for it and store it on the DB.

# standar imports
import sys
import re
import getopt
import copy
import os
import time
import sqlite3
from getCoordinatesFromAddress import getCoordinates


# Global variables
vernum = '0.1'
debug = False
quiet = False


def version():
    """
    This function prints information about this utility
    """

    print
    print "   "+ sys.argv[0] + " Version "+ vernum 
    print "   Authors: Vero Valeros (vero.valeros@gmail.com)"
    print "   manageDB is a python tool to manage bluedriving database.            "
    print

def usage():
    """
    This function prints the posible options of this program.
    """
    print
    print "   "+ sys.argv[0] + " Version "+ vernum +" @COPYLEFT"
    print "   Authors: Vero Valeros (vero.valeros@gmail.com), Seba Garcia (eldraco@gmail.com)"
    print "   Contributors: nanojaus"
    print "   manageDB is a python tool to manage bluedriving database.            "
    print
    print "\n   Usage: %s <options>" % sys.argv[0]
    print "   Options:"
    print "  \t-h, --help                           Show this help message and exit."
    print "  \t-D, --debug                          Debug mode ON. Prints debug information on the screen."
    print "  \t-d, --database-name                  Name of the database to store the data."
    print "  \t-l, --limit                          Limits the number of results when querying the database"
    print "  \t-e, --get-devices                    List all the MAC addresses of the devices stored in the DB"
    print "  \t-n, --get-devices-with-names         List all the MAC addresses and the names of the devices stored in the DB"
    print "  \t-E, --device-exists <mac>            Check if a MAC address is present on the database"
    print "  \t-R, --remove-device <mac>            Remove a device using a MAC address"
    print "  \t-g, --grep-names <string>            Look names matching the given string"
    print "  \t-r, --rank-devices <limit>           Shows a top 10 of the most seen devices on the database"
    print "  \t-m, --merge-with <db>                Merge the database (-d) with this database.Ex. bluedriving.py -d blu.db -m netbook.db"
    print "  \t-L, --get-locations-with-date <mac>  Prints a list of locations and dates in which the mac has been seen."
    print "  \t-q, --quiet-devices                  Print only the results"
    print "  \t-C, --count-devices                  Count the amount of devices on the database"
    print "  \t-c, --create-db                      Create an empty database. Useful for merging."
    print "  \t-S, --grep-locations                 Find devices near this GPS location. Use % for pattern matching, like '%50.071%,14.402%' "
    print "  \t-A, --all-data                       Get all the data for all the devices in the database."

def db_create(database_name):
    """
    This function creates a new bluedriving database. 
    """
    global debug
    global verbose

    connection = ""

    try:
        # We check if the database exists
        if not os.path.exists(database_name):
            if debug:
                print 'Creating database'
            # Creating database
            connection = sqlite3.connect(database_name)
            # Creating tables
            connection.execute("CREATE TABLE Devices(Id INTEGER PRIMARY KEY AUTOINCREMENT, Mac TEXT , Info TEXT, Vendor TEXT)")
            connection.execute("CREATE TABLE Locations(Id INTEGER PRIMARY KEY AUTOINCREMENT, MacId INTEGER, GPS TEXT, FirstSeen TEXT, LastSeen TEXT, Address TEXT, Name TEXT, UNIQUE(MacId,GPS))")
            connection.execute("CREATE TABLE Notes(Id INTEGER, Note TEXT)")
            connection.execute("CREATE TABLE Alarms(Id INTEGER, Alarm TEXT)")
            connection.commit()
            connection.close()
            if debug:
                print 'Database created'
            return True
        else:
            if debug:
                print 'Database already exist. Choose a different name.'
            return False
    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_create(database_name) function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        x, y = inst # _getitem_ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        sys.exit(1)


def db_connect(database_name):
    """
    This function creates a connection to the database and return the connection
    """
    global debug
    global verbose

    connection = ""

    try:
        if not os.path.exists(database_name):
            return False
        connection = sqlite3.connect(database_name)
        if debug:
            print 'Database connection retrieved'
        return connection

    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_connect(database_name) function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        x, y = inst # _getitem_ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        sys.exit(1)

def db_count_devices(connection):
    """
    This function returns the amount of devices in table Devices
    """
    global debug
    global verbose

    try:
        result = connection.execute("SELECT count(*) FROM Devices")
        if result:
            result = result.fetchall()
            return result[0][0]
        else:
            return False

    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_count_devices(connection) function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        x, y = inst # _getitem_ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        sys.exit(1)

def db_locations_and_dates(connection,mac):
    """
    This function returns a set of Id, GPS, FSeen, LSeen, Name and Address, for a given mac.
    """
    global debug
    global verbose

    try:
        macId = db_get_id_from_mac(connection, mac)
        if macId:
            result = connection.execute("SELECT Id, GPS, FirstSeen, LastSeen, Name, Address FROM Locations WHERE MacId="+str(macId)+" ORDER BY FirstSeen ASC;")
            if result:
                result = result.fetchall()
                return result
            else:
                return False
        else:
            print 'The device seems not to be in the database. Please check the MAC address.'
            return False

    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_locations_and_dates(connection,mac) function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        x, y = inst # _getitem_ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        sys.exit(1)

def db_get_mac_from_id(connection, MacId):
    """
    Given a MacId this function returns the MAC address of it.
    """
    global debug
    global verbose

    try:
        result = connection.execute("SELECT Mac FROM Devices WHERE Id = "+str(MacId)+";")
        if result:
            result = result.fetchall()
            return result[0][0]
        else:
            return False

    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_get_mac_from_id(connection,MacId) function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        x, y = inst # _getitem_ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        sys.exit(1)

def db_get_id_from_mac(connection, Mac):
    """
    Given a MAC address this function returns the mac id 
    """
    global debug
    global verbose

    try:
        result = connection.execute("SELECT Id FROM Devices WHERE Mac = \""+str(Mac)+"\";")
        if result:
            result = result.fetchall()
            return result[0][0]
        else:
            return False

    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_get_id_from_mac(connection,mac) function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        x, y = inst # _getitem_ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        sys.exit(1)

def db_merge(db_merged_connection,db_to_merge_connection):
    """
    This function merges two databases into one
    """
    global debug
    global verbose

    count_dev = 0
    count_loc = 0
    count_ala = 0
    count_not = 0

    try:
        # Adding data from devices database
        try:
            result = db_to_merge_connection.execute("SELECT Id, Mac, Info FROM Devices")
        except:
            print "Exception in sql query: \"SELECT Id, Mac,Info FROM Devices\""
            sys.exit(0)
        devices = result.fetchall()
        for (MacId,Mac,Info) in devices:
            #result = db_merged_connection.execute("INSERT OR IGNORE INTO Devices (Mac,Info) VALUES(\"11:11:11:11:11:11\",\"[]\");")
            try:
                result= db_merged_connection.execute("INSERT OR IGNORE INTO Devices (Mac,Info) VALUES(\""+str(Mac)+"\",\""+str(Info[0])+"\");")
                count_dev = count_dev+1
            except:
                print 'Exception mergin this device: {}, {}'.format(Mac,Info[0])
                sys.exit(0)

            db_merged_connection.commit()

            #Adding data from locations table
            try:
                result = db_to_merge_connection.execute("SELECT MacId,GPS,FirstSeen,LastSeen,Address,Name FROM Locations WHERE MacId="+str(MacId)+";")
            except:
                print "Exception in sql query: \"SELECT MacId,GPS,FirstSeen,LastSeen,Address,Name FROM Locations WHERE MacId=\""
                sys.exit(0)
            locationinfo = result.fetchall()
            for (MacIdLoc,GPS,FSeen,LSeen,Address,Name) in locationinfo:
                # To avoid the errors when inserting in the db from old databases
                Address = Address.encode('utf-8').replace('"','').replace('<','').replace('>','').replace('/', '')
                Name = Name.encode('utf-8').replace('"','').replace('<','').replace('>', '').replace('/', '')
                if debug:
                    print '{} {} {} {} {} {}'.format(MacIdLoc,GPS,FSeen,LSeen,Address,Name)
                newMacId = db_get_id_from_mac(db_merged_connection,Mac)
                if debug:
                    print 'New macId: {}'.format(newMacId)
                try:
                    result = db_merged_connection.execute("INSERT OR IGNORE INTO Locations (MacId, GPS, FirstSeen, LastSeen, Address, Name) VALUES("+str(newMacId)+",\""+str(GPS)+"\",\""+str(FSeen)+"\",\""+str(LSeen)+"\",\""+str(Address)+"\",\""+str(Name)+"\");")
                except:
                    print "Exception in sql query: \"INSERT OR IGNORE INTO Locations (MacId, GPS, FirstSeen, LastSeen, Address, Name) VALUES(\""
                    print str(GPS)+","+str(FSeen)+","+str(LSeen)+","+str(Address)+","+str(Name).encode('utf-8')

                    sys.exit(0)
                count_loc = count_loc+1

            db_merged_connection.commit()

            #Adding data from notes table
            try:
                result = db_to_merge_connection.execute("SELECT Id,Note FROM Notes WHERE Id="+str(MacId)+";")
            except:
                print "Exeption in sql query: \"SELECT Id,Note FROM Notes WHERE Id=\""
                sys.exit(0)
            notesinfo = result.fetchall()
            for (Id,Note) in notesinfo:
                newMacId = db_get_id_from_mac(db_merged_connection,Mac)
                try:
                    result = db_merged_connection.execute("INSERT OR IGNORE INTO Notes (Id, Note) VALUES("+str(newMacId)+",\""+str(Note)+"\");")
                except:
                    print "Exception in sql query: \"INSERT OR IGNORE INTO Notes (Id, Note) VALUES(\""
                    sys.exit(0)
                count_not = count_not+1

            #Adding data from alarm table
            try:
                result = db_to_merge_connection.execute("SELECT Id,Alarm FROM Alarms WHERE Id="+str(MacId)+";")
            except:
                print "Error in sql query: \"SELECT Id,Alarm FROM Alarms WHERE MacId=\""
            notesinfo = result.fetchall()
            for (Id,alarm) in notesinfo:
                newMacId = db_get_id_from_mac(db_merged_connection,Mac)
                try:
                    result = db_merged_connection.execute("INSERT OR IGNORE INTO Alarms (Id, Alarm) VALUES("+str(newMacId)+",\""+str(alarm)+"\");")
                except:
                    print "Exception in sql query: \"INSERT OR IGNORE INTO Alarms (Id, Alarm) VALUES(\""
                    sys.exit(0)
                count_ala = count_ala+1

            if debug:
                print "Amount of devices processed: {}".format(count_dev)
                print "Amount of locations processed: {}".format(count_loc)
                print "Amount of notes processed: {}".format(count_not)
                print "Amount of alarms processed: {}".format(count_ala)

        db_merged_connection.commit()
        db_to_merge_connection.close()

    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_merge(database_name) function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        x, y = inst # _getitem_ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        sys.exit(1)

def db_list_devices(connection, limit):
    """
    This function returns a list of devices (macs). Variable limit can limit the results
    """
    global debug
    global verbose

    devices=""

    try:
        try:
            result = connection.execute("SELECT Mac FROM Devices LIMIT "+str(limit))
            devices = result.fetchall()
            return devices
        except:
            return False
    
    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_list_devices(connection) function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        x, y = inst # _getitem_ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        sys.exit(1)


def db_list_devices_and_names(connection, limit):
    """
    This function returns a list of MAC, Names of an amount of devices defined by the parameter limit.
    """
    global debug
    global verbose

    devices=""
    deviceswname=[]

    try:
        try:
            result = connection.execute("SELECT Id,Mac FROM Devices LIMIT "+str(limit))
            devices = result.fetchall()
            for dev in devices:
                name=""
                result = connection.execute("SELECT Name FROM Locations WHERE MacId=\""+str(dev[0])+"\" LIMIT 1") 
                name = result.fetchall()
                if not name:
                    print 'The device existed, but there are no locations for it. Maybe a broken merge.'
                    continue
                deviceswname.append([dev[1],name[0][0]])
                if debug:
                    print "{} - {} - {}".format(dev[0],dev[1],name[0][0])
            if debug:
                print deviceswname
            return deviceswname
        except:
            print "Exception in db_list_devices_and_names"
            return False
    
    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_list_devices_and_names(connection,limit) function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        x, y = inst # _getitem_ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        sys.exit(1)

def db_device_exists(connection, mac):
    """
    This function returns true if the given mac is stored on the database 
    """
    global debug
    global verbose

    device=""
    result=False

    try:
        try:
            result = connection.execute("SELECT Id FROM Devices WHERE Mac=\""+str(mac)+"\"") 
            if result:
                device = result.fetchall()
                if device:
                    return True
                else:
                    return False
            else:
                print "no result"
                return False
            
        except:
            print "Exception in db_device_exists"
            return False
    
    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_device_exists(connection) function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        x, y = inst # _getitem_ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        sys.exit(1)

def db_grep_names(connection,string):
    """
    This function returns devices which names are similar to the given string
    """
    global debug
    global verbose

    try:
        try:
            result = connection.execute("SELECT DISTINCT MacId,Name FROM Locations WHERE Name LIKE \"%"+str(string)+"%\"") 
            if result:
                result = result.fetchall()
                return result
            else:  
                return False
            
        except:
            print "Exception in db_grep_names()"
            return False
    
    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_grep_names(connection,string) function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        x, y = inst # _getitem_ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        sys.exit(1)

def db_update_address(connection,mac=False):
    """
    
    """
    global debug
    global verbose

    result = ""
    addr=""
    MacId=""
    GPS=""
    Address=""

    try:
            if mac:
                macid = db_get_id_from_mac(connection, mac)
                result = connection.execute("SELECT MacId,GPS,Address FROM Locations WHERE MacId="+str(macid)+";") 
            else:
                result = connection.execute("SELECT MacId,GPS,Address FROM Locations WHERE Address like \"NO ADDRESS RETRIEVED\" OR Address=\"\";") 
            if result:
                result = result.fetchall()
                print
                for (MacId,GPS,Address) in result:
                    if GPS != 'False':
                        if Address in ['NO ADDRESS RETRIEVED','']:
                            temp= getCoordinates(GPS)
                            temp= getCoordinates(str(GPS.strip("\'").strip("\'")))
                            addr = temp[1]
                            addr = addr.encode('utf-8')
                            result_update = connection.execute("UPDATE Locations SET Address=? WHERE MacId=? AND GPS=?;",(repr(addr),str(MacId),str(GPS))) 
                            print 'Updating {}'.format(mac)
                            print '   {} :: {} :: {}'.format(GPS, Address.encode('utf-8'), addr)
                        else:
                            print 'Address of the device already exists: {}'.format(mac)
                            print '   {} :: {}'.format(GPS, Address.encode('utf-8'))

                    else:
                        print 'No location stored for device {}'.format(mac)
                        print '   {} {} {}'.format(MacId, GPS, Address)
                    time.sleep(1)
                    print
            else:  
                print 'No results found with empty address to update.'
            connection.commit()
    
    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_update_address(connection,mac=False) function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        x, y = inst # _getitem_ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        sys.exit(1)


def db_grep_locations(connection,coordinates):
    """
    This function returns a list of mac, name and first seen of devices that are near the given coordinates.
    """
    global debug
    global verbose

    try:
        try:
            if debug:
                print "On db_grep_locations()"
                print "Coordinates to search: {}".format(coordinates)
            result = connection.execute("SELECT Name,MacId,FirstSeen,GPS FROM Locations WHERE GPS LIKE \""+str(coordinates)+"\";") 
            if result:
                result = result.fetchall()
                if debug:
                    print "Result:"
                    print result
                return result
            else:  
                if debug:
                    print 'Result is empty'
                return False
            
        except:
            print "Exception in db_grep_locations()"
            return False
    
    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_grep_locations(connection,coordinates) function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        x, y = inst # _getitem_ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        sys.exit(1)


def db_rank_devices(connection,limit):
    """
    This function returns a list of devices and the amount of times that were observed. Number of results is defined by limit.
    """
    global debug
    global verbose

    result = ""
    try:
        try:
            result = connection.execute("SELECT Name, MacId, count(MacId) as amount FROM Locations GROUP BY MacId ORDER BY amount DESC LIMIT "+str(limit)+" ;") 
            result = result.fetchall()
            
            if result:
                return result
            else:
                return False
        except:
            print "Exception in db_rank_devices()"
            return False
    
    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_rank_devices(connection,limit) function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        x, y = inst # _getitem_ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        sys.exit(1)


def db_remove_device(connection, mac):
    """
    This function removes a device from the database
    """
    global debug
    global verbose

    try:
        try:
            #Here we check that the device is present on the database
            exists = db_device_exists(connection, mac)
            if exists:
                    result = connection.execute("SELECT Id FROM Devices WHERE Mac=\""+str(mac)+"\" LIMIT 1")
                    id = result.fetchall()
                    id = id[0][0]
                    try:
                            result = connection.execute("DELETE FROM Locations WHERE MacId = "+str(id))
                    except:
                            if debug:
                                print "No rows affected"
                    try:
                            result = connection.execute("DELETE FROM Alarms WHERE Id = "+str(id))
                    except:
                            if debug:
                                print "No rows affected"
                    try:
                            result = connection.execute("DELETE FROM Notes WHERE Id = "+str(id))
                    except:
                            if debug:
                                print "No rows affected"
                    try:
                            result = connection.execute("DELETE FROM Devices WHERE Id = "+str(id))
                    except:
                            if debug:
                                print "No rows affected"
                    
                    connection.commit()

                    print "Checking if the deletion was efective"
                    result = connection.execute("SELECT Mac FROM Devices WHERE Id = "+str(id))
                    result = result.fetchall()
                    if not result:
                        print "\t[-] Deletion from Devices was effectve"
                    result = connection.execute("SELECT Id FROM Locations WHERE MacId = "+str(id))
                    result = result.fetchall()
                    if not result:
                        print "\t[-] Deletion from Locations was effectve"
                    result = connection.execute("SELECT Id FROM Alarms WHERE Id = "+str(id))
                    result = result.fetchall()
                    if not result:
                        print "\t[-] Deletion from Alarms was effectve"
                    result = connection.execute("SELECT Id FROM Notes WHERE Id = "+str(id))
                    result = result.fetchall()
                    if not result:
                        print "\t[-] Deletion from Notes was effectve"
        except:
            print "Exception in db_remove_device(connection,mac)"
            return False
    
    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_remove_device(connection,mac) function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        x, y = inst # _getitem_ allows args to be unpacked directly
        print 'x =', x
        print 'y =', y
        sys.exit(1)

def steam_vendors_names(vendor):
    """
    """
    try:
        global debug
        global verbose

        steamed_vendor = ''

        if 'samsung' in vendor.lower():
            steamed_vendor = 'Samsung'
        elif 'nokia' in vendor.lower():
            steamed_vendor = 'Nokia'
        elif 'parrot' in vendor.lower():
            steamed_vendor = 'Parrot'
        elif 'garmin' in vendor.lower():
            steamed_vendor = 'Garmin'
        elif 'ericsson' in vendor.lower():
            steamed_vendor = 'Ericsson'
        elif 'lg' in vendor.lower():
            steamed_vendor = 'LG'
        elif 'hon hai precision' in vendor.lower():
            steamed_vendor = 'Hon Hai Precision'
        elif 'apple' in vendor.lower():
            steamed_vendor = 'Apple'
        elif 'research in motion' in vendor.lower() or 'rim' in vendor.lower():
            steamed_vendor = 'RIM'
        elif 'motorola' in vendor.lower():
            steamed_vendor = 'Motorola'
        elif 'cisco' in vendor.lower():
            steamed_vendor = 'Cisco'
        else:
            steamed_vendor = vendor

        return steamed_vendor
   
    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in steam_vendors_names function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        sys.exit(1)


def db_update_vendor(connection, mac):
    """
    Get a mac and if its vendor is not in the db, look it up and update the db.
    """
    try:
        global debug
        global verbose
        import os

        
        if debug:
            print 'Updating vendor for mac {}'.format(mac)

        # Get the curent vendor for this mac
        try:
            ((vendor,),) = connection.execute("SELECT Vendor FROM Devices WHERE mac like '%" + mac + "%'")
        except :
            if debug:
                print 'There was no column vendor!! Maybe an old database? Add it manually.'
            exit(-1)


        # If there is no vendor, get it
        if vendor == None or vendor == '':
            if debug:
                print 'Getting the vendor from internet.'
            vendor = os.popen("wget -qO- 'http://www.coffer.com/mac_find/?string=" + mac + "'|grep -i 'class=\"Table2\"><a'|awk -F\"q=\" '{print $2}'|awk -F\> '{print $1}' |uniq").read().strip('\n').split('\n')[0][:-1] 
            if debug:
                print 'Vendor: {0}'.format(vendor)

            if debug:
                print 'Updating the database.'
            try:
                connection.execute("UPDATE Devices SET Vendor='" + str(vendor)+ "' WHERE mac like '%" + mac + "%'")
                connection.commit()
            except :
                if debug:
                    print 'There was no column vendor'
                exit(-1)

            # If you need to verify the writing
            #(vendor,) = connection.execute("SELECT Vendor FROM Devices WHERE mac like '%" + mac + "%'")
            #for a in vendor:
                #print a
        #elif vendor != (None,):
            #print vendor

        return vendor

    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in db_update_vendor function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        sys.exit(1)




def get_locations_and_dates(connection, mac):
    """
    Get a mac address and return all its locations, dates and vendor
    """
    try:
        global debug
        global verbose
        global quiet


        if debug:
            print '* In get locations and dates from device'
        addresslist = {}
        address = ""
        address_to_insert = ""

        locations_dates_results = db_locations_and_dates(connection,mac)

        # Update the mac vendor if it is not there.
        vendor = db_update_vendor(connection, str(mac))

        # Get the steamed version also
        steamed_vendor = steam_vendors_names(vendor)

        if not quiet:
            print "\tMAC Address: {0}. Vendor: {1}. Steamed Vendor: {2}".format(mac,vendor,steamed_vendor)

        # Get all the locations from the db for this mac
        for (Id,gps,fseen,lseen,name,address) in locations_dates_results:
            address = address.encode('utf-8')
            gps = str(gps)


            if debug:
                print '\n\n* This is the data that is currently being processed:'
                print '* Id: {}, GPS: {}, FirstSeen: {}, LastSeen: {}, Name: {}, Address: {}'.format(Id,gps,fseen,lseen,name,address)
                print


            #if (str(gps) != "False") or (str(gps) != ' ') or (str(gps) != 'GPS') or ('NO GPS' not in str(gps)):
            #if ( len(gps.split(',')) == 2 and len(gps.split(',')[0].split('.')) == 2 and len(gps.split(',')[1].split('.')) == 2 ):

            # Search for a proper gps position string using regular expresions
            import re
            gpspattern = re.compile('[0-9]+\.[0-9]+,[0-9]+\.[0-9]+')
            if ( gpspattern.search(gps) ):
                if debug:
                    print '* gps: {} is not \'False\' nor empty nor \'GPS\''.format(gps)
                    print 
                if ('NO ADDRESS' in address) or (len(address)<8):
                    if debug:
                        print '* address: {} is not \'NO ADDRESS\' nor empty'.format(address)
                        print
                    try:
                        address_to_insert = addresslist[gps]
                        if debug:
                            print '* Address to insert: {}'.format(address_to_insert)
                            print
                        print 'Address cached: {}'.format(address_to_insert)
                    except KeyboardInterrupt: 
                        print 'Exiting'
                        sys.exit(1)
                        break
                    except:
                        # This can be deleted. There is nothing here that is not a proper gps...
                        try:
                            gps.split(",")[1]
                        except:
                            print '\t\tNO GPS.'
                            print "\t\t\tIgnoring: {}: {}-{}, {} ({})".format(name, fseen, lseen, gps, str(address_to_insert))
                            break
                        #time.sleep(1)
                        a = gps
                        addr = getCoordinates(str(a.strip("\'").strip("\'")))
                        address_to_insert = addr[1]
                        address_to_insert = address_to_insert.encode('utf-8')
                        try:
                            addresslist[gps]=address_to_insert 
                        except:
                            print 'Cannot add new address to cache'
                    try:
                        if debug:
                            print '* Updating Locations table, setting address.'
                        if len(address_to_insert) > 5:
                                connection.execute("UPDATE Locations SET Address=\""+str(address_to_insert)+"\" WHERE Id="+str(Id))
                                connection.commit()
                                print "\t\t*{}: {}-{}, {} ({})".format(name, fseen, lseen, gps, str(address_to_insert))
                        else:
                                print '\t\tAddress content seems incorrect'
                                print "\t\t\tNot updating: {}: {}-{}, {} ({})".format(name, fseen, lseen, gps, str(address_to_insert))
                    except KeyboardInterrupt: 
                        print 'Exiting'
                        sys.exit(1)
                        break
                    except:
                        print "Exception updating device address"
                        print "{}".format(gps)
                        print "{}".format(address)
                        print "{}".format(address_to_insert)
                else:
                    if debug:
                        print 'Address already exists'
                    print "\t\t{}: {}-{}, {} ({})".format(name, fseen, lseen, gps, address)
            else:
                if debug:
                    print 'There is no GPS.'
                print "\t\t#{}: {}-{}, {} ({})".format(name, fseen, lseen, gps, address)


    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
        sys.exit(1)
    except Exception as inst:
        print 'Exception in get_locations_and_dates() function'
        print 'Ending threads, exiting when finished'
        print type(inst) # the exception instance
        print inst.args # arguments stored in .args
        print inst # _str_ allows args to printed directly
        sys.exit(1)





def main():
    """
    manageDB.py is a tool that allows to query and manage the database generated by bluedriving. Use -h for help.
    """
    global debug
    global verbose
    global quiet

    database=""
    connection=""
    get_devices=""
    get_devices_with_names=""
    device_mac=""
    device_exists = False
    remove_device = False
    grep_names = False
    rank_devices = False
    ranking=""
    limit=99999999
    merge_db=False
    db_to_merge=""
    db_count=False
    create_db=False
    locations_and_dates=False
    grep_locations=False
    coordinates=""
    update_address=False

    try:

        # By default we crawl a max of 5000 distinct URLs
        opts, args = getopt.getopt(sys.argv[1:], "hDd:l:enE:R:g:r:qm:Cc:L:S:A", ["help","debug","database-name=","limit=","get-devices","get-devices-with-names","device-exists=","remove-device=","grep-names=","rank-devices=","quiet","merge-with=","count-devices","create-db=","get-locations-with-dates=","grep-locations=","all-data"])
    except:
        usage()
        exit(-1)

    for opt, arg in opts:
        if opt in ("-h", "--help"): usage(); sys.exit()
        if opt in ("-D", "--debug"): debug = True
        if opt in ("-d", "--database"): database = arg
        if opt in ("-l", "--limit"): limit = arg
        if opt in ("-e","--get-devices"): get_devices = True
        if opt in ("-n","--get-devices-with-names"): get_devices_with_names = True
        if opt in ("-E","--device-exists"): device_mac = arg; device_exists=True
        if opt in ("-R","--remove-device"): device_mac = arg; remove_device=True
        if opt in ("-g","--grep-names"): string = arg; grep_names=True
        if opt in ("-r","--rank-devices"): limit = arg; rank_devices=True
        if opt in ("-q","--quiet-devices"): quiet=True
        if opt in ("-m","--merge-with"): db_to_merge=arg; merge_db=True
        if opt in ("-C","--count-devices"): db_count=True
        if opt in ("-c", "--create-db"): database = arg; create_db=True
        if opt in ("-L", "--get-locations-with-dates"): mac = arg; locations_and_dates=True
        if opt in ("-S", "--grep-locations"): coordinates = arg; grep_locations=True
        if opt in ("-A", "--all-data"): all_data = True

    try:
        if create_db:
            result = db_create(database)
            if result:
                print '[+] Database created'
            else:
                print '[+] Database not created'
            sys.exit()

        if database:
            if not quiet:
                version()
                print "[+] Database: {}".format(database)
            import os
            if not os.path.isfile(database):
                print 'The database does not exists.'
                exit(-1)
            connection = db_connect(database)

            if connection:
                if not quiet:
                    print "[+] Connection established"

                #List devices
                if get_devices:
                    devices = db_list_devices(connection, limit)
                    if devices:
                        if not quiet:
                            print "[+] List of devices in the database:"
                        for key in devices:
                            print "\t{}".format(key[0])
                # List devices with name
                elif get_devices_with_names:
                    deviceswnames= db_list_devices_and_names(connection,limit)
                    if deviceswnames:
                        for (mac,name) in deviceswnames:
                            print "\t{} - {}".format(mac,name)
                elif device_exists:
                    exists = db_device_exists(connection,device_mac)
                    if exists:
                        print "\tDevice {} exists in the database".format(device_mac)
                    else:
                        print "\tDevice {} is not present in the database".format(device_mac)
                elif remove_device:
                    db_remove_device(connection,device_mac)
                    exists = db_device_exists(connection,device_mac)
                    if exists:
                        print "\tDevice {} exists in the database".format(device_mac)
                    else:
                        print "\tDevice {} is not present in the database".format(device_mac)
                elif grep_names:
                    similar_names = db_grep_names(connection,string)
                    if similar_names:
                        for (macId,name) in similar_names:
                            mac = db_get_mac_from_id(connection,macId)
                            print "\t{} | {}".format(mac, name)
                elif rank_devices:
                    ranking = db_rank_devices(connection,limit)
                    if ranking:
                        for (name,macId,count) in ranking:
                            mac = db_get_mac_from_id(connection,macId)
                            print "\t{} - {} ({})".format(count, name, mac)
                elif merge_db:
                    db_to_merge_connection = db_connect(db_to_merge)
                    db_merge(connection,db_to_merge_connection)
                elif db_count:
                    number_of_devices = db_count_devices(connection)
                    print '\tNumber of devices on the database: {}'.format(number_of_devices)

                elif locations_and_dates:
                    # Get all the Locations and dates from the devices
                    get_locations_and_dates(connection, mac)

                elif grep_locations:
                    locations = db_grep_locations(connection,coordinates)
                    if locations:
                        for (name,macid,fseen,gps) in locations:
                            mac = db_get_mac_from_id(connection,macid)
                            print ' {}::{} {} {}'.format(mac,name,fseen,gps)
                elif all_data:
                    
                    # Get all the macs
                    if debug:
                        print 'Getting all the information from all the macs'
                    result = connection.execute("SELECT Mac FROM Devices")
                    # Get the data for all the macs
                    for mac in result:
                        (mac,) = mac
                        get_locations_and_dates(connection, mac)

                else:
                    print "Nothing to do. Please select an option."

                if connection: 
                    connection.commit()
                    connection.close()
                    if not quiet:
                        print "[+] Connection closed"

            else:
                print "A connection to the database could not be retrieved"
        else:
            print "You have to select a database. Use the -d option or -h for help."

    except KeyboardInterrupt:
        print 'Exiting. It may take a few seconds.'
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


