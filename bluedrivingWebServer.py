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


def uniquify(seq, idfun=None): 
    """ fastes way to uniquify an array"""
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result


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
		info = {}

		top['Info'] = info

		#for row in cursor.execute('SELECT * FROM details WHERE mac == ?',mac):
			#print row

		return je.encode(top)



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


def get_n_positions(n):
	""" Get the n last positions of every MAC in the database """
	global debug

	try:
		conn = sqlite3.connect('bluedriving.db')
		cursor = conn.cursor()


		# Get all the macs into an array
		temp_macs = []
		uniq_macs = []
		for row in cursor.execute('SELECT MAC FROM devices ORDER BY MAC'):
			temp_macs.append(str(row[0]))

		uniq_macs = uniquify(temp_macs)
		if debug:
			print ' >> Unique macs: {0}'.format(uniq_macs)


		# Encoder
		je = json.JSONEncoder()
		
		# Example
		# { "map": [ 
		#		{ "MAC":"00:11:22:33:44:55", 
		#			"pos": [ 					// Called pos_vect below
		#					"gps":"-21.0001 -32.0023", 	// Called gps_data below
		#					"gps":"-44.5423 -56.65544" 
		#				] }, 
		#		{}, // Each of this is called data below
		#		{}, 
		#		{} 
		#	   ] } 

		# Top stores everythin
		top = {}

		# Map is the vector of name 'Map'
		map = []

		# Link the map vector with the name 'Map'
		top['Map'] = map

		# For each mac, obtain the last n positions
		for mac in uniq_macs:
			#if debug:
				#print ' >> Asking for mac: {0}'.format(mac)

			# Data holds information for each mac with all its positions
			data = {}
			data['MAC'] = mac

			pos_vect=[]
			data['pos'] = pos_vect

			# gps_data holds all the gps info for a given mac
			gps_data = {}

			askmac = ('%'+mac+'%',n)

			# Flag to know if this mac has at least one position and avoid returning an empty position vector.
			no_gps_at_all = True
			for row in cursor.execute("SELECT * FROM devices WHERE mac like ? ORDER BY LastSeen DESC limit 1,?",askmac):
				gps = row[5]
				#print gps
				if 'not available' not in gps and gps != '':
					no_gps_at_all = False
					gps_data['gps'] = gps
					pos_vect.append(gps)
					if debug:
						print ' >> MAC {0} has position: {1}'.format(mac,gps)

			if no_gps_at_all:
				if debug:
					print ' >> MAC {0} has no gps position at all.'.format(mac)
				# This avoids adding an empty data to the map results.
				continue

			# Store the info of all the positions of one mac
			map.append(data)


		return je.encode(top)





	except Exception as inst:
		if debug:
			print '\tget_n_positions()'
		print type(inst)     # the exception instance
		print inst.args      # arguments stored in .args
		print inst           # __str__ allows args to printed directly
		x, y = inst          # __getitem__ allows args to be unpacked directly
		print 'x =', x
		print 'y =', y
		exit(-1)


