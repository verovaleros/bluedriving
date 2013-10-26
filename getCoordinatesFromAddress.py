#! /usr/bin/env python
#  Copyright (C) 2009  Veronica Valeros
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
# Author: Veronica Valeros, vero () valeros () gmail () com
#
# Changelog

# Description
# This little scripst receives an address and gets the coordinates using a Google Maps API



# standard imports
import os, pwd, string, sys
import getopt
import re
import urllib2
try:
    import simplejson
except:
    print 'Library needed. apt-get install python-simplejson'
    exit(-1)



####################
# Global Variables
vernum = 0.1
#########


# Print version information and exit
def version():
  print "+----------------------------------------------------------------------+"
  print "| getCoordinatesFromAddress.py Version "+ str(vernum) +"                             |"
  print "| This program is free software; you can redistribute it and/or modify |"
  print "| it under the terms of the GNU General Public License as published by |"
  print "| the Free Software Foundation; either version 2 of the License, or    |"
  print "| (at your option) any later version.                                  |"
  print "|                                                                      |"
  print "| Author: Veronica Valeros - vero () valeros () gmail () com           |"
  print "+----------------------------------------------------------------------+"
  print


# Print help information and exit:
def usage():
  print "+----------------------------------------------------------------------+"
  print "| getCoordinatesFromAddress.py Version "+ str(vernum) +"                             |"
  print "| This program is free software; you can redistribute it and/or modify |"
  print "| it under the terms of the GNU General Public License as published by |"
  print "| the Free Software Foundation; either version 2 of the License, or    |"
  print "| (at your option) any later version.                                  |"
  print "|                                                                      |"
  print "| Author: Veronica Valeros - vero () valeros () gmail () com           |"
  print "+----------------------------------------------------------------------+"
  print "\nusage: %s <options>" % sys.argv[0]
  print "options:"
  print "  -h, --help           Show this help message and exit"
  print "  -V, --version        Output version information and exit"
  print "  -v, --verbose        Output more information."
  print "  -D, --debug          Debug. In debug mode the statistics run live."
  print "  -a, --address        Address or coordinates between quotes. Ex: \"1600 Amphitheatre Parkway, Mountain View, Canada\"."
  print
  sys.exit(1)




# funtions here
def getCoordinates(address):
	global debug
	global verbose

	api_url = "http://maps.google.com/maps/api/geocode/json?sensor=false&address="
	query = ""
	answer = ""
	lat = ""
	lng = ""
	content = "" 
	coordinates = ""
	formattedaddress = ""

	try:
            # We verify the given address
            try:
                # Type
                if type(address) != str:
                    return 'Bad format. The given address is not a string. Do you used quotes?'
                # Format
                if len(address.split(',')) < 2 or len(address.split(',')) > 4:
                        return 'Bad address. Remember that the address should be like: \"Street number Street, City, Country\"'
                # Length of the address
                if len(address) > 255:
                    return 'Too long. The address is too long, request ignored.'
                # Characters accepted
                if not re.match('^[a-zA-Z0-9, .-]+$',address):
                    return 'Bad sintax. Unaccepted characters found in address. Try again.'
            
                address = address.rstrip(' ').strip(' ').replace(' ','+')
                query = api_url+address
                
                try:
                    answer = urllib2.urlopen(query)
                    content = simplejson.load(answer)
                    lat = content['results'][0]['geometry']['location']['lat']
                    lng = content['results'][0]['geometry']['location']['lng']
                
                    coordinates = str(lat)+','+str(lng)
                    formattedaddress = content['results'][0]['formatted_address']
                    return [coordinates,formattedaddress]
                except:
                    return [" "," "]
			
            except Exception, e:
                print "misc. exception (runtime error from user callback?):", e
                return [" "," "]

	except Exception, e:
		print "misc. exception (runtime error from user callback?):", e
		sys.exit(1)
	except KeyboardInterrupt:
		sys.exit(1)




def main():
        try:
                global debug
                global verbose

                address=""

		opts, args = getopt.getopt(sys.argv[1:], "VvDha:", ["help","version","verbose","debug","address="])
        except getopt.GetoptError: usage()

        for opt, arg in opts:
            if opt in ("-h", "--help"): usage()
            if opt in ("-V", "--version"): version();exit(-1)
            if opt in ("-v", "--verbose"): verbose=True
            if opt in ("-D", "--debug"): debug=True
	    if opt in ("-a", "--address"): address=arg
        try:
                try:
			if address:
				version()
				[coordinates,address] = getCoordinates(address)
				if coordinates or address: 
					print '[+] Location found: '
					if address: 
						print '\t '+address
					else: 
						print '\t No address found'
					if coordinates: 
						print '\t '+coordinates
					else:
						print '\t Not coordinates found.'
				else:
					print '\t Not address nor coordinates found.'
				print 
				print
                        else:
                                usage()
                                sys.exit(1)
                except Exception, e:
                        print "misc. exception (runtime error from user callback?):", e
                except KeyboardInterrupt:
                        sys.exit(1)
        except KeyboardInterrupt:
                # CTRL-C pretty handling.
                print "Keyboard Interruption!. Exiting."
                sys.exit(1)


if __name__ == '__main__':
    main()

