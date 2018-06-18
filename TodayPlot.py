#!/usr/bin/python3

# TodayPlot.py

import pandas as pd
# import numpy as np
# import subprocess
import datetime
import time
import os.path
import shutil
import logging
# import json
import matplotlib as mpl            # both of these lines must be before importing matplotlib.pyplot
mpl.use('Agg')                      # crontab won't work without this
import matplotlib.pyplot as plt
# import seaborn as sns
from weightfunctions import read_scale, write_file, get_weather, IFTTTmsg, calculate, check_web_response
from matplotlib.dates import DateFormatter      # , YEARLY, rrulewrapper, RRuleLocator, drange)
import matplotlib.dates as dates

# TODO
# Sunrise/sunset delta trigger
# Types of plots to add
# Nectar start/end
# Day of 1/2 nectar flow
# Daily weight by year (stacked by adding 100lbs)
# Water Tower buckets per day
# Make functions to read each file type correctly (Read Daily Log and set WMain to category)
# Plot each day curve on one graph to see daily differences, see also andrews_curves

try:
    # Plot scatter with filecontents.index as X values
    # use_index=True
    # # or
    # np.random.seed(1)
    # year = [1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014]
    # value = np.random.rand(23)
    # ser =  pd.Series(index = year,data=value)
    # df =ser.to_frame()
    # df.reset_index(inplace=True)
    # df.columns = ['year','value']
    # df.plot(kind='scatter',x='year',y='value')
    # plt.show()

    # ################################
    # outlier_test_HI = round(np.median(BIGdata), 2)
    # if round(np.median(BIGdata), 2) > outlier_test_HI:
    #     problem_msg = "Outlier"
    #     logger.info(problem_msg)
    #     IFTTTmsg(problem_msg)
    #     print(problem_msg)
    #     = [np.nan]


    # ############################
    # # change to problem_msg = ""
    # Notes = ""
    #         + str(round(np.std(SMLdata_raw), 1)) + COMMA       \
    #         + Notes + "\n"
    # Notes = Notes + "Big DHT Retries: " + str(i)
    # Notes = Notes + str(i) + " retries for BigHX"
    # Notes = Notes + str(i) + " retries for SmlHX"

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

    TODAY = datetime.datetime.now().date()
    # print(TODAY, type(TODAY))
    MINUS_ONE_DAY = datetime.timedelta(days=1)
    YESTERDAY = TODAY - MINUS_ONE_DAY
    # print(YESTERDAY, type(YESTERDAY))
    YEAR = TODAY.year
    # print(YEAR, type(YEAR))
    ISO_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    ISO_DATE_FORMAT = "%Y-%m-%d"
    FILE_DATE_FORMAT = "%Y%m%d"

    INPUTFILEPATH_TODAY = "/home/pi/Documents/Code/" + TODAY.strftime(FILE_DATE_FORMAT) + "_WeightLog.csv"
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
    with open(INPUTFILEPATH_TODAY, 'r') as inputfile:
        # print(inputfile)
        filecontents = pd.read_csv(inputfile, delimiter=',', parse_dates=True, dayfirst=False)      # nrows=5

    # print(filecontents.columns)
    # print(filecontents.info())
    TODAY_FILENAME = "/home/pi/Documents/Code/Graphs/" + str(filedate) + "_Today.jpg"    # try jpeg first then png
    markersize_all = 1.5
    # colors picked from: https://htmlcolorcodes.com/color-picker/
    linecolor_blue = "#3c33ff"
    linecolor_red = "#f40303"
    linecolor_orange = "#ff9933"
    linecolor_green = "#08a806"
    formatter = DateFormatter("%d-%H")
    # print(filecontents['DateTime'])
    datetime_object = pd.to_datetime(filecontents['DateTime'], format=ISO_DATETIME_FORMAT)
    # print(datetime_object)
    logger.info("Plot Data")
    fig, ax1 = plt.subplots()
    ax1.plot_date(x=datetime_object, y=filecontents['WBigMed'], xdate=True, ydate=False, color=linecolor_blue, marker=".", markersize=markersize_all)      # linestyle='-', linewidth=0.5 #float
    ax1.plot_date(x=datetime_object, y=filecontents['WSmlMed'], xdate=True, ydate=False, color=linecolor_blue, marker=".", markersize=markersize_all)      # linestyle='-', linewidth=0.5 #float
    ax1.set_xlabel('Day-Hour')
    ax1.set_ylabel('Weight (lbs)', color=linecolor_blue)
    ax1.tick_params('y', colors=linecolor_blue)

    ax2 = ax1.twinx()
    ax2.plot_date(x=datetime_object, y=filecontents['BigTemp'], xdate=True, ydate=False, color=linecolor_red, marker=".", markersize=markersize_all)      # linestyle='-', linewidth=0.5 #float
    ax2.plot_date(x=datetime_object, y=filecontents['WTemp'], xdate=True, ydate=False, color=linecolor_orange, marker=".", markersize=markersize_all)      # linestyle='-', linewidth=0.5 #float
    # ax2.plot_date(x=datetime_object, y=filecontents['Solar'], xdate=True, ydate=False, color=linecolor_green, marker=".", markersize=markersize_all)      # linestyle='-', linewidth=0.5 #float
    ax2.set_ylabel('Temp (F)', color=linecolor_red)
    ax2.tick_params('y', colors=linecolor_red)
    ax2.xaxis.set_major_formatter(formatter)
    # ax.xaxis.set_tick_params(rotation=30, labelsize=10)
    # plt.show()         #might not work with "Agg" set above during import
    # logger.info("Save Plot")
    plt.savefig(TODAY_FILENAME, dpi=300)
    if os.path.exists(TODAY_FILENAME):
        print("File exists")
        shutil.copyfile(TODAY_FILENAME, "/home/pi/Documents/Code/www/images/today.jpg")
    else:
        IFTTTmsg("No Plot")

    # Plot multi day data
    fivedaydata = pd.DataFrame()
    FIVEDAY_FILENAME = "/home/pi/Documents/Code/Graphs/" + str(filedate) + "_5Day.jpg"
    YESTERDAYa = YESTERDAY
    # print(YESTERDAYa)
    YESTERDAYb = YESTERDAYa - MINUS_ONE_DAY
    # print(YESTERDAYb)
    YESTERDAYc = YESTERDAYb - MINUS_ONE_DAY
    # print(YESTERDAYc)
    YESTERDAYd = YESTERDAYc - MINUS_ONE_DAY
    # print(YESTERDAYd)
    YESTERDAYe = YESTERDAYd - MINUS_ONE_DAY
    # print(YESTERDAYe)
    YESTERDAYS = [YESTERDAYe, YESTERDAYd, YESTERDAYc, YESTERDAYb, YESTERDAYa]
    # print(YESTERDAYS)

    for eachday in YESTERDAYS:
        # print(eachday)
        INPUTFILEPATH_5DAY = "/home/pi/Documents/Code/" + eachday.strftime(FILE_DATE_FORMAT) + "_WeightLog.csv"
        with open(INPUTFILEPATH_5DAY, 'r') as inputfile:
            # print(inputfile)
            filecontents = pd.read_csv(inputfile, delimiter=',', parse_dates=True, dayfirst=False)
            # print(filecontents)
        fivedaydata = fivedaydata.append(filecontents, ignore_index=True)
    # print(fivedaydata.info())
    datetime_object = pd.to_datetime(fivedaydata['DateTime'], format=ISO_DATETIME_FORMAT)
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Day-Hour')
    ax1.set_ylabel('Weight (lbs)', color=linecolor_blue)
    ax1.xaxis.set_major_formatter(formatter)
    ax1.plot_date(x=datetime_object, y=fivedaydata['WBigMed'], xdate=True, ydate=False, color=linecolor_blue, marker=".", markersize=markersize_all)
    ax1.plot_date(x=datetime_object, y=fivedaydata['WSmlMed'], xdate=True, ydate=False, color=linecolor_red, marker=".", markersize=markersize_all)
    # plt.show()
    plt.savefig(FIVEDAY_FILENAME, dpi=300)
    if os.path.exists(FIVEDAY_FILENAME):
        print("File exists")
        shutil.copyfile(FIVEDAY_FILENAME, "/home/pi/Documents/Code/www/images/fiveday.jpg")
    else:
        IFTTTmsg("No Plot")

    # Plot DailyStats
    INPUTFILEPATH_DAILYSTATS = "/home/pi/Documents/Code/" + str(YEAR) + "_DailyStats.csv"
    # print(INPUTFILEPATH_DAILYSTATS)
    DAILYSTATS_FILENAME = "/home/pi/Documents/Code/Graphs/" + str(YEAR) + "_DailyStats.jpg"
    # print(DAILYSTATS_FILENAME)

    with open(INPUTFILEPATH_DAILYSTATS, "r") as inputfile:
        # print(inputfile)
        filecontents = pd.read_csv(inputfile, delimiter=',', parse_dates=True, dayfirst=False)
        # print(filecontents)
    dailystatsdata = filecontents   # .tail()
    # print(dailystatsdata.info())
    datetime_object = pd.to_datetime(dailystatsdata['DateTime'], format=ISO_DATE_FORMAT)
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Day')
    ax1.set_ylabel('Median Weight Big (lbs)', color=linecolor_blue)
    formatter = DateFormatter("%d")
    ax1.xaxis.set_major_formatter(formatter)
    ax1.plot_date(x=datetime_object, y=dailystatsdata['WBigMed-Median'], xdate=True, ydate=False, color=linecolor_blue, marker="o", markersize=markersize_all)
    ax1.plot_date(x=datetime_object, y=dailystatsdata['WBigMed-Q1'], xdate=True, ydate=False, color=linecolor_blue, marker="v", markersize=markersize_all)
    ax1.plot_date(x=datetime_object, y=dailystatsdata['WBigMed-Q3'], xdate=True, ydate=False, color=linecolor_blue, marker="^", markersize=markersize_all)
    ax1.plot_date(x=datetime_object, y=dailystatsdata['WBigMed-Min'], xdate=True, ydate=False, color=linecolor_blue, marker="_", markersize=markersize_all)
    ax1.plot_date(x=datetime_object, y=dailystatsdata['WBigMed-Max'], xdate=True, ydate=False, color=linecolor_blue, marker="_", markersize=markersize_all)
    ax2 = ax1.twinx()
    ax2.plot_date(x=datetime_object, y=dailystatsdata['WSmlMed-Median'], xdate=True, ydate=False, color=linecolor_red, marker="o", markersize=markersize_all)
    ax2.plot_date(x=datetime_object, y=dailystatsdata['WSmlMed-Q1'], xdate=True, ydate=False, color=linecolor_red, marker="v", markersize=markersize_all)
    ax2.plot_date(x=datetime_object, y=dailystatsdata['WSmlMed-Q3'], xdate=True, ydate=False, color=linecolor_red, marker="^", markersize=markersize_all)
    ax2.plot_date(x=datetime_object, y=dailystatsdata['WSmlMed-Min'], xdate=True, ydate=False, color=linecolor_red, marker="_", markersize=markersize_all)
    ax2.plot_date(x=datetime_object, y=dailystatsdata['WSmlMed-Max'], xdate=True, ydate=False, color=linecolor_red, marker="_", markersize=markersize_all)
    ax2.set_ylabel('Median Weight Small (lbs)', color=linecolor_red)
    ax2.tick_params('y', colors=linecolor_red)
    plt.savefig(DAILYSTATS_FILENAME, dpi=300)
    # plt.show()
    if os.path.exists(DAILYSTATS_FILENAME):
        print("File exists")
        shutil.copyfile(DAILYSTATS_FILENAME, "/home/pi/Documents/Code/www/images/dailystats.jpg")
    else:
        IFTTTmsg("No Plot")

    with open(INPUTFILEPATH_TODAY, 'r') as inputfile:
        # print(inputfile)
        filecontents = pd.read_csv(inputfile, delimiter=',', index_col='DateTime')  # , parse_dates=[0], infer_datetime_format=True)      # nrows=5, index_col='DateTime'
    # print(filecontents.info())

    filecontents.index = pd.to_datetime(filecontents.index, format=ISO_DATETIME_FORMAT)
    # print(filecontents.info())
    column_list_left = ["WBigMed", "WSmlMed"]
    column_list_right = ["BigTemp", "WTemp"]
    # print(filecontents.index)
    # print(filecontents.DateTime)
    # print(filecontents.keys())
    ax1 = filecontents[column_list_left].plot(figsize=(5, 5), title="Today Plot", style=".", color=[linecolor_blue, linecolor_green], legend=False, markersize=markersize_all)
    # ax2 = ax1.twinx()
    ax2 = filecontents[column_list_right].plot(ax=ax1, secondary_y=True, style=".", color=[linecolor_red, linecolor_orange], legend=False, markersize=markersize_all)
    ax1.set_xlabel('Day-Hour')
    ax1.set_ylabel('Weight (lbs)', color=linecolor_blue)
    ax1.tick_params('y', colors=linecolor_blue)
    ax2.set_ylabel('Temps (F)', color=linecolor_red)
    ax2.tick_params('y', colors=linecolor_red)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    plt.legend(h1+h2, l1+l2, loc=2, fontsize=7)
    # formatter = DateFormatter("%H-%M")
    # ax1.xaxis.set_major_formatter(formatter)
    plt.savefig("/home/pi/Documents/Code/test.jpg", dpi=300)
    # plt.show()

    INPUTFILEPATH_WEIGHTLOG = "/home/pi/Documents/Code/" + str(YEAR) + "_WeightLog.csv"
    with open(INPUTFILEPATH_WEIGHTLOG, 'r') as inputfile:
        # print(inputfile)
        filecontents = pd.read_csv(inputfile, delimiter=',', index_col='DateTime')  # , parse_dates=[0], infer_datetime_format=True)      # nrows=5, index_col='DateTime'
    # print(filecontents.info())

    filecontents.index = pd.to_datetime(filecontents.index, format=ISO_DATETIME_FORMAT)
    # print(filecontents.info())
    column_list_left = ["WBigMed", "WSmlMed"]
    column_list_right = ["BigTemp", "WTemp"]
    # print(filecontents.index)
    # print(filecontents.DateTime)
    # print(filecontents.keys())
    ax1 = filecontents[column_list_left].plot(figsize=(5, 5), title="All Data", style=".", colormap="jet", legend=False, markersize=markersize_all)
    # ax2 = ax1.twinx()
    ax2 = filecontents[column_list_right].plot(ax=ax1, secondary_y=True, style=".", colormap="Dark2", legend=False, markersize=markersize_all)
    # plt.fill_between(filecontents.index, 95, 105, color='b', alpha=0.2)
    ax1.set_xlabel('Day-Hour')
    ax1.set_ylabel('Weight (lbs)', color=linecolor_blue)
    ax1.tick_params('y', colors=linecolor_blue)
    ax2.set_ylabel('Temps (F)', color=linecolor_red)
    ax2.tick_params('y', colors=linecolor_red)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    plt.legend(h1+h2, l1+l2, loc=2, fontsize=7)
    # formatter = DateFormatter("%H-%M")
    # ax1.xaxis.set_major_formatter(formatter)
    plt.savefig("/home/pi/Documents/Code/test_all.jpg", dpi=300)
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
