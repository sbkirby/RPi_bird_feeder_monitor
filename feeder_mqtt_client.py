#!/usr/bin/env python3
"""
  Bird Feeder Monitor - RPi
  The Feeder Module

Parts:
	2ea Waterproof Enclosures
	1ea roll 1/4" Copper Foil Tape
	1ea CAP1188 8-Key Capacitive Touch Sensor
	1ea Raspberry Pi Zero W
	1ea micro-SD card
	1ea Bird Feeder (CedarWorks Plastic Hopper Bird Feeder)
	1ea Automotive Waterproof Electrical Connector Plug 2 Pin
Modules:
    RPI.GPIO
    adafruit-blinka
	adafruit-circuitpython-cap1188
    paho-mqtt

Date: November 4, 2018
By: Stephen B. Kirby
 """

import sys
import time
import board
import busio
import paho.mqtt.client as mqtt
import json

# Create Adafruit library object using our Bus I2C port
from adafruit_cap1188.i2c import CAP1188_I2C
i2c = busio.I2C(board.SCL, board.SDA)
cap = CAP1188_I2C(i2c)

# Bird Feeder name
feeder_name = 'Feeder1'
# Bird Counting Variables
birdTimer  = [0,0,0,0,0,0,0,0]   # temporary timer for each perch
birdResult = [0,0,0,0,0,0,0,0]   # total time for each perch
birdCnt    = [0,0,0,0,0,0,0,0]   # number of times perch touched
birdTouch  = [0,0,0,0,0,0,0,0]   # temporary flag indicating a touch for each perch
perches    = [0,0,0,0,0,0,0,0]   # picture taking disabled on all perches by default
perchCnt   = 6                   # currently configured for six of eight perches - modify as needed
# minutes from midnight to Dawn and dusk
dawn = 0
dusk = 0
localOffset = 0
# current number of minutes from midnight
right_now = 0
# Is it OK to run
current_status = True
# Flag to transmit
transmit = True
# milliseconds timer
current_milli_time = lambda: int(round(time.time() * 1000))
# set DEBUG=1 to print debug statements
DEBUG = 0
# init client object
client = None

# read data from config file. json only
def load_config():
    with open('config.json') as json_data_file:
    	return json.load(json_data_file)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc, *extra_params):
    global DEBUG
    if DEBUG:
        print('Connected with result code ' + str(rc))
    client.subscribe('monitor/feeder/#')

# Publish data to server
def publish_count():
    global client, DEBUG
    if DEBUG:
        print("publish_count=",get_feeder_status())
    if transmit:
        client.publish('monitor/feeder/count', get_feeder_status(), 1)

# Decode JSON data in payload
def decode_msg(msg):
    m_decode = str(msg.payload.decode("utf-8","ignore"))
    return json.loads(m_decode)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global dawn, dusk, right_now, current_status, DEBUG
    if msg.topic == 'monitor/feeder/getcount':
        if current_status:
            publish_count() # publish bird count data
            reset()         # resets variables
    if msg.topic == 'monitor/feeder/astronomy':
        # example: {"localOffset":360,"perch_0":1,"perch_1":1,"perch_2":1,"perch_3":1,"perch_4":1,"perch_5":1,"perch_6":0,"perch_7":0,"state":"ON Auto","dawn":767,"dusk":26,"now":1036}
        msg_data = decode_msg(msg)
        if 'ON' in msg_data['state']:
            current_status = True
        if 'OFF' in msg_data['state']:
            current_status = False
            reset()
        localOffset = msg_data['localOffset']
        dawn = msg_data['dawn'] - localOffset
        dusk = (1440 + msg_data['dusk']) - localOffset
        right_now = msg_data['now'] - localOffset
        # Enable/Disable picture taking for individual perches
        for i in range(0,8):
            perches[i] = msg_data["perch_"+str(i)]
        if DEBUG:
            print('astronomy: Dawn='+str(dawn)+' Dusk='+str(dusk)+' Now='+str(right_now)+' Status='+str(current_status))
    if msg.topic == 'monitor/feeder/recalibrate':
        recalibrate_feeder_sensor()

