#!/usr/bin/python3

#TodayPlot.py

import pandas as pd
import numpy as np
import subprocess
import datetime
import time
import os.path
import logging
import json
import matplotlib as mpl            #both of these lines must be before importing matplotlib.pyplot
mpl.use('Agg')                      #crontab won't work without this
import matplotlib.pyplot as plt
from weightfunctions import read_scale, write_file, get_weather, IFTTTmsg
from matplotlib.dates import DateFormatter      #, YEARLY, rrulewrapper, RRuleLocator, drange)
import matplotlib.dates as dates

try:
    LogFileName = "/home/pi/Documents/Code/Log/TodayPlot.log"
    logger = logging.getLogger("TodayPlot")
    logger.setLevel(logging.INFO)

    # create the logging file handler
    LogHandler = logging.FileHandler(LogFileName)
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
    LogHandler.setFormatter(formatter)

    # # add handler to logger object
    logger.addHandler(LogHandler)
    logger.info("Program started")

    TODAY = time.strftime("%Y%m%d")
    INPUTFILEPATH = "/home/pi/Documents/Code/" + str(TODAY) + "_WeightLog.csv"
    #INPUTFILEPATH = "/home/pi/Documents/Code/20180308_WeightLog.csv"
    COMMA = ","

    filedate = INPUTFILEPATH.split('_')
    #print(filedate)
    filedate = filedate[0].split('/')
    #print(filedate)
    filedate = filedate[-1]
    #print(filedate)
    filedate = filedate[0:4] + '-' + filedate[4:6] + '-' + filedate[6:8]
    print(filedate)

    print("Plot current data")
    #logger.info("Read CSV")
    with open(INPUTFILEPATH,'r') as inputfile:
        #print(inputfile)
        filecontents = pd.read_csv(inputfile, delimiter=',', parse_dates=True, dayfirst=False)      #nrows=5

    #print(filecontents.columns)
    #print(filecontents.info())
    graphfilename = "/home/pi/Documents/Code/Graphs/" + str(filedate) + "_graph.jpeg"    #try jpeg first then png
    markersize_all = 1.5
    line1color_blue = "#3c33ff"
    line2color_red = "#f40303"
    line3color_orange = "#ff9933"
    line4color_green = "#08a806"
    formatter = DateFormatter("%d-%H")
    #print(filecontents['DateTime'])
    datetime_object = pd.to_datetime(filecontents['DateTime'], format="%Y-%m-%d-%H-%M-%S")
    #print(datetime_object)
    logger.info("Plot Data")
    fig, ax1 = plt.subplots()
    ax1.plot_date(x=datetime_object, y=filecontents['WBigMed'], xdate=True, ydate=False, color=line1color_blue, marker=".", markersize=markersize_all)      #linestyle='-', linewidth=0.5 #float
    ax1.set_xlabel('Day-Hour')
    ax1.set_ylabel('Weight (lbs)', color=line1color_blue)
    ax1.tick_params('y', colors=line1color_blue)

    ax2 = ax1.twinx()
    ax2.plot_date(x=datetime_object, y=filecontents['BigTemp'], xdate=True, ydate=False, color=line2color_red, marker=".", markersize=markersize_all)      #linestyle='-', linewidth=0.5 #float
    ax2.plot_date(x=datetime_object, y=filecontents['WTemp'], xdate=True, ydate=False, color=line3color_orange, marker=".", markersize=markersize_all)      #linestyle='-', linewidth=0.5 #float
    #ax2.plot_date(x=datetime_object, y=filecontents['Solar'], xdate=True, ydate=False, color=line4color_green, marker=".", markersize=markersize_all)      #linestyle='-', linewidth=0.5 #float
    ax2.set_ylabel('Temp (F)', color=line2color_red)
    ax2.tick_params('y', colors=line2color_red)
    ax2.xaxis.set_major_formatter(formatter)
    #ax.xaxis.set_tick_params(rotation=30, labelsize=10)
    #plt.show()         #might not work with "Agg" set above during import
    #logger.info("Save Plot")
    plt.savefig(graphfilename, dpi=300)

    #print("Success!")
    #IFTTTmsg('TodayPlot Success!')

except:
    IFTTTmsg('TodayPlot Exception')
    logging.exception("TodayPlot Exception")
    raise
    #print("Exception")

finally:
    print("Done")
    logger.info("Program Done")