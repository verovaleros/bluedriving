#! /usr/bin/env python
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
# Sebastian Garcia eldraco@gmail.com
#
# Changelog

#
# TODO

#
# KNOWN BUGS

#
# Description
# Web server for the bludriving.py
#
#


# Standard imports
import getopt
import sys
import BaseHTTPServer
from os import curdir, sep
import simplejson as json
import sqlite3
import copy

####################
# Global Variables

# Debug
debug=0
vernum="0.1"
unread_index = -1
####################



# Print version information and exit
def version():
  print "+----------------------------------------------------------------------+"
  print "| bludrivingWebServer.py Version "+ vernum +"                                      |"
  print "| This program is free software; you can redistribute it and/or modify |"
  print "| it under the terms of the GNU General Public License as published by |"
  print "| the Free Software Foundation; either version 2 of the License, or    |"
  print "| (at your option) any later version.                                  |"
  print "|                                                                      |"
  print "| Author: Sebastian Garcia, eldraco@gmail.com                          |"
  print "| Mateslab Hackspace, www.mateslab.com.ar                              |"
  print "+----------------------------------------------------------------------+"
  print


# Print help information and exit:
def usage():
  print "+----------------------------------------------------------------------+"
  print "| bludrivingWebServer.py Version "+ vernum +"                                      |"
  print "| This program is free software; you can redistribute it and/or modify |"
  print "| it under the terms of the GNU General Public License as published by |"
  print "| the Free Software Foundation; either version 2 of the License, or    |"
  print "| (at your option) any later version.                                  |"
  print "|                                                                      |"
  print "| Author: Sebastian Garcia, eldraco@gmail.com                          |"
  print "| Mateslab Hackspace, www.mateslab.com.ar                              |"
  print "+----------------------------------------------------------------------+"
  print "\nusage: %s <options>" % sys.argv[0]
  print "options:"
  print "  -h, --help         	Show this help message and exit"
  print "  -V, --version        Show the version"
  print "  -v, --verbose        Be verbose"
  print "  -D, --debug        Debug"
  print "  -p, --port        Web server tcp port to use"


def createWebServer(port):
	""" Crate a web server """

	global debug
	# By default bind to localhost
	server_address = ('127.0.0.1', port)

	# Create a webserver
	try:
		httpd = BaseHTTPServer.HTTPServer(server_address, MyHandler)
		# Get the socket
		sa = httpd.socket.getsockname()

		print "Serving HTTP on", sa[0], "port", sa[1], "..."

		# Run forever
		httpd.serve_forever()
	except KeyboardInterrupt:
		print ' Received, shutting down the server.'
		httpd.socket.close()


def get_unread_registers():
	""" Get unread registers from the database since the last read and return a json with all the data"""
	try:

		global unread_index
		global debug
		conn = sqlite3.connect('bluedriving.db')
		cursor = conn.cursor()
		id = (unread_index,)

		# Encoder
		je = json.JSONEncoder()

		top = {}
		array = []

		top['UnReadData'] = array

		for row in cursor.execute('SELECT * FROM devices WHERE Id > ?',id):
			dict = {}

			# ID
			dict['id'] = row[0]
			# MAC
			dict['mac'] = row[1]
			# Name
			dict['name'] = row[2]
			# FirstSeen
			dict['firstseen'] = row[3]
			# LastSeen
			dict['lastseen'] = row[4]
			# Global position
			dict['gps'] = row[5]

			
			array.append(dict)

		try:
			unread_index = row[0]
		except UnboundLocalError:
			pass

		return je.encode(top)

	except Exception as inst:
		if debug:
			print '\tError on get_unread_registers()'
		print type(inst)     # the exception instance
		print inst.args      # arguments stored in .args
		print inst           # __str__ allows args to printed directly
		x, y = inst          # __getitem__ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		exit(-1)




def get_info_from_mac(temp_mac):
	""" Get info from one mac """
	global debug

	try:
		conn = sqlite3.connect('bluedriving.db')
		cursor = conn.cursor()
		mac = (temp_mac,)

		# Encoder
		je = json.JSONEncoder()

		# {"Info" : {"ID":0, "MAC":"00:11:22:33:44:55", "Name":"Test", } }

		top = {}
		array = []

		top['Info'] = array

		for row in cursor.execute('SELECT * FROM details WHERE mac == ?',mac):
			print row



	except Exception as inst:
		if debug:
			print '\tError on get_info_from_mac()'
		print type(inst)     # the exception instance
		print inst.args      # arguments stored in .args
		print inst           # __str__ allows args to printed directly
		x, y = inst          # __getitem__ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		exit(-1)




class MyHandler (BaseHTTPServer.BaseHTTPRequestHandler):
	""" Handle the requests """
	def do_GET(self):
		global debug
		try:
			if debug:
				print ' >> Path: {0}'.format(self.path)

			# Return the index.html

			# Return the basic info about the MACs since last request
			if self.path == "/data":
				# Get the unread registers from the DB since last time
				json_to_send = get_unread_registers()

				#json_to_send = json.dumps("{'test': Yes}")

				self.send_response(200)
				self.send_header('Content-Type',        'text/html')
				self.end_headers()
				self.wfile.write(json_to_send)

			# Get a MAC and return all the info about that MAC
			elif self.path.rfind("/info?mac=") == 0:
				
				mac = self.path.split('mac=')[1]
				json_to_send = get_info_from_mac(mac)

				self.send_response(200)
				self.send_header('Content-Type',        'text/html')
				self.end_headers()
				self.wfile.write(json_to_send)

			# Get an X amount and return for every MAC the last X positions.
			elif self.path.rfind("/map?amount=") == 0:

				json_to_send = json.dumps("{'map': amount}")

				self.send_response(200)
				self.send_header('Content-Type',        'text/html')
				self.end_headers()
				self.wfile.write(json_to_send)

			else:
				# Read files in the directory
				extension = self.path.split('.')[1]

				self.send_response(200)

				if extension == 'css':
					self.send_header('Content-Type','text/css')
					self.send_header('Content-Length','400000')
					self.end_headers()

				elif extension == 'png':
					self.send_header('Content-Type','image/png')
					self.send_header('Content-Length','400000')
					self.end_headers()

				elif extension == 'js':
					self.send_header('Content-Type','text/javascript')
					self.send_header('Content-Length','400000')
					self.end_headers()

				elif extension == 'html':
					self.send_header('Content-Type','text/html; charset=UTF-8')
					self.send_header('Content-Length','400000')
					self.end_headers()

				file = open(curdir + sep + self.path)
				self.wfile.write(file.read())
				file.close()

			return


		except IOError:
			self.send_error(404,'File Not Found: {0}'.format(self.path))







def main():
	try:
		global debug
		# Default port to use
		port = 8000

		opts, args = getopt.getopt(sys.argv[1:], "VvDh", ["help","version","verbose","debug","port"])
	except getopt.GetoptError: usage()

	for opt, arg in opts:
	    if opt in ("-h", "--help"): usage()
	    if opt in ("-V", "--version"): version();exit(-1)
	    if opt in ("-v", "--verbose"): verbose=True
	    if opt in ("-D", "--debug"): debug=1
	    if opt in ("-p", "--port"): port=int(arg)
	try:

		try:
			if True:
				createWebServer(port)
				

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