def add_note_to(mac,note):
	""" Get a MAC and a note and add the note to the database """
	import re
	global debug

	try:
		# Replace + with spaces.
		note = note.replace('+', ' ')

		# verify the data types
		try:
			# Are they strings?
			if type(mac) != str or type(note) != str:
				if debug:
					print ' >> Some strange attempt to hack the server:1'
				return ''
		        # Is the format ok?
			if len(mac.split(':')) != 6 or len(mac) != 17:
				if debug:
					print ' >> Some strange attempt to hack the server:2'
				return ''
		        # Is the len of the noteok?
			if len(note) > 255:
				if debug:
					print ' >> Some strange attempt to hack the server:4'
				return ''
			# Characters fot the mac
			if not re.match('^[a-fA-F0-9:]+$',mac):
				if debug:
					print ' >> Some strange attempt to hack the server:4'
				return ''
			# Characters fot the note
			if not re.match('^[a-zA-Z0-9 ]+$',note):
				if debug:
					print ' >> Some strange attempt to hack the server:5'
				return ''
		except Exception as inst:
			if debug:
				print ' >> Some strange attempt to hack the server.6'
			print type(inst)     # the exception instance
			print inst.args      # arguments stored in .args
			print inst           # __str__ allows args to printed directly
			x, y = inst          # __getitem__ allows args to be unpacked directly
			print 'x =', x
			print 'y =', y
			return ''

		# We are hopefully safe here...
		if debug:
			print ' >> We are safe'

		# Search fot that mac on the database first...
		conn = sqlite3.connect('bluedriving.db')
		cursor = conn.cursor()
		askmac = ('%'+mac+'%',)

		row = cursor.execute("SELECT * FROM devices WHERE mac like ? limit 1,1",askmac)

		# Does this mac exists?
		if len(row.fetchall()) == 0:
			if debug:
				print ' >> This mac does not exist'
			return ''
			
		cursor = conn.cursor()

		# Try to insert
		try:
			cursor.execute("INSERT INTO Details (Mac,Note) values (?,?) ",(mac,note))
			conn.commit()
			if debug:
				print ' >> Inserted values. Mac: {0}, Note:{1}'.format(mac,note)
			conn.close()
		except Exception as inst:
			if debug:
				print ' >> Some problem inserting in the database in the funcion add_note_to()'
			print type(inst)     # the exception instance
			print inst.args      # arguments stored in .args
			print inst           # __str__ allows args to printed directly
			x, y = inst          # __getitem__ allows args to be unpacked directly
			print 'x =', x
			print 'y =', y
			return ''

		return 'Ok'


	except Exception as inst:
		if debug:
			print '\tadd_note_to()'
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
		note = ""
		try:
			if debug:
				print ' >> Path: {0}'.format(self.path)

			# Return the basic info about the MACs since last request
			if self.path == '/data':
				if debug:
					print ' >> Get /data'
				# Get the unread registers from the DB since last time
				json_to_send = get_unread_registers()

				#json_to_send = json.dumps("{'test': Yes}")

				self.send_response(200)
				self.send_header('Content-Type',        'text/html')
				self.end_headers()
				self.wfile.write(json_to_send)

			# Get a MAC and add a note in the database 
			elif self.path.rfind('/note?mac=') == 0: # and self.path.find("note=") > 0:
				if debug:
					print ' >> Get /note'
				mac = str(self.path.split('mac=')[1].split('&')[0])
				note = str(self.path.split('note=')[1])
				json_to_send = add_note_to(mac,note)

				self.send_response(200)
				self.send_header('Content-Type',        'text/html')
				self.end_headers()
				self.wfile.write(json_to_send)

			# Get a MAC and return all the info about that MAC
			elif self.path.rfind('/info?mac=') == 0:
				if debug:
					print ' >> Get /info'
				
				mac = self.path.split('mac=')[1]
				json_to_send = get_info_from_mac(mac)

				self.send_response(200)
				self.send_header('Content-Type',        'text/html')
				self.end_headers()
				self.wfile.write(json_to_send)

			# Get an X amount and return for every MAC the last X positions.
			elif self.path.rfind('/map?amount=') == 0:
				if debug:
					print ' >> Get /map'

				n = self.path.split('amount=')[1]

				json_to_send = get_n_positions(int(n))

				self.send_response(200)
				self.send_header('Content-Type',        'text/html')
				self.end_headers()
				self.wfile.write(json_to_send)

			elif self.path == "/":
				if debug:
					print ' >> Get /'
				# Return the index.html
				file = open(curdir + sep + 'index.html')

				temp_read = file.read()
				file_len = len(temp_read)

				self.send_response(200)
				self.send_header('Content-Type','text/html; charset=UTF-8')
				self.send_header('Content-Length',file_len)
				self.end_headers()

				self.wfile.write(temp_read)
				file.close()


			elif self.path != "/":
				# Read files in the directory
				if debug:
					print ' >> Get generic file'

				try:
					extension = self.path.split('.')[1]
				except:
					# Does not have . on it...
					self.send_response(200)
					return


				self.send_response(200)

				if extension == 'css':
					file = open(curdir + sep + self.path)
					temp_read = file.read()
					file_len = len(temp_read)
					self.send_header('Content-Type','text/css')
					self.send_header('Content-Length',file_len)
					self.end_headers()

				elif extension == 'png':
					file = open(curdir + sep + self.path)
					temp_read = file.read()
					file_len = len(temp_read)
					self.send_header('Content-Type','image/png')
					self.send_header('Content-Length',file_len)
					self.end_headers()

				elif extension == 'js':
					file = open(curdir + sep + self.path)
					temp_read = file.read()
					file_len = len(temp_read)
					self.send_header('Content-Type','text/javascript')
					self.send_header('Content-Length', file_len)
					self.end_headers()

				elif extension == 'html':
					file = open(curdir + sep + self.path)
					temp_read = file.read()
					file_len = len(temp_read)
					self.send_header('Content-Type','text/html; charset=UTF-8')
					self.send_header('Content-Length',file_len)
					self.end_headers()
				else:
					self.send_header('Content-Type','text/html; charset=UTF-8')
					self.send_header('Content-Length','9')
					self.end_headers()
					self.wfile.write('Hi there.')
					return

				self.wfile.write(temp_read)
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
	    if opt in ("-h", "--help"): usage();exit(-1)
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
