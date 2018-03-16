#!/usr/bin/python3

# TodayPlot.py

import pandas as pd
# import numpy as np
# import subprocess
# import datetime
import time
# import os.path
import logging
# import json
import matplotlib as mpl            # both of these lines must be before importing matplotlib.pyplot
mpl.use('Agg')                      # crontab won't work without this
import matplotlib.pyplot as plt
#import seaborn as sns
from weightfunctions import read_scale, write_file, get_weather, IFTTTmsg, calculate, check_web_response
from matplotlib.dates import DateFormatter      # , YEARLY, rrulewrapper, RRuleLocator, drange)
import matplotlib.dates as dates

try:
    LogFileName = "/home/pi/Documents/Code/Log/TodayPlot.log"
    logger = logging.getLogger("TodayPlot")
    logger.setLevel(logging.INFO)

    # create the logging file handler
    LogHandler = logging.FileHandler(LogFileName)
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
    LogHandler.setFormatter(formatter)

    # add handler to logger object
    logger.addHandler(LogHandler)
    logger.info("Program started")

    TODAY = time.strftime("%Y%m%d")
    YESTERDAY = TODAY[0:6] + str((int(TODAY[6:]) - 1)).zfill(2)
    YEAR = YESTERDAY[0:4]
    INPUTFILEPATH_TODAY = "/home/pi/Documents/Code/" + str(TODAY) + "_WeightLog.csv"
    # INPUTFILEPATH_TODAY = "/home/pi/Documents/Code/20180308_WeightLog.csv"
    COMMA = ","

    filedate = INPUTFILEPATH_TODAY.split('_')
    # print(filedate)
    filedate = filedate[0].split('/')
    # print(filedate)
    filedate = filedate[-1]
    # print(filedate)
    filedate = filedate[0:4] + '-' + filedate[4:6] + '-' + filedate[6:8]
    print(filedate)

    print("Plot current data")
    # logger.info("Read CSV")
    with open(INPUTFILEPATH_TODAY,'r') as inputfile:
        # print(inputfile)
        filecontents = pd.read_csv(inputfile, delimiter=',', parse_dates=True, dayfirst=False)      # nrows=5

    # print(filecontents.columns)
    # print(filecontents.info())
    TODAY_FILENAME = "/home/pi/Documents/Code/Graphs/" + str(filedate) + "_Today.jpeg"    # try jpeg first then png
    markersize_all = 1.5
    # colors picked from: https://htmlcolorcodes.com/color-picker/
    line1color_blue = "#3c33ff"
    line2color_red = "#f40303"
    line3color_orange = "#ff9933"
    line4color_green = "#08a806"
    formatter = DateFormatter("%d-%H")
    # print(filecontents['DateTime'])
    datetime_object = pd.to_datetime(filecontents['DateTime'], format="%Y-%m-%d-%H-%M-%S")
    # print(datetime_object)
    logger.info("Plot Data")
    fig, ax1 = plt.subplots()
    ax1.plot_date(x=datetime_object, y=filecontents['WBigMed'], xdate=True, ydate=False, color=line1color_blue, marker=".", markersize=markersize_all)      # linestyle='-', linewidth=0.5 #float
    ax1.plot_date(x=datetime_object, y=filecontents['WSmlMed'], xdate=True, ydate=False, color=line1color_blue, marker=".", markersize=markersize_all)      # linestyle='-', linewidth=0.5 #float
    ax1.set_xlabel('Day-Hour')
    ax1.set_ylabel('Weight (lbs)', color=line1color_blue)
    ax1.tick_params('y', colors=line1color_blue)

    ax2 = ax1.twinx()
    ax2.plot_date(x=datetime_object, y=filecontents['BigTemp'], xdate=True, ydate=False, color=line2color_red, marker=".", markersize=markersize_all)      # linestyle='-', linewidth=0.5 #float
    ax2.plot_date(x=datetime_object, y=filecontents['WTemp'], xdate=True, ydate=False, color=line3color_orange, marker=".", markersize=markersize_all)      # linestyle='-', linewidth=0.5 #float
    # ax2.plot_date(x=datetime_object, y=filecontents['Solar'], xdate=True, ydate=False, color=line4color_green, marker=".", markersize=markersize_all)      # linestyle='-', linewidth=0.5 #float
    ax2.set_ylabel('Temp (F)', color=line2color_red)
    ax2.tick_params('y', colors=line2color_red)
    ax2.xaxis.set_major_formatter(formatter)
    # ax.xaxis.set_tick_params(rotation=30, labelsize=10)
    # plt.show()         #might not work with "Agg" set above during import
    # logger.info("Save Plot")
    plt.savefig(TODAY_FILENAME, dpi=300)

    # Plot multi day data
    fivedaydata = pd.DataFrame()
    FIVEDAY_FILENAME = "/home/pi/Documents/Code/Graphs/" + str(filedate) + "_5Day.jpeg"
    YESTERDAYa = TODAY[0:6] + str((int(TODAY[6:]) - 1)).zfill(2)
    # print(YESTERDAYa)
    YESTERDAYb = YESTERDAYa[0:6] + str((int(YESTERDAYa[6:]) - 1)).zfill(2)
    # print(YESTERDAYb)
    YESTERDAYc = YESTERDAYb[0:6] + str((int(YESTERDAYb[6:]) - 1)).zfill(2)
    # print(YESTERDAYc)
    YESTERDAYd = YESTERDAYc[0:6] + str((int(YESTERDAYc[6:]) - 1)).zfill(2)
    # print(YESTERDAYd)
    YESTERDAYe = YESTERDAYd[0:6] + str((int(YESTERDAYd[6:]) - 1)).zfill(2)
    # print(YESTERDAYe)
    YESTERDAYS = [YESTERDAYe, YESTERDAYd, YESTERDAYc, YESTERDAYb, YESTERDAYa]

    for eachday in YESTERDAYS:
        INPUTFILEPATH_5DAY = "/home/pi/Documents/Code/" + str(eachday) + "_WeightLog.csv"
        with open(INPUTFILEPATH_5DAY,'r') as inputfile:
            # print(inputfile)
            filecontents = pd.read_csv(inputfile, delimiter=',', parse_dates=True, dayfirst=False)
            # print(filecontents)
        fivedaydata = fivedaydata.append(filecontents, ignore_index=True)
    # print(fivedaydata.info())
    datetime_object = pd.to_datetime(fivedaydata['DateTime'], format="%Y-%m-%d-%H-%M-%S")
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Day-Hour')
    ax1.set_ylabel('Weight (lbs)', color=line1color_blue)
    ax1.xaxis.set_major_formatter(formatter)
    ax1.plot_date(x=datetime_object, y=fivedaydata['WBigMed'], xdate=True, ydate=False, color=line1color_blue, marker=".", markersize=markersize_all)
    ax1.plot_date(x=datetime_object, y=fivedaydata['WSmlMed'], xdate=True, ydate=False, color=line2color_red, marker=".", markersize=markersize_all)
    # plt.show()
    plt.savefig(FIVEDAY_FILENAME, dpi=300)

    # Plot DailyStats
    INPUTFILEPATH_DAILYSTATS = "/home/pi/Documents/Code/" + YEAR + "_DailyStats.csv"
    DAILYSTATS_FILENAME = "/home/pi/Documents/Code/Graphs/" + YEAR + "_DailyStats.jpeg"

    with open(INPUTFILEPATH_DAILYSTATS, "r") as inputfile:
        # print(inputfile)
        filecontents = pd.read_csv(inputfile, delimiter=',', parse_dates=True, dayfirst=False)
        # print(filecontents)
    # print(fivedaydata.info())
    dailystatsdata = filecontents.tail()
    datetime_object = pd.to_datetime(dailystatsdata['DateTime'], format="%Y-%m-%d")
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Day')
    ax1.set_ylabel('Median Weight Big (lbs)', color=line1color_blue)
    formatter = DateFormatter("%d")
    ax1.xaxis.set_major_formatter(formatter)
    ax1.plot_date(x=datetime_object, y=dailystatsdata['WBigMed-Median'], xdate=True, ydate=False, color=line1color_blue, marker="o", markersize=markersize_all)
    ax1.plot_date(x=datetime_object, y=dailystatsdata['WBigMed-Q1'], xdate=True, ydate=False, color=line1color_blue, marker="v", markersize=markersize_all)
    ax1.plot_date(x=datetime_object, y=dailystatsdata['WBigMed-Q4'], xdate=True, ydate=False, color=line1color_blue, marker="^", markersize=markersize_all)
    ax1.plot_date(x=datetime_object, y=dailystatsdata['WBigMed-Min'], xdate=True, ydate=False, color=line1color_blue, marker="_", markersize=markersize_all)
    # ax1.plot_date(x=datetime_object, y=dailystatsdata['WBigMed-Max'], xdate=True, ydate=False, color=line1color_blue, marker="_", markersize=markersize_all)
    ax2 = ax1.twinx()
    ax2.plot_date(x=datetime_object, y=dailystatsdata['WSmlMed-Median'], xdate=True, ydate=False, color=line2color_red, marker="o", markersize=markersize_all)
    ax2.plot_date(x=datetime_object, y=dailystatsdata['WSmlMed-Q1'], xdate=True, ydate=False, color=line2color_red, marker="v", markersize=markersize_all)
    ax2.plot_date(x=datetime_object, y=dailystatsdata['WSmlMed-Q4'], xdate=True, ydate=False, color=line2color_red, marker="^", markersize=markersize_all)
    ax2.plot_date(x=datetime_object, y=dailystatsdata['WSmlMed-Min'], xdate=True, ydate=False, color=line2color_red, marker="_", markersize=markersize_all)
    # ax2.plot_date(x=datetime_object, y=dailystatsdata['WSmlMed-Max'], xdate=True, ydate=False, color=line2color_red, marker="_", markersize=markersize_all)
    ax2.set_ylabel('Median Weight Small (lbs)', color=line2color_red)
    ax2.tick_params('y', colors=line2color_red)
    plt.savefig(DAILYSTATS_FILENAME, dpi=300)
    # plt.show()

    # print("Success!")
    # IFTTTmsg('TodayPlot Success!')

except:
    IFTTTmsg('TodayPlot Exception')
    logging.exception("TodayPlot Exception")
    raise
    # print("Exception")

finally:
    print("Done")
    logger.info("Program Done")