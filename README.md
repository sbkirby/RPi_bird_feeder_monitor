# Bird Feeder Monitor V2.0
Bird Feeder | Grafana Display
------------ | -------------
![Main Photo 1](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Cardinal%20on%20Feeder.jpg)|![Main Photo 2](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Bird%20Feeder%20Monitor%20Grafana%20Display.png)

This is a project to monitor, photograph and record the number and time spent by birds visiting our bird feeder. Multiple Raspberry Pi's (RPi) were used for this project. One was used as a capacitive touch sensor, Adafruit CAP1188, to detect, record and trigger the photographs of the birds feeding. Another RPi was configured to control the operation of this monitoring system, as well as store and maintain the data for monitoring and analysis. The last RPi was configured as a Camera to photograph each bird visiting the feeder.

## Supplies:
* 1 ea - [Raspberry Pi W](https://www.adafruit.com/product/3400)
* 1 ea - [Raspberry Pi 3 - Model B+](https://www.adafruit.com/product/3775) - for MQTT Server
* 1 ea - Raspberry Pi with Camera - Optional
* 2 ea - Weatherproof Cases for RPi and CAP1188 Sensor
* 1 ea - [Copper Foil Tape with Conductive Adhesive](https://www.adafruit.com/product/1128)
* Wire - 18-22 AWG
* Soldering Iron and Solder
* Soldering Flux for Electronics
* Silicone Caulking*
* 8 ea - M3 x 25 Machine Screws*
* 8 ea - M3 Nuts*
* 1 ea - Proto Board for mounting CAP1188
* 1 ea - 1x8 Female Dupont Connector
* 1 ea - 1x6 Male Dupont Connector
* 1 ea - [CAP1188 - 8-Key Capacitive Touch Sensor](https://www.adafruit.com/product/1602)
* 2 ea - [PG7 Waterproof IP68 Nylon Cable Gland Joint Adjustable Locknut for 3mm-6.5mm Dia Cable Wire](https://www.amazon.com/gp/product/B01MXZ1M4I)
* 1 set - [2 Pin Way Car Waterproof Electrical Connector Plug with Wire AWG Marine Pack of 10](https://www.amazon.com/gp/product/B01F54PFLE)
* 3 ea - 5VDC Power Supply - one for each RPi
* 1 ea - Bird Feeder (CedarWorks Plastic Hopper Bird Feeder), or any Bird Feeder with plastic or wooden perches

*for 3D Printed Weatherproof Cases

## Overview of Bird Feeder Monitoring System
![MQTT Diagram](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/mqtt%20diagram.png)

This is a monitoring system designed to count, time, record and photograph the birds feeding at our bird feeder. The previous version of my [Bird Feeder Monitor](https://www.instructables.com/id/Bird-Feeder-Monitor/) used an Arduino Yun, and stored the data in a spreadsheet on my Google Disk. This version uses multiple Raspberry Pi's, MQTT communications and local storage of data and photographs.

The Bird Feeder is equipped with a Raspberry Pi Zero W and Capacitive Touch Sensor (CAP1188). Any birds lighting on the perches activate the touch sensor which starts a timer to determine the length of time each events last. As soon as the touch is activated, the "monitor/feeder/picture" MQTT message is published by the Bird Feeder Monitor. This message notifies the Raspberry Pi Camera to take a photo. If the MQTT Server publishes a "monitor/feeder/getcount" message, the Bird Feeder Monitor will respond with a "monitor/feeder/count" MQTT message which the server will store.

The MQTT Server performs several tasks. It requests and stores data from the Bird Feeder Monitor, and it controls the operation of the monitor. It activates the monitor at Dawn and shuts it down at Dusk. It also controls the timing interval for requesting data, and it also monitors the current weather conditions via [DarkSky](https://darksky.net/dev). The weather conditions are monitored for a couple of reasons. First of all, the amount of precipitation might affect the sensors. If this occurs, the sensors are recalibrated on a routine basis while rain is falling. The second reason, is to monitor and record weather conditions for correlation with the bird count data.

The Raspberry Pi camera is a RPi + Raspberry Pi Camera module. The camera software used for this project does not work with a USB Webcam. The RPi Camera is equipped with WIFI and is operating MQTT Client software. It subscribes to "monitor/feeder/picture" MQTT messages, and takes a photo each time this message is received. The photos are stored on RPi Camera, and managed remotely.

## Installing Raspbian on Bird Feeder Monitor
![RPi Zero W Stuff](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/RPi%20Zero%20W%20Stuff.jpg)

Install the latest version of Raspbian Lite on the Raspberry Pi Zero W. I recommend following the step-by-step instructions that can be found at Adafruit's [Raspberry Pi Zero Headless Quick Start](https://learn.adafruit.com/raspberry-pi-zero-creation?view=all).

The following steps were included in the instructions above, but deserve reiterating:

Connect to the RPi via ssh and run the following commands:
```
sudo apt-get update
sudo apt-get upgrade
```
The above commands will take a while to complete, but running these commands will insure you are up-to-date with the latest packages.

Next, run the following command to configure the RPi Software:
```
sudo raspi-config
```
Change your password, enable SPI and I2C, and Expand the Filesystem. Once these are complete, then exit **raspi-config**.

## Wiring of RPi and CAP1188
![RPi and CAP1188 Wiring](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/RPi%20and%20CAP1188%20Wiring.png)

The Raspberry Pi W (RPi) and the CAP1188 are wired using I2C. There are other capacitive touch sensors available with either one, five or eight sensors. I chose eight because my bird feeder has six sides.

### Wiring:
* CAP1188 SDA == RPi Pin 3
* CAP1188 SCK == RPi Pin 5
* CAP1188 VIN == RPi Pin 1 (+3.3VDC)
* CAP1188 GND == RPi Pin 9 (GND)
* CAP1188 C1-C8 == Connect to wires on each perch via 1x8 Female Dupont Connector
* RPi Pin 2 == +5VDC
* RPi Pin 14 == GND

Power for the RPi was provided externally, by running a wire underground from my garage, and up through the pipe used as the bird feeder stand. A 2-Pin Weatherproof Connector was attached to the end of the wire for connecting the RPi Bird Feeder Monitor. The other end of the wire was connected to a fused 5-VDC power supply in the garage. This project should work with batteries, but I didn't want the hassle of changing batteries on a routine basis.

I constructed a 16" long cable to connect the Weatherproof Box containing the RPi to the Weatherproof Box containing the CAP1188. The capacitive sensor needs to be located as close to the perches as possible.

The RPi Zero and CAP1188 could have been packaged in one weatherproof box, but I preferred to package them separately.

## Configuring the Bird Feeder Monitor
![I2C Tool](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/i2cdetect.png)
![crontab](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/crontab_Bird_Feeder_Monitor.png)

Log into the Raspberry Pi Zero W and perform the following steps.

Install pip:
```
sudo apt-get install python3-pip
```
Install Adafruit CircuitPython:
```
sudo pip3 install --upgrade setuptools
```
Check for I2C and SPI devices:
```
ls /dev/i2c* /dev/spi*
```
You should see the following response:
```
/dev/i2c-1 /dev/spidev0.0 /dev/spidev0.1
```
Next install a GPIO and Adafruit blinka package:
```
pip3 install RPI.GPIO
pip3 install adafruit-blinka
```
Install Adafruit's CAP1188 module:
```
pip3 install adafruit-circuitpython-cap1188
```
Install I2C tools:
```
sudo apt-get install python-smbus
sudo apt-get install i2c-tools
```
Check I2C addresses with above tool:
```
i2cdetect -y 1
```
If the CAP1188 is connected, you will see the same response as seen in the photo above, which indicates the sensor is at I2C address 0x29.

Install mosquitto, mosquitto-clients and paho-mqtt:
```
sudo apt-get install mosquitto mosquitto-clients python-mosquitto
sudo pip3 install paho-mqtt
```
I recommend using Adafruit's [Configuring MQTT on the Raspberry Pi](https://learn.adafruit.com/diy-esp8266-home-security-with-lua-and-mqtt/configuring-mqtt-on-the-raspberry-pi) to configure and setup MQTT on this RPi.

Install the Bird Feeder Monitor software:
```
cd ~
sudo apt-get install git
git clone "https://github.com/sbkirby/RPi_bird_feeder_monitor.git"
```
Create logs directory:
```
cd ~
mkdir logs
```
Wire the CAP1188 sensor to the RPi and perform the following to test the system after the MQTT server is operational:
```
cd RPi_bird_feeder_monitor
sudo nano config.json
```
Replace the values for "OIP_HOST", "MQTT_USER", "MQTT_PW" and "MQTT_PORT" to match your local setup. Exit and save your changes.

### Run at Startup
While still in the **/home/pi/RPi_bird_feeder_monitor** directory.
```
nano launcher.sh
```
Include the following text in launcher.sh
```
#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home
cd /
cd home/pi/RPi_bird_feeder_monitor
sudo python3 feeder_mqtt_client.py
cd /
```
Exit and save the launcher.sh

We need to make the script an executable.
```
chmod 755 launcher.sh
```
Test the script.
```
sh launcher.sh
```
Next, we need to edit crontab (the linux task manager) to launch the script at startup. Note: we have already created the /logs directory previously.
```
sudo crontab -e
```
This will bring the crontab window as seen above. Navigate to the end of the file and enter the following line.
```
@reboot sh /home/pi/RPi_bird_feeder_monitor/launcher.sh >/home/pi/logs/cronlog 2>&1
```
Exit and save the file, and reboot the RPi. The script should start the feeder_mqtt_client.py script after the RPi reboots. The status of the script can be checked in the log files located in the **/logs** folder.

## 3D Printed Parts
![weatherproof box bottom](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Weatherproof%20Box%20Bottom.png)
![weatherproof box top](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Weatherproof%20Box%20Top.png)
![wedge for bird feeder](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Bird%20Feeder%20Wedge.png)

These STL files are for the 3D Printed parts I created for this project, and all of these parts are optional. Weatherproof cases can be fabricated or purchased locally.
The "Mounting Wedge" for the CedarWorks Bird Feeder is also optional. This part was necessary to mount the the CAP1188 sensor case.

## Bird Feeder Monitor Assembly
![weatherproof box assembly](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Weatherproof%20Box%20Assembly.jpg)

After installing Raspbian, configuring and testing the RPi and CAP1188 Sensor as mentioned previously, now it's time to mount these devices in their weatherproof cases.

I used the two weatherproof cases I printed to mount the RPi and CAP1188 Sensor. First of all, I drilled a 1/2" hole on one end of each case. Drill the hole on the RPi case opposite the side with the SD Card. Mount the Nylon Cable Gland Joint with Adjustable Locknut in each hole. Run the four conductor cable between each case. Install and solder the 2 Pin Car Waterproof Electrical Female Connector to the RPi as shown in the photo above. Solder the red wire to the +5VDC Pin 2 of the RPi, and the black wire to GND or Pin 14. See the wiring diagram for the other connections used on the RPi.

Run the other end of the four conductor wire through the Gland Joint on the CAP1188 case, and attach the wires as indicated in the wiring diagram. All 8 of the CAP1188 capacitive touch sensors are soldered to the 8 Pin female Dupont connector. This connector is recessed in the side of the case to allow for water tight seal when the top is applied. Note: the Top on both cases will probably require modifications to allow for the nuts on the Gland Joint Connectors.

Before closing, I apply silicone caulking to edges of each case, and around the wires of the Gland Joints to seal the cases. I also add silicone to the back of the Dupont connector to seal it from the elements.

## Wiring the Bird Feeder
![wiring bird feeder 1](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Feeder%20Wiring%201.jpg)
![wiring bird feeder 2](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Feeder%20Wiring%202.jpg)
![feeder and rpi box](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Feeder%20and%20RPi%20Box.jpg)

Each of the perches on the feeder was covered with 1/4" wide self adhesive copper foil tape. A small hole was drilled through the tape and perch, and a wire was soldered to the foil tape and routed beneath the feeder. Each of the wires are connected to a male 6-pin Dupont connector.

Note: With the bird feeder shown above, I recommend a gap between the ends of each foil stripe of 1 1/4" - 1 1/2". I discovered that the larger birds, such as grackles and doves, are capable of touching two foil strips at the same time if they are placed to close together.

The "Mounting Wedge" mentioned previously was printed and glued to the bottom of the feeder to provide a level area to mount the Weatherproof Box containing the CAP1188. Velcro tape was applied to the Box as well as the wooden block to provide a means of attaching. This can seen in the photo above of the completed assembly. A velcro strap is used to wrap around the pipe and RPi box to secure them beneath the feeder.

The bird feeder is refilled with the sensor and RPi attached to the feeder, and while it is still on the pipe stand. Luckily, I'm 6'2" tall and reach the container without much effort.

## MQTT Server
![mqtt server](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Bird%20Feeder%20Node%20Red%20Flow.png)
![user interface](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Bird%20Feeder%20Monitor%20Node%20Red%20User%20Interface.png)

If your already dabbling in the IOT world, you may already have a MQTT Server up and running on your network. If you don't, I recommend using a Raspberry Pi 3 for the MQTT Server, and the instructions and IMG image file found at Andreas Spiess's website "[Node-Red, InfuxDB & Grafana Installation](http://www.sensorsiot.org/node-red-infuxdb-grafana-installation/)". Andreas also has an informative video on this subject [#255 Node-Red, InfluxDB, and Grafana Tutorial on Raspberry Pi](https://www.youtube.com/watch?v=JdV4x925au0).

Once the Node-Red Server is operational, you can import the Bird Feeder Monitor flow by copying the data in **~/RPi_bird_feeder_monitor/json/Bird_Feeder_Monitor_Flow.json**, and using **Import > Clipboard** to paste the clipboard into a new flow.

This Flow will require the following nodes:

* node-red-node-darksky - A [DarkSky API](https://darksky.net/dev) account is required to use this node.
* node-red-contrib-bigtimer - [Big Timer](https://tech.scargill.net/big-timer/) by Scargill Tech
* node-red-contrib-influxdb - [InfluxDB](https://www.influxdata.com/) Database

Weather data for your location is provided via DarkSky. And I currently monitor and record "precipIntensity", "temperature", "humidity", "windSpeed", "windBearing", "windGust" and "cloudCover". The "precipIntensity" is important because it is used to determine if the sensors need to be recalibrated as a result of the rain.

The Big Timer node is the swiss army knife of timers. It's used to Start and Stop the recording of data at Dawn and Dusk each day.

InfluxDB is a light weight easy to use time series database. The database automatically adds a timestamp each time we insert data. Unlike SQLite, the fields do not need to be defined. They are added automatically when data is inserted into the database.

### Node-Red Configuration
The JSON file mentioned above will load a Flow which requires a few tweaks to fit your requirements.

** Connect the "MQTT Publish" and "monitor/feeder/#" to your MQTT Server.
** Set the Latitude and Longitude to your location in the "Dawn & Dusk Timer (config)" Big Timer node.
** Set the "Counter Timer (config)" node to the desired time interval. Default = 5 min
** Set the Latitude and Longitude to your location in the "DarkSky (config)" node. Secondly, enter your DarkSky API Key in the darksky-credentials node.
** Set the precipitation intensity in the "monitor/feeder/recalibrate (config)" Function node. Default = 0.001 in/hr
** Edit the "Topic Filter for MQTT Receiver Debug Node (config)" Function node to filter the MQTT messages out you DON'T want to see.
** Optional: If you wish to store data in a Spreadsheet on your Google Drive, you will need to edit "Build Google Docs Payload (config)" Function node with Form Field ID's.
** Optional: Add your unique Form URL to the URL field of the "Google Docs GET (config)" HTTP Request node.

### Node-Red UI Desktop
The Bird_Feeder_Monitor_Flow includes a User Interface (UI) for accessing the MQTT Server via a cell phone. The monitor can be turned OFF or ON, Recalibrate Sensors or Take Photos manually. A total of the sensor "touches" is also shown, which will give you a rough idea of the number of birds visiting the feeder.

## Grafana
![grafana display](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Bird%20Feeder%20Monitor%20Grafana%20Display.png)
![grafana influxdb](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Grafana%20Influx%20Database.jpg)

"Grafana is an open source metric analytics & visualization suite. It is most commonly used for visualizing time series data for infrastructure and application analytics but many use it in other domains including industrial sensors, home automation, weather, and process control." refn: [Grafana Docs](https://grafana.com/docs/v4.3/).

This software is include on Andreas Spiess's image file used to create my MQTT Server. After configuring the InfluxDB database on the MQTT Server, Grafana can be configured to use this database as seen in the image above. Next, the dashboard used by this project can be loaded from the JSON file found in the **~/RPi_bird_feeder_monitor/json/Bird_Feeder_Monitor_Grafana.json**. Tips for configuring Grafana can be found at Andreas Spiess's website "[Node-Red, InfuxDB & Grafana Installation](http://www.sensorsiot.org/node-red-infuxdb-grafana-installation/)".

## InfluxDB
![influx node 1](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Bird%20Feeder%20Database%20Node%201.jpg)
![influx node 2](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Bird%20Feeder%20Database%20Node%202.jpg)

As mentioned before Adreas Spiess has a great guide and video to walk you thru the configuration of InfluxDB. Here's the steps I took to configure my database.

First of all, I logged into my MQTT Server via SSH and created a USER:
```
root@MQTTPi:~#
root@MQTTPi:~# influx
Connected to "http://localhost:8086" version 1.7.6
InfluxDB shell version: 1.7.6
Enter an InfluxQL query
> CREATE USER "pi" WITH PASSWORD 'raspberry' WITH ALL PRIVILEGES
> SHOW USERS
user	admin
----	-----
pi	true
```
Next, I created a database:
```
CREATE DATABASE BIRD_FEEDER_MONITOR
>
> SHOW DATABASES
name: databases
name
----
_internal
BIRD_FEEDER_MONITOR
>
```
AFTER you have created the database above, you can configure the InfluxDB node in Node-Red. As seen in photo above, I name the **Measurement** "feeders". This can be seen in InfluxDB after data has initialized:
```
> USE BIRD_FEEDER_MONITORUsing database BIRD_FEEDER_MONITOR
>
> SHOW MEASUREMENTS
name: measurements
name
----
feeders
>
```
One of the many features of InfluxDB is the FIELDS configuration isn't required. The FIELDS are added and configured automatically when data is entered. Here are the FIELDS and FIELDTYPE for this database:
```
> SHOW FIELD KEYS<br>name: feeders
fieldKey   fieldType
--------   ---------
cloudcover float
count_1    float
count_2    float
count_3    float
count_4    float
count_5    float
count_6    float
humidity   float
name       string
precip_Int float
temp       float
time_1     float
time_2     float
time_3     float
time_4     float
time_5     float
time_6     float
winddir    float
windgust   float
windspeed  float
>
```
A few entries from the database can be seen below:
```
>
> SELECT * FROM feeders LIMIT 10
name: feeders
time                cloudcover count_1 count_2 count_3 count_4 count_5 count_6 humidity name    precip_Int temp time_1 time_2 time_3 time_4 time_5 time_6 winddir windgust windspeed
----                ---------- ------- ------- ------- ------- ------- ------- -------- ----    ---------- ---- ------ ------ ------ ------ ------ ------ ------- -------- ---------
1550270591000000000            0       0       0       0       0       0                Feeder1                 0      0      0      0      0      0       
1550271814000000000            0       0       0       0       0       0                Feeder1                 0      0      0      0      0      0       
1550272230000000000            0       0       0       0       0       0                Feeder1                 0      0      0      0      0      0       
1550272530000000000            0       0       0       0       0       0                Feeder1                 0      0      0      0      0      0       
1550272830000000000            0       0       0       0       0       0                Feeder1                 0      0      0      0      0      0       
1550273130000000000            0       0       0       0       0       0                Feeder1                 0      0      0      0      0      0       
1550273430000000000            0       0       0       0       0       0                Feeder1                 0      0      0      0      0      0       
1550273730000000000            0       0       0       0       0       0                Feeder1                 0      0      0      0      0      0       
1550274030000000000            0       0       0       0       0       0                Feeder1                 0      0      0      0      0      0       
1550274330000000000            0       0       0       0       0       0                Feeder1                 
```

## Raspberry Pi Camera
![camera 1](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/RPi%20Cam%20Control%20-%20RPi%20Camera.png)
![camera 12](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/RPi%20Camera%20Inside%20View.jpg)
![crontab](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/crontab_RPi_Camera.png)

I recommend using my Instructable, Remote CNC Stop and Monitor, to assemble a Raspberry Pi Camera. Perform all of the Steps mentioned except 6 & 8 to create the camera. Please notice I am using an older Raspberry Pi for my Camera, but it has worked very well from my Shop window.

Upgrade Rasbian:
```
sudo apt-get update
sudo apt-get upgrade
```
Install PIP:
```
sudo apt-get install python3-pip
```
Install paho-mqtt:
```
sudo pip3 install paho-mqtt
```
Install git and Bird Monitoring Software:
```
cd ~
sudo apt-get install git
git clone "https://github.com/sbkirby/RPi_bird_feeder_monitor.git"
```
If you wish to make videos from the images taken by the camera, install ffmpeg:
```
git clone "https://git.ffmpeg.org/ffmpeg.git" ffmpeg
cd ffmpeg
./configure
make
sudo make install
```
Configuring the permissions on the Bird Feeder Monitoring software:
```
cd RPi_bird_feeder_monitor
sudo chmod 764 make_movie.sh
sudo chmod 764 take_photo.sh
sudo chown www-data:www-data make_movie.sh
sudo chown www-data:www-data take_photo.sh
```
Personally, I don't recommend using the make_movie.sh on the RPi Camera. It requires to many resources to run on the RPi. I recommend transferring the images to your PC and run ffmpeg there.

### Run at Startup
Log into the RPi and change to the **/RPi_bird_feeder_monitor** directory.
```
cd RPi_bird_feeder_monitor
nano launcher.sh
```
Include the following text in launcher.sh
```
#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home
cd /
cd home/pi/RPi_bird_feeder_monitor
sudo python3 camera_mqtt_client.py
cd /
```
Exit and save the launcher.sh

We need to make the script and executable.
```
chmod 755 launcher.sh
```
Test the script.
```
sh launcher.sh
```
Create a log directory:
```
cd ~
mkdir logs
```
Next, we need to edit crontab (the linux task manager) to launch the script at startup.
```
sudo crontab -e
```
This will bring the crontab window as seen above. Navigate to the end of the file and enter the following line.
```
@reboot sh /home/pi/RPi_bird_feeder_monitor/launcher.sh >/home/pi/logs/cronlog 2>&1
```
Exit and save the file, and reboot the RPi. The script should start the camera_mqtt_client.py script after the RPi reboots. The status of the script can be checked in the log files located in the **/logs** folder.

## Enjoy
![dove and cardinal](https://github.com/sbkirby/RPi_bird_feeder_monitor/blob/master/images/Dove%20and%20Cardinal%20on%20Feeder.jpg)

We enjoy watching birds, however we cannot place the feeder in a location for maximum enjoyment. The only place most of us can see it is from the breakfast table, and not everyone can see the feeder from there. Therefore, with the Bird Feeder Monitor we can admire the birds at our convenience.

One thing we discovered with the monitor is the frequency of birds landing on one perch, followed by a jump to the next perch until they've made it around the entire feeder. As a result, the bird counts are WAY OFF from the number of individual birds visiting our feeder. A feeder with only one or two narrow perches would probably be best for "counting" birds.
