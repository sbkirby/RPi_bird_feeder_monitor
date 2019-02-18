#!/usr/bin/env python3
"""
  Bird Feeder Monitor - RPi
  The Camera Module

Parts:
    1ea Raspberry Pi
    1ea Raspberry Pi Camera
Modules:
    RPi-Cam-Web-Interface https://elinux.org/RPi-Cam-Web-Interface
    paho-mqtt

Note: This does not work with a Web Camera...only with a RPi Camera

Date: December 1, 2018
By: Stephen B. Kirby
"""

import sys
import time
import paho.mqtt.client as mqtt
import json
from subprocess import call

# set DEBUG=1 to print debug statements
DEBUG = 0
# init global variables
client = None
# Camera Name
camera_name = 'Camera1'

# read data from config file. json only
def load_config():
    with open('config.json') as json_data_file:
        return json.load(json_data_file)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global DEBUG
    if DEBUG:
        print("Connected - result code: "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("monitor/feeder/picture")
    client.subscribe("monitor/feeder/makemovie")

# Logging
def on_log(client, userdata, level, buf):
    global DEBUG
    if DEBUG:
        print("log: ",buf)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global DEBUG
    if DEBUG:
        print(msg.topic+" "+str(msg.payload))
    if msg.topic=='monitor/feeder/picture':
        call('sh ./take_photo.sh',shell=True)
        time.sleep(1)
        if DEBUG:
            print("Smile ;)")
    if msg.topic=='monitor/feeder/makemovie':
        call('sudo sh ./make_movie.sh',shell=True)
        if DEBUG:
            print("Movie Time!")

# save the data, cleanup GPIO and exit
def clean_and_exit():
    global client
    client.loop_stop()
    client.disconnect()
    time.sleep(0.1)
    sys.exit() #exit python to system

def main():
    global client, DEBUG
    # wait 15 seconds for CAP1188 and network to start
    if DEBUG:
        print("Standby 15 seconds for things to start.")
    time.sleep(15)
    # load config.json data file
    data = load_config()
    if DEBUG:
        print("OIP_HOST= "+str(data['OIP_HOST'])+"   MQTT_PORT="+str(data['MQTT_PORT']))
    client = mqtt.Client(camera_name)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_log = on_log
    client.username_pw_set(data['MQTT_USER'], password=data['MQTT_PW'])
    client.connect(data['OIP_HOST'], data['MQTT_PORT'], 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

if __name__ == "__main__":
    main()
    clean_and_exit()