# Logging
def on_log(client, userdata, level, buf):
    global DEBUG
    if DEBUG:
        print("log: ",buf)

# Assemble sensor data
def get_feeder_status():
    # currently configured for six of eight perches
    sensor_data = {'name':feeder_name, 'cnt1':birdCnt[0], 'time1':int(birdResult[0]/1000), 'cnt2':birdCnt[1], 'time2':int(birdResult[1]/1000), 'cnt3':birdCnt[2], 'time3':int(birdResult[2]/1000), 'cnt4':birdCnt[3], 'time4':int(birdResult[3]/1000), 'cnt5':birdCnt[4], 'time5':int(birdResult[4]/1000), 'cnt6':birdCnt[5], 'time6':int(birdResult[5]/1000)}
    return json.dumps(sensor_data)

# Recalibrate the touch sensors
def recalibrate_feeder_sensor():
    cap.recalibrate()

# Reset bird counting arrays
def reset():
    global birdTouch, birdCnt, birdResult, birdTimer
    birdTouch  = [0,0,0,0,0,0,0,0]
    birdCnt    = [0,0,0,0,0,0,0,0]
    birdResult = [0,0,0,0,0,0,0,0]
    for j in range(0,perchCnt):
        birdTimer[j] = current_milli_time()

# save the data, cleanup GPIO and exit
def clean_and_exit():
    time.sleep(0.1)
    sys.exit() #exit python to system

def main():
    global cap, client, birdTouch, birdCnt, birdResult, birdTimer
    # wait 15 seconds for CAP1188 and network to start
    if DEBUG:
        print("Standby 15 seconds for things to start.")
    time.sleep(15)
    # reset variables
    reset()
    # load config.json file
    data = load_config()
    # mqtt connect
    client = mqtt.Client(feeder_name)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_log = on_log
    client.username_pw_set(data['MQTT_USER'], password=data['MQTT_PW'])
    client.connect(data['OIP_HOST'], data['MQTT_PORT'], 60)
    time.sleep(0.5)
    client.loop_start()

    while True:
        # Loop shouldn't start until a 'monitor/feeder/astronomy' message
        # is received to initialize dawn, dusk and right_now variables
        if current_status & (right_now > dawn) & (right_now < dusk):
            # check the CAP1188
            touched = cap.touched()

            # if NOT TOUCHED
            if (touched == 0):
                for j in range(0,perchCnt):
                    # if TOUCHED previously add time to birdResult
                    if birdTouch[j]:
                        birdResult[j] = birdResult[j] + (current_milli_time() - birdTimer[j])
                        birdTimer[j] = current_milli_time()
                    birdTouch[j] = 0
            else:
                if DEBUG:
                    print("Touched!")

            # if TOUCHED check status of each capacitor
            for i in range(0,perchCnt):
                if (touched & (1 << i)):
                    # if NOT touched previously - TAKE A PICTURE
                    if not birdTouch[i]:
                        birdTouch[i] = 1
                        birdCnt[i] = birdCnt[i] + 1
                        birdTimer[i] = current_milli_time()
                        if (transmit & perches[i]):
                            mypayload = {'message':'smile-'+str(i),'perch':i}
                            client.publish('monitor/feeder/picture', json.dumps(mypayload) , 1)
                    # if TOUCHED previously
                    else:
                        birdResult[i] = birdResult[i] + (current_milli_time() - birdTimer[i])
                        birdTimer[i] = current_milli_time()
            time.sleep(0.1)
        else:
            if DEBUG:
                print('False: current_status & (right_now > dawn) & (right_now < dusk) ')
            time.sleep(5)

    client.loop_stop()
    client.disconnect()
    clean_and_exit()

if __name__ == "__main__":
    main()
