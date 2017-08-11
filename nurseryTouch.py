#! /usr/bin/python

#Requires I2C to be switched on in raspi-config

#Requires python-smbus
#Requires touchphat - pip install touchphat

import touchphat
import signal
import paho.mqtt.client as paho
import time
import json

#Connect to an MQTT server
client = paho.Client()

#Wait for the connection before carrying on
time.sleep(1)

#Connect to the broker
client.connect("192.168.1.10")

#Create some variables to log states
feedingLeft=False
feedingRight=False
sleeping=False

#Start a loop for MQTT
client.loop_start()

@touchphat.on_touch(['Back','A','B','C','D','Enter'])
def handle_touch(event):
    eventTime = time.strftime("%H:%M:%S", time.localtime())
    eventDate = time.strftime("%Y-%m-%d", time.localtime())
    print(eventTime, eventDate,)

    #Test for nappy states
    if event.name=="A":
        client.publish("/house/nursery/nappy",json.dumps({"state":"dirty","time":eventTime,"date":eventDate}))
        print("Dirty Nappy")
    elif event.name=="B":
        client.publish("/house/nursery/nappy",json.dumps({"state":"wet","time":eventTime,"date":eventDate}))
        print("Wet Nappy")
    elif event.name=="C":
        client.publish("/house/nursery/nappy",json.dumps({"state":"mixed","time":eventTime,"date":eventDate}))
        print("Mixed Nappy")

    #Test for sleeping
    elif event.name=="D":
        global sleeping
        if sleeping==False:
            sleeping=True
        else:
            sleeping=False
        client.publish("/house/nursery/sleeping",json.dumps({"state":int(sleeping),"time":eventTime,"date":eventDate})) 
        print("Sleeping: ",sleeping)
    #Test for feeding
    elif event.name=="Back":
        global feedingLeft
        #This is left
        if feedingLeft == False:
            feedingLeft = True
        else:
            feedingLeft = False
        client.publish("/house/nursery/feeding/left",json.dumps({"state":str(feedingLeft),"time":eventTime,"date":eventDate}))
        print ("Left: ",feedingLeft)	
    elif event.name=="Enter":
	global feedingRight
        #This is right
        if feedingRight == False:
            feedingRight = True
        else:
            feedingRight = False
        client.publish("/house/nursery/feeding/right",json.dumps({"state":str(feedingRight),"time":eventTime,"date":eventDate}))
        print ("Right: ",feedingRight)

    #Set the LED on and off again and add a delay for debounce
    touchphat.set_led(event.name, True)
    time.sleep(0.5)
    touchphat.set_led(event.name, False)

signal.pause()
client.disconnect()
