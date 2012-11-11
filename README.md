Bluedriving
-----------

What
----
Bluedriving is a bluetooth wardriving utility. It can capture bluetooth devices, lookup their services, get GPS and present everything in a nice webpage.

Authors: verovaleros, eldraco, nanojaus                               

Mail Features
-------------
- Scan bluetooth devices.
- Lookup services.
- Use threads.
- Stores everything in a sqlite database.
- Has a stand-alone web server with an API. It can be also started within the bluedriving.py tool.
- Implement alarms for the bluetooth devices that you want: Play a sound, Read the bluetooth name with festival, send an email with the information.
- You can manually specify the GPS coordinates, so you can have the map functionality without having a GPS.
- You can interact with the program through these keys and pressing Enter:
 -- a (set or unset alarms)
 -- s (set or unset sounds)
 -- l (set or unset lookup devices)
 -- d (set or unset debugging)
- Has a beautiful web page, that lets you:
 -- See all the bluetooth devices ordered by last seen position.
 -- See each device information, including a map with the position you are inspecting.
 -- see the history of all the positions of the selected device in a large map.





Usage: ./bluedriving.py <options>
Options:                    
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
                    
