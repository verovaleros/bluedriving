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

# Global Variables
vernum = '0.1'


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

# standard imports
import os, pwd, string, sys
from stat import *
import getopt
import types
#from datetime import datetime
#from time import mktime
#from time import strptime
import logging
#from subprocess import Popen
#from subprocess import PIPE
#import shlex
#import copy
#from pyevolve import *
#import IPy


####################
# Global Variables

# Debug
debug=0

vernum="0.1"














def main():
	try:
		global debug

		opts, args = getopt.getopt(sys.argv[1:], "VvDh", ["help","version","verbose","debug"])
	except getopt.GetoptError: usage()

	for opt, arg in opts:
	    if opt in ("-h", "--help"): usage()
	    if opt in ("-V", "--version"): version();exit(-1)
	    if opt in ("-v", "--verbose"): verbose=True
	    if opt in ("-D", "--debug"): debug=1
	try:

		try:
			if True:
				usage()
				sys.exit(1)

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
