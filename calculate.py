#!/usr/bin/python3

#calculate.py

import pandas as pd
import numpy as np
import os
import logging
import time
from weightfunctions import read_scale, write_file, get_weather, IFTTTmsg

#TO DO:
#Use dictionary to read and edit/save daily values
#use shape attribute to store number of readings for each day

try:
    LogFileName = "/home/pi/Documents/Code/Log/calculate.log"
    logger = logging.getLogger("calculate")
    logger.setLevel(logging.INFO)

    # create the logging file handler
    LogHandler = logging.FileHandler(LogFileName)
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
    LogHandler.setFormatter(formatter)

    # # add handler to logger object
    logger.addHandler(LogHandler)
    logger.info("Program started")

    TODAY = time.strftime("%Y%m%d")
    #print(TODAY)
    YESTERDAY = TODAY[0:6] + str((int(TODAY[6:]) - 1)).zfill(2)
    #print(YESTERDAY)
    inputfilepath = "/home/pi/Documents/Code/" + YESTERDAY + "_WeightLog.csv"
    #INPUTFILEPATH = "/home/pi/Documents/Code/" + str(TODAY) + "_WeightLog.csv"
    outputfilepath = "/home/pi/Documents/Code/DailyStats.csv"
    COMMA = ","
    datatosave = ""
    headers = ""
    observationthreshold = 12 * 24  #obs every 5 min per hour times 24 hrs

    print("Calculate Stats on Daily Readings")
    logger.info("Read CSV")
    with open(inputfilepath,'r') as inputfile:
        #print(inputfile)
        filecontents = pd.read_csv(inputfile, delimiter=',', parse_dates=True, dayfirst=False)      #nrows=5
    #print(type(filecontents))
    #print(filecontents)
    #print(filecontents.columns)
    #print(filecontents.loc[:,["WSmlMed"]])
    #print(filecontents.info())
    # df.describe()
    # df.column.value_counts()

    #DateTime,WBigMed,WSmlMed,BigTemp,BigHum,SmlTemp,SmlHum,WMain,WDesc,WTemp,WPressure,WHumid,WWindSpd,WWindDir,WRain,WSnow,WVisible,WClouds,WSunrise,WSunset,Solar,UV,Precip1hr,PrecipToday,RawReadB,WBigStd,RawReadS,WSmlStd,Notes

    observationcount = filecontents.iloc[0].count()
    if observationcount < observationthreshold:
        print("missing datapoints")
        IFTTTmsg("Missing datapoints yesterday")

    #print(filecontents.DateTime)
    filedate = inputfilepath.split('_')
    #print(filedate)
    filedate = filedate[0].split('/')
    #print(filedate)
    filedate = filedate[-1]
    #print(filedate)
    filedate = filedate[0:4] + '-' + filedate[4:6] + '-' + filedate[6:8]
    print(filedate)
    firstdateinfile = filecontents.iloc[0][0]
    firstdateinfile = firstdateinfile[0:10]
    print(firstdateinfile)
    if filedate == firstdateinfile:
        print("Filename and Datalog Dates Match!")
    else:
        print("Not a match")
    logger.info("Calc Stats")
    for column in filecontents.columns:
        #print(type(filecontents[column]))
        print(column)
        if isinstance(filecontents[column][0], float or int):
            #print(column)
            # print(round(filecontents[column][0]))
            Mean = str(round(filecontents[column].mean(), 2))
            Median = str(round(filecontents[column].median(), 2))
            Stdev = str(round(filecontents[column].std(), 2))
            Min = str(round(filecontents[column].min(), 2))
            Max = str(round(filecontents[column].max(), 2))
            Q1 = str(round(filecontents[column].quantile(.25), 2))
            Q4 = str(round(filecontents[column].quantile(.75), 2))
            IQR = str(round(float(Q4) - float(Q1), 2))      #Inner Quartile Range (spread measure with Median)
            Count = str(round(filecontents[column].count(), 2))
            headers = headers+column+"-Mean,"+column+"-Median,"+column+"-Std,"+column+"-Min,"+column+"-Max,"+column+"-Q1,"+column+"-Q4,"+column+"-IQR,"+column+"-Count"+COMMA
            currentcolumndata = Mean + COMMA + Median + COMMA + Stdev + COMMA + Min + COMMA + Max + COMMA + Q1 + COMMA + Q4 + COMMA + IQR + COMMA + Count
            datatosave = datatosave + COMMA + currentcolumndata

            # print("Mean:" + Mean)
            # print("Median:" + Median)
            # print("Stdev:" + Stdev)
            # print("Min:" + Min)
            # print("Max:" + Max)
            # print("Q1:" + Q1)
            # print("Q4:" + Q4)
            # print("Count:" + Count)
            # print(headers)
            # print(currentcolumndata)
        else:
            if column == "DateTime":
                print("Skip " + column)
            else:
                if not isinstance(filecontents[column][0], float or int):
                    print("Add string column: " + column)
                    headers = headers+column+"-Mean,"+column+"-Median,"+column+"-Std,"+column+"-Min,"+column+"-Max,"+column+"-Q1,"+column+"-Q4,"+column+"-IQR,"+column+"-Count"+COMMA
                    currentcolumndata = ",,,,,,,,"
                    datatosave = datatosave + COMMA + currentcolumndata
    headers = "DateTime," + headers + "\n"
    datatosave = filedate + datatosave + "\n"
    # print(headers)
    # print(currentcolumndata)
    # print(datatosave)

    #pn.DataFrame(headers)
    logger.info("Write data to file")

    write_file(outputfilepath, 'a', headers)
    write_file(outputfilepath, 'a', datatosave)

