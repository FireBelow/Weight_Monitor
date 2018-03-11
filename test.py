#!/usr/bin/python3

#test.py

import pandas as pn
import numpy as np
import RPi.GPIO as GPIO
import subprocess
import datetime
import time
import Adafruit_DHT
import os.path
import logging
import json
import matplotlib.pyplot as plt
from hx711 import HX711                             # import the class HX711
from weightfunctions import read_scale, write_file, get_weather, IFTTTmsg

try:
    #includes = ['*.doc', '*.odt'] # for files only
    #excludes = ['/home/Documents'] # for dirs and files
    # searchfilepath = "/home/pi/Documents/Code/Topo/LinksbyState/"
    # for root, dirs, files in os.walk(searchfilepath):               #gives (dirpath, dirnames, filenames)
    #     print(root, dirs, files)
    #     for file in files:
    #         inputfilepath = file
            #for path in paths:
            #if fnmatch.fnmatch(path, include):
            #print(root, dirs, files)
            # if file.endswith(('doc','csv')):
            #     print file
            #     print(os.path.join(root, file))
            #     os.path.splitext(os.path.basename(searchfilepath))[0]       #or use dirs
    inputfilepath = "/home/pi/Documents/Code/20180303_WeightLog.csv"
    #outputfilepath = "/home/pi/Documents/Code/test.csv"
    COMMA = ","
    datatosave = ""
    headers = ""
    observationthreshold = 12 * 24  #obs every 5 min per hour times 24 hrs

    filedate = inputfilepath.split('_')
    #print(filedate)
    filedate = filedate[0].split('/')
    #print(filedate)
    filedate = filedate[-1]
    #print(filedate)
    filedate = filedate[0:4] + '-' + filedate[4:6] + '-' + filedate[6:8]
    print(filedate)

    print("Test")
    with open(inputfilepath,'r') as inputfile:
        #print(inputfile)
        filecontents = pn.read_csv(inputfilepath, delimiter=',', parse_dates=True, dayfirst=False)      #nrows=5

    #print(filecontents.columns)
    print(filecontents.info())
    graphfilename = "/home/pi/Documents/Code/" + str(filedate) + "_graph.jpeg"    #try jpeg first then png
    filecontents.plot(kind='scatter', x='WTemp', y='WBigMed')
    #plt.show()
    plt.savefig(graphfilename, dpi=300)

except:
    IFTTTmsg('Test Exception')
    logging.exception("Test Exception")
    raise
    #print("Exception")

finally:
    print("Done")