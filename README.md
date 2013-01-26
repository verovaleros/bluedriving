Bluedriving
-----------

Version 0.11. Nov 2012.

What
----
Bluedriving is a bluetooth wardriving utility. It can capture bluetooth devices, lookup their services, get GPS information and present everything in a nice web page. It can search for and show a lot of information about the device, the GPS address and the historic location of devices on a map.
The main motivation of this tool is to research about the targeted surveillance of people by means of its cellular phone or car.
With this tool you can capture information about bluetooth devices and show, on a map, the points where you have seen the same device in the past.
For the moment it only runs on linux.

Authors: verovaleros, eldraco, nanojaus

Main Features
-------------
- Scan bluetooth devices.
- Lookup services on each device.
- Use threads to speed up the process.
- Stores everything in a sqlite database.
- Has a stand-alone python web server that implements an API. It can be started by the bludriving.py tool or by using the bluedrivingWebServer.py tool. 
- Has sounds for:
 -- GPS signal activation.
 -- New device found.
 -- Old device found.
 -- System Running and no GPS.
 -- System Running and GPS.
 -- Sound for devices with the sound alarm setted.
- Implements alarm notifications for the bluetooth devices that you want: 
 -- Play a sound
 -- Read the bluetooth name with festival
 -- Send an Email with the device information.
- You can manually specify the GPS coordinates, so you can have the GPS and location functionality without having a GPS. This is very usefull is you are not moving but want to record the position.
- Interactive keys while running (key+Enter) to :
 -- a (activate or deactivate alarms)
 -- s (activate or deactivate sounds)
 -- l (activate or deactivate lookup devices)
 -- d (activate or deactivate debugging)
 -- i (activate or deactivate internet for searching the real address of the GPS information)
 -- i (activate or deactivate GPS)
 -- q (quit)
- Has a beautiful web page listening on localhost:8000, that lets you:
 -- See all the bluetooth devices ordered by last seen position. The list updates itself every 3 seconds.
 -- See each device information, including a map with the position you are inspecting.
 -- Set/unset a permanent note on the device, stored on the database.
 -- Set/unset a permanent alarm on the device, stored on the database.
 -- See all the history of positions for the selected device in a large map.
 -- See the positions of the last N devices together in a map, so you can see all at the same time.
- It shows the amount of different locations and devices in the table.
- It can update the system state in the web page automatically. When it is down and when it comes back.

Poor man GPS solution
---------------------
This tool lets you have a GPS location without having a GPS signal. You can use the -f option to set a google map coordinate like this -f "35.685307,139.779765". In this way all the bluetooth devices are going to be recorded on that position. It is very useful if you are at home or at some static point with internet (to get the coordinates) but without GPS.
On future versions we plan to have a manual GPS method to change your position while moving on a car without having a GPS.
Remember that the usefulness of the project is to have a location for the devices.
By default the tool tries to get GPS information from gpsd continually.

Stand-alone web server
----------------------
The web server was separated to help visualize the data without capturing more devices. If you want to analyze a previous database, or analyze the data off line, you can start the webs erver alone.

Using multiples bluetooth dongles
----------------------------------
Unfortunately, the bluetooth libraries does not allow us to select the bluetooth device you want to use. So, if you use an external bluetooth device, we recommend you to switch off all the wireless capabilities of you computer (using the hardware or software switch), to plug the new external bluetooth device and then to reenable the wireless capabilities. In this way your external bluetooth device will be the hci0 device. (You can check with hciconfig)

Alarms and notes
----------------
Alarms and notes are stored in the database. Every time a device is seen, the alarms for that device are checked. If a sound alarm is found, a nice sound is played. If a festival alarm is found, the device name is read with festival. If a mail alarm is found, a mail with the device information is sent to the specified mail address (-m option) from the same mail address. This is done by using your gmail account. In this way, gmail allow you to send mail without problems. Note that the bluedriving tool does no communicate or store the mail or password. This data is for the session only and totally private.
Alarms are meant to tell you when a certain device was seen again. For example, you can set an alarm on your friend device to know if he enters the same bar as you later!
Notes are meant to add your own information to any device. Perhaps you know the exact name of the person using that device.


Usage 
-----
Usage: ./bluedriving.py <options>
-h, --help                    
	Show this help message and exit.                    
                    
-D, --debug                    
	Debug mode ON. Prints debug information on the screen.                    
                    
-d, --database-name                    
	Name of the database to store the data. The default database name is bluedriving.db.                    
                    
-w, --webserver                    
	It runs a local webserver (127.0.0.1:8000) to visualize and interact with the collected information.                     
                    
-s, --not-sound                    
	Turn sound off.     
                    
-i, --not-internet                    
	Turn off address resolve module.                     
	By default, if gps is activated, the program tries to get the real address from the coordinates of the current position.  This is very useful to have an idea of where have you been walking.                     
	If you do not have internet use this option to save time on the discovering.                    
                    
-l, --not-lookup-services                       
	Turn off lookup devices services. Use this option to not lookup for services for each device.                                                            
                    
-g, --not-gps                      
	Use this option when you want to run the bluedriving withouth a gpsd connection. This option also deactivates the use of internet to resolve address (-i)                    

-f, --fake-gps
	Fake gps position. Useful when you don't have a gps but know your location from google maps. Example: -f '38.897388,-77.036543'

-m, --mail-user
	Gmail user to send mails from and to when a mail alarm is found. The password is entered later.

Examples
--------
./bludriving.py -w
Start the bluedriving with the web server.

./bludriving.py -w -f "35.685307,139.779765"
Start the bluedriving with the web server and a fake GPS coordinate.

./bludriving.py -s
Start with no sounds. Useful if you are in a quiet place.

./bludriving.py -l
Start but do not look up devices information. You will not have the extra info, but the process will run faster.

./bludriving.py -D -w
Start with the web server and debug mode.

TODO
----
- Add the notes to the mail.
- Change the order of web columns.
- Merge databases.
- Add more types of alarms.
- Avoid congesting the inbox
- Add the map to the mail?
- Send the mail to multiples recipients.
- Update the address of the gps coordinates manually. (right click?)
- Delete devices and locations from the database.
