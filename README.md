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
The web server was separated to help visualize the data without capturing more devices. If you want to analyze a previous database, or analyze the data off line, you can start the web server alone.

Using multiples bluetooth dongles
----------------------------------
Unfortunately, the bluetooth libraries does not allow us to select the bluetooth device you want to use. So, if you use an external bluetooth device, we recommend you to switch off all the wireless capabilities of you computer (using the hardware or software switch), to plug the new external bluetooth device and then to reenable the wireless capabilities. In this way your external bluetooth device will be the hci0 device. (You can check with hciconfig)

Alarms and notes
----------------
Alarms and notes are stored in the database. Every time a device is seen, the alarms for that device are checked. If a sound alarm is found, a nice sound is played. If a festival alarm is found, the device name is read with festival. If a mail alarm is found, a mail with the device information is sent to the specified mail address (-m option) from the same mail address. This is done by using your gmail account. In this way, gmail allow you to send mail without problems. Note that the bluedriving tool does no communicate or store the mail or password. This data is for the session only and totally private.
Alarms are meant to tell you when a certain device was seen again. For example, you can set an alarm on your friend device to know if he enters the same bar as you later!
Notes are meant to add your own information to any device. Perhaps you know the exact name of the person using that device.

Improve speed
-------------
To improve the speed while detecting new devices, we recommend to switch on the "Not Internet" parameter (press the i letter while running or -i) and to switch on the "Not look up services" (press the l letter while running or -l)

Dependencies
------------
python-bluez
python-lightblue
python-pygame
python-gps
python-simplejson

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


Connecting to a cell phone GPS
-----------------------------
- Activate the bluetooth on your phone
- Check that you can use the bluetooth device on the pi without problems.
    hcitool scan
- You need to pair both devices. Once they were paired there is no need to repeat this every time.
    - Make your pi visible
        bluez-test-adapter discoverable on
    - Put a default pin on the pi
        bluetooth-agent 0000 &
    - From you phone, pair with the pi
- YOU SHOULD COMPLETE THE PREVIOUS STEPS BEFORE CONTINUING! Turn off and on the bluetooth on both sides until you get it working.
- Make your phone discoverable
- Find its MAC from the pi
    hcitool scan
- Start the bluenmea app on your phone
- Find the serial channel number where the bluenmea app is servicing the serial communication
    sdptool browse <MAC of your phone>
    The channel number is on a service called "BlueNMEA" or similar. In the "Protocol Description List" should say "RFCOMM". Like this
        Service Name: BlueNMEA
        Service RecHandle: 0x1000a
        Service Class ID List:
          UUID 128: 00001101-0000-1000-8000-00805f9b34fb
        Protocol Descriptor List:
          "L2CAP" (0x0100)
          "RFCOMM" (0x0003)
            Channel: 1

    In this case the channel is 20
- Create a configuration for the future permanent connection from your pi to your cell phone in the file /etc/bluetooth/rfcomm.conf
    rfcomm0 {
    bind yes;
    device <MAC of your phone>;
    channel <channel>;
    comment "Serial Port";
    }

- Bind the serial link from  your pi to your phone
    rfcomm bind 0 <MAC of your phone> <channel>
- Verify that the rfcomm connection is working
    rfcomm
    
    You should see something like this:
    rfcomm0: 10:a2:B3:c2:92:13 channel 1 clean
- Be sure your bluenmea app is working and active.

- Start the gpsd like this
    gpsd -n /dev/rfcomm0

- Access solicitude
    Your phone may recive an access solicitation from you pi to access some files (YES FILES!). Say yes.
- Test if you have gps data with 
    cgps
    or xgps
- Make this work permanently after reboot
    Put in the file /etc/rc.local these lines

        rfcomm bind 0 <phone MAC> <channel>

        # gpsd
        /usr/sbin/gpsd -n /dev/rfcomm0

        cd /home/pi/ro/aplics/bluedriving/bluedriving/
        ./bluedriving.py -i -l

- That's it!

Script to automatically connect your pi to your phone
-----------------------------------------------------
- Put the following script some file like /root/blupi.sh
- Note that you should change your phone's MAC
    #!/bin/bash
    FILE="/etc/bluetooth/rfcomm.conf"
    rm $FILE
    DEVICE='<your-phone-mac>'
    CHANNEL=`sdptool browse $DEVICE|grep -iA 8 BlueNMEA|grep -i channel|awk -F": " '{print $2}'`
    echo $CHANNEL
    echo "rfcomm0 {" >> $FILE
    echo "bind yes;" >> $FILE
    echo "device $DEVICE;" >> $FILE
    echo "channel $CHANNEL;" >> $FILE
    echo "comment \"Serial Port\";" >> $FILE
    echo "}" >> $FILE
    rfcomm bind 0 $DEVICE $CHANNEL
    /usr/sbin/gpsd -n /dev/rfcomm0
    cd <path-to-your-bluedriving-installation>
    ./bluedriving.py -l -w -I 0.0.0.0

- Give proper permissions: chmod 777 /root/blupi.sh
- Put this line in /etc/rc.local to execute the script when the pi boots
    /root/blupi.sh


Giving Internet to your raspberry pi via bluetooth at the same time
-------------------------------------------------------------------
- To know with which devices you are paired with
    bluez-test-device list
- To connect to your phone and 
    sudo pand -c C8:BC:C8:E1:E5:C5 --role PANU --persist 30
    dhclient bnep0


TroubleShooting
---------------
- If the program stop finding bluetooth devices, try to scan manually with 'hcitool scan'. If it still does not find anything, try to bring the interface down with 'hciconfig hci0 down' and up again with 'hciconfig hci0 up'. That should fix the problems with the devices.

Bugs
----
- Sometimes the libraries throw and exception like this "*** glibc detected *** /usr/bin/python: double free or corruption (!prev): 0x01284fe8 ***". We have no idea why. Sorry.
- In the All devices map, if you come from the results, it sometimes delete the iframe of the input.


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
- Show the total amount of devices
- At the right of each device it can say how many times we found it.
- Filter devices by name or MAC
