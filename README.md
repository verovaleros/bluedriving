README
------

./bluedriving.py Version 0.1 @COPYLEFT                    
Authors: verovaleros, eldraco, nanojaus                               
Bluedriver is a bluetooth wardriving utility.                        


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
                    