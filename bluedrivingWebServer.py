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
#import os, pwd
#from stat import *
#import types
#from datetime import datetime
#from time import mktime
#from time import strptime
#import logging
#from subprocess import Popen
#from subprocess import PIPE
#import shlex
#import copy
#from pyevolve import *
#import IPy
import getopt
import sys
import BaseHTTPServer
#from SimpleHTTPServer import SimpleHTTPRequestHandler
#from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep
import simplejson as json

####################
# Global Variables

# Debug
debug=0
vernum="0.1"



# Print version information and exit
def version():
  print "+----------------------------------------------------------------------+"
  print "| bludrivingWebServer.py Version "+ vernum +"                                      |"
  print "| This program is free software; you can redistribute it and/or modify |"
  print "| it under the terms of the GNU General Public License as published by |"
  print "| the Free Software Foundation; either version 2 of the License, or    |"
  print "| (at your option) any later version.                                  |"
  print "|                                                                      |"
  print "| Author:                                                              |"
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
  print "| Author:                                                              |"
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



class MyHandler (BaseHTTPServer.BaseHTTPRequestHandler):

	def do_GET(self):
		try:
			json_to_send = json.dumps("{'test': Yes}")
			self.send_response(200)
			self.send_header('Content-Type',        'text/hml')
			self.end_headers()
			#self.wfile.write(file.read())
			self.wfile.write(json_to_send)
			#file.close()
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