#     pd.concat([uber1, uber2, uber3])        #concatenate each daily record into yearly log, use ignore_index if index values are not unique
# # Merge the DataFrames: o2o based on different names in the dataframes
# o2o = pd.merge(left=site, right=visited, left_on='name', right_on='site')

# #  Iterate over csv_files
# for csv in csv_files:
#     #  Read csv into a DataFrame: df
#     df = pd.read_csv(csv)
#     # Append df to frames
#     frames.append(df)           #might only need this line

# import re
# prog = re.compile('\d{3}-\d{3}-\d{4}')

# # See if the pattern matches
# result = prog.match('123-456-7890')
# print(bool(result))

# matches = re.findall('\d+', 'the recipe calls for 10 strawberries and 1 banana')  #should return two results with the +

# tips['total_dollar_replace'] = tips.total_dollar. apply(lambda x: x.replace('$', '')) #replace values in column for each value
# tips['total_dollar_re'] = tips.total_dollar.apply(lambda x: re.findall('\d+\.\d+', x)[0])

# df.drop_duplicates()    #remove duplicate entries (rows I think)
# df.Ozone.fillna(newvalue)       #replace missing values (NAN) with new value
# df.column.plot('hist')
# df.apply(function_name)         #apply function to columns
# df.apply(function_name, axis=1)         #apply function to rows

# # Assert that there are no missing values
# assert pd.notnull(ebola).all().all()    #asserts will return error if not true
# # Assert that all values are >= 0
# assert (ebola >= 0).all().all()

# plt.xlabel('Life Expectancy by Country in 1800')
# plt.ylabel('Life Expectancy by Country in 1899')
# plt.xlim(20, 55)
# plt.ylim(20, 55)

# from matplotlib.dates import (YEARLY, DateFormatter,
#                               rrulewrapper, RRuleLocator, drange)
# # tick every 5th easter
# rule = rrulewrapper(YEARLY, byeaster=1, interval=5)
# loc = RRuleLocator(rule)
# formatter = DateFormatter('%m/%d/%y')
# date1 = datetime.date(1952, 1, 1)
# date2 = datetime.date(2004, 4, 12)
# delta = datetime.timedelta(days=100)

# dates = drange(date1, date2, delta)
# s = np.random.rand(len(dates))  # make up some random y values

# fig, ax = plt.subplots()
# plt.plot_date(dates, s)
# ax.xaxis.set_major_locator(loc)
# ax.xaxis.set_major_formatter(formatter)
# ax.xaxis.set_tick_params(rotation=30, labelsize=10)

# #multi line, doesn't work with plot_date
# plt.plot(x,y, 'r--', x, y**2, 'bs', x, y**3, 'g^')

# import matplotlib.pyplot as plt
# import numpy as np              #not needed except for sample data

# t = np.arange(0.01, 5.0, 0.01)
# s1 = np.sin(2 * np.pi * t)
# s2 = np.exp(-t)
# s3 = np.sin(4 * np.pi * t)

# ax1 = plt.subplot(311)  #three rows, 1 col, graph index 1
# plt.plot(t, s1)
# plt.setp(ax1.get_xticklabels(), fontsize=6)

# # share x only
# ax2 = plt.subplot(312, sharex=ax1)      #three rows, 1 col, graph index 2
# plt.plot(t, s2)
# # make these tick labels invisible
# plt.setp(ax2.get_xticklabels(), visible=False)

# # share x and y
# ax3 = plt.subplot(313, sharex=ax1, sharey=ax1)  #three rows, 1 col, graph index 3
# plt.plot(t, s3)
# plt.xlim(0.01, 5.0)
# plt.show()
# #, facecolor='r' for red subplot color

        # df.info()
        # df["column"].value_counts(dropna=False) #finds missing data
        # df.describe()
        # df["column"].plot(kind='hist')
        # df.boxplot(column='GDP', by='country')
        # df["column"].plot(kind='scatter', x='colname', y='colname')
        # plt.show()
        # graphfilepath = ""
        # graphfilename = str(datetime) + "graph.jpeg"    #try jpeg first then png
        # plt.savefig('graph.png')
        # df[df['column'] > 1000]         #find outliers
        #df.column.astype('category') #use for weather? will reduce the size of the dataframe
        #tips['total_bill'] = pd.to_numeric(tips['total_bill'], errors='coerce') #convert object col to num


        #print(row[0])
        #for colname in row.column()
        #   print(row, colname)

        #Wind
        #360    270     180     90      0
        #N      W       S       E       N
        #Convert pandas array to numpy for speed?

    # {filecontents[0]["DateTime"]:{filecontents["WBigMed"]:{"Avg: filecontents["WBigMed"].mean(), "Med": filecontents["WBigMed"].median(), "Stdev": filecontents["WBigMed"].std(), "Min": filecontents["WBigMed"].min(), "Max": filecontents["WBigMed"].max()},
    #{{filecontents["WSmlMed"]:{"Avg: filecontents["WSmlMed"].mean(), "Med": filecontents["WSmlMed"].median(), "Stdev": filecontents["WSmlMed"].std(), "Min": filecontents["WSmlMed"].min(), "Max": filecontents["WSmlMed"].max()}}

except:
    IFTTTmsg("Calculate Exception")
    logging.exception("Calculate Exception")
    raise
    #print("Exception")

finally:
    print("Done!")