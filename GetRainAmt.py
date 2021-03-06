#!/usr/bin/python3

# GetPollen.py

import pandas as pd
import numpy as np
import RPi.GPIO as GPIO
import subprocess
import datetime
import time
import Adafruit_DHT
import os.path
import logging
import json
import requests
import re
import matplotlib.pyplot as plt
# import seaborn as sns
from hx711 import HX711                             # import the class HX711
from weightfunctions import read_scale, write_file, get_weather, IFTTTmsg, calculate, check_web_response, weather_date_only, get_rain_json
from matplotlib.dates import DateFormatter      # , YEARLY, rrulewrapper, RRuleLocator, drange)
import matplotlib.dates as dates

try:
    LogFileName = "/home/pi/Documents/Code/Log/RainAmt.log"
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # create the logging file handler
    LogHandler = logging.FileHandler(LogFileName)
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
    LogHandler.setFormatter(formatter)

    # # add handler to logger object
    logger.addHandler(LogHandler)
    logger.info("Program started")

    MINUS_ONE_DAY = datetime.timedelta(days=1)
    TODAY = datetime.datetime.now().date()
    print(TODAY, type(TODAY))
    YESTERDAY = TODAY - MINUS_ONE_DAY
    # print(YESTERDAY, type(YESTERDAY))
    YEAR = TODAY.year
    # print(YEAR, type(YEAR))
    ISO_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    ISO_DATE_FORMAT = "%Y-%m-%d"
    FILE_DATE_FORMAT = "%Y%m%d"
    OUTPUTFILE_RAIN = "/home/pi/Documents/Code/" + str(YEAR) + "_Rain.csv"
    jsonfilename = "/home/pi/Documents/Code/private.json"
    TEMP_FILEPATH = "/home/pi/Documents/Code/temp/rain_temp.html"
    RAIN_DATADUMP_FILEPATH = "/home/pi/Documents/Code/temp/rain_dump.html"
    with open(jsonfilename) as jsonfile:
        jsondata = json.load(jsonfile)          # read json
        Zip_Code = jsondata['weather']['zipcode']
        RainHeaders = jsondata['Headers']['RainHeaders']

    # URL_weathercom = "https://weather.com/forecast/agriculture/l/" + Zip_Code + ":4:US"
    # response = requests.get(URL_weathercom)
    # # print(response.text)
    # html_data = response.text
    # write_file(TEMP_FILEPATH, 'w', html_data)
    # html_data = html_data.split("window.__data=")
    # # print(data[1])
    # html_data = html_data[1].split(";window.experience={")
    # # print(html_data[0])
    # rain_data = json.loads(html_data[0])
    # prog = re.compile("<div class=\"lifestyle-precip-soil\">[A-Za-z ]*</div>")
    # # See if the pattern matches
    # result_past = prog.findall(html_data)
    # print(result_past)

    # Get All Rain Data
    rain_data = get_rain_json("agriculture", Zip_Code)
    # print(rain_data)
    print(type(rain_data))

    # Get Rain History Data
    isodate = weather_date_only([rain_data[0]["dal"]["FarmersAlmanac"]["language:en_US:location:{}:4:US".format(Zip_Code)]["data"]["FarmingAlmanacRecordHdr"]["isoDate"]])
    prevdayprecip = (rain_data[0]["dal"]["FarmersAlmanac"]["language:en_US:location:{}:4:US".format(Zip_Code)]["data"]["FarmingAlmanacRecordData"]["ReportedConditions"]["prevDayPrecipIn"])
    prevdaylow = (rain_data[0]["dal"]["FarmersAlmanac"]["language:en_US:location:{}:4:US".format(Zip_Code)]["data"]["FarmingAlmanacRecordData"]["ReportedConditions"]["prevDayLowF"])
    prevdayhi = (rain_data[0]["dal"]["FarmersAlmanac"]["language:en_US:location:{}:4:US".format(Zip_Code)]["data"]["FarmingAlmanacRecordData"]["ReportedConditions"]["prevDayHighF"])
    sevendayprecip = (rain_data[0]["dal"]["FarmersAlmanac"]["language:en_US:location:{}:4:US".format(Zip_Code)]["data"]["FarmingAlmanacRecordData"]["ReportedConditions"]["sevenDayPrecipIn"])
    sevendaylow = (rain_data[0]["dal"]["FarmersAlmanac"]["language:en_US:location:{}:4:US".format(Zip_Code)]["data"]["FarmingAlmanacRecordData"]["ReportedConditions"]["sevenDayLowF"])
    sevendayhi = (rain_data[0]["dal"]["FarmersAlmanac"]["language:en_US:location:{}:4:US".format(Zip_Code)]["data"]["FarmingAlmanacRecordData"]["ReportedConditions"]["sevenDayHighF"])
    monthprecip = (rain_data[0]["dal"]["FarmersAlmanac"]["language:en_US:location:{}:4:US".format(Zip_Code)]["data"]["FarmingAlmanacRecordData"]["ReportedConditions"]["mtdPrecipIn"])
    monthlow = (rain_data[0]["dal"]["FarmersAlmanac"]["language:en_US:location:{}:4:US".format(Zip_Code)]["data"]["FarmingAlmanacRecordData"]["ReportedConditions"]["mtdLowF"])
    monthhi = (rain_data[0]["dal"]["FarmersAlmanac"]["language:en_US:location:{}:4:US".format(Zip_Code)]["data"]["FarmingAlmanacRecordData"]["ReportedConditions"]["mtdHighF"])

    # Get Forecast Data
    # print(rain_data[0]["dal"]["DailyForecast"]["geocode:38.95,-77.02:language:en-US:units:e"]["data"]["vt1dailyForecast"][0]["day"].get("precipAmt"))
    rain_forecast_day = []
    rain_forecast_night = []
    for i in rain_data[0]["dal"]["DailyForecast"]["geocode:38.95,-77.02:language:en-US:units:e"]["data"]["vt1dailyForecast"]:
        rain_forecast_day.append(i["day"]["precipAmt"])
        rain_forecast_night.append(i["night"]["precipAmt"])
    print(rain_forecast_day)
    print(rain_forecast_night)

    # print(isodate, prevdayprecip, prevdaylow, prevdayhi, sevendayprecip, sevendaylow, sevendayhi, monthprecip, monthlow, monthhi)
    AllData = str(isodate) + "," +      \
        str(prevdayprecip) + "," +      \
        str(prevdaylow) + "," +         \
        str(prevdayhi) + "," +          \
        str(sevendayprecip) + "," +     \
        str(sevendaylow) + "," +        \
        str(sevendayhi) + "," +         \
        str(monthprecip) + "," +        \
        str(monthlow) + "," +           \
        str(monthhi) + "," +            \
        str(rain_data[1]) + "," +       \
        str(rain_forecast_day) + "," +  \
        str(rain_forecast_night) + "\n"
    AllData = AllData.replace("[", "")
    AllData = AllData.replace("]", "")
    AllData = AllData.replace("'", "")
    AllData = AllData.replace(" ", "")
    print(AllData)

    PrecipSummary = str(isodate) + "," +      \
        "ystr:" + str(prevdayprecip) + "," +             \
        "7day:" + str(sevendayprecip) + "," +            \
        "mnth:" + str(monthprecip) + "," +               \
        str(rain_data[1]) + "\n"
    print(PrecipSummary)

    # prog = re.compile("<div class=\"lifestyle-precip-soil\">[A-Za-z ]*</div>")
    # # See if the pattern matches
    # result_past = prog.findall(html_data)
    # print(result_past)

    # Get Yesterday Pollen data
    # "vt1pastPollen":{"reportDate":["2018-03-16T12:44:20.000-04:00"],"tree":[2],"grass":[0],"weed":[0],"mold":[1],"pollen":[25]}}
    # print("Yesterday " + str(result_past[0]))        # pollen data for yesterday
    # prog = re.compile("\:null\}")
    # if bool(prog.findall(result_past[0])):
    #     print("null found: weekend no data")
    #     pollen_yesterday_reportDate = ""
    #     pollen_yesterday_tree = ""
    #     pollen_yesterday_grass = ""
    #     pollen_yesterday_weed = ""
    #     pollen_yesterday_mold = ""
    #     pollen_yesterday_pollen = ""
    # else:
    #     data = result_past[0].split(":{")
    #     data = "{" + data[1]

    #     pollen_yesterday = json.loads(data)
    #     # pollen_yesterday = dict(eval(data))
    #     # print(pollen_yesterday)
    #     # print(pollen_yesterday.keys())
    #     pollen_yesterday_reportDate = pollen_yesterday["reportDate"][0]
    #     pollen_yesterday_reportDate = pollen_yesterday_reportDate.split("T")[0]
    #     # print(pollen_yesterday_reportDate)
    #     pollen_yesterday_tree = pollen_yesterday["tree"]
    #     # print(pollen_yesterday_tree)
    #     pollen_yesterday_grass = pollen_yesterday["grass"]
    #     # print(pollen_yesterday_grass)
    #     pollen_yesterday_weed = pollen_yesterday["weed"]
    #     # print(pollen_yesterday_weed)
    #     pollen_yesterday_mold = pollen_yesterday["mold"]
    #     # print(pollen_yesterday_mold)
    #     pollen_yesterday_pollen = pollen_yesterday["pollen"]
    #     # print(pollen_yesterday_pollen)
    #     print("Yesterday ", pollen_yesterday_reportDate, pollen_yesterday_tree, pollen_yesterday_grass, pollen_yesterday_weed, pollen_yesterday_mold, pollen_yesterday_pollen)

    # # All pollen history
    # # "vt1pastPollen":null}     #weekend null readings
    # # print("History " + str(result_past[1]))
    # prog = re.compile("\:null\}")
    # if bool(prog.findall(result_past[1])):
    #     print("null found: weekend no data")
    # else:
    #     data = result_past[1].split(":{")
    #     # print(data)
    #     data = "{" + data[1]
    #     # print(data)
    #     pollen_history = json.loads(data)
    #     # pollen_history = dict(eval(data))
    #     # print(pollen_history)
    #     # print(pollen_history.keys())
    #     pollen_history_reportDate = pollen_history["reportDate"]
    #     pollen_history_reportDate = weather_date_only(pollen_history_reportDate)
    #     # print(pollen_history_reportDate)
    #     print("History: Tree, Grass, Weed, Mold, Pollen")
    #     pollen_history_tree = pollen_history["tree"]
    #     print(pollen_history_tree)
    #     pollen_history_grass = pollen_history["grass"]
    #     print(pollen_history_grass)
    #     pollen_history_weed = pollen_history["weed"]
    #     print(pollen_history_weed)
    #     pollen_history_mold = pollen_history["mold"]
    #     print(pollen_history_mold)
    #     pollen_history_pollen = pollen_history["pollen"]
    #     print(len(pollen_history_pollen))     #get array length
    #     print(pollen_history_pollen)

    # # Get Pollen Forecast
    # # "vt1idxPollenDayPart":{"day":{"fcstValid":[1521370800,1521457200,1521543600,1521630000,1521716400,1521802800,1521889200,1521975600,1522062000,1522148400,1522234800,1522321200,1522407600,1522494000,1522580400],"fcstValidLocal":["2018-03-18T07:00:00-0400","2018-03-19T07:00:00-0400","2018-03-20T07:00:00-0400","2018-03-21T07:00:00-0400","2018-03-22T07:00:00-0400","2018-03-23T07:00:00-0400","2018-03-24T07:00:00-0400","2018-03-25T07:00:00-0400","2018-03-26T07:00:00-0400","2018-03-27T07:00:00-0400","2018-03-28T07:00:00-0400","2018-03-29T07:00:00-0400","2018-03-30T07:00:00-0400","2018-03-31T07:00:00-0400","2018-04-01T07:00:00-0400"],"dayInd":["D","D","D","D","D","D","D","D","D","D","D","D","D","D","D"],"num":[1,3,5,7,9,11,13,15,17,19,21,23,25,27,29],"daypartName":["Today","Tomorrow","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],"grassPollenIndex":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"grassPollenCategory":["None","None","None","None","None","None","None","None","None","None","None","None","None","None","None"],"treePollenIndex":[2,2,0,0,1,2,1,1,2,1,0,0,1,1,1],"treePollenCategory":["Moderate","Moderate","None","None","Low","Moderate","Low","Low","Moderate","Low","None","None","Low","Low","Low"],"ragweedPollenIndex":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"ragweedPollenCategory":["None","None","None","None","None","None","None","None","None","None","None","None","None","None","None"]},"night"
    # prog = re.compile("\"vt1idxPollenDayPart\"[A-Za-z0-9:\-\[\]\{\}\"\,\. ]*\"night\":\{\"fcstValid\"")
    # result_forecast = prog.findall(html_data)
    # # print("Forecast " + str(result_forecast))
    # data = result_forecast[0].split("night")
    # # print(data[0])
    # data = data[0].replace("\"vt1idxPollenDayPart\":{\"day\":", "")
    # # print(data)
    # data = data.replace("},\"", "}")
    # # print(data)
    # # data = data + "}"
    # # print(data)
    # data = data.replace("null", "\"null\"")
    # pollen_forecast = json.loads(data)
    # # pollen_forecast = dict(eval(data))
    # # print(pollen_forecast)
    # # print(pollen_forecast.keys())
    # # dict_keys(['ragweedPollenIndex', 'grassPollenCategory', 'grassPollenIndex', 'ragweedPollenCategory', 'treePollenCategory', 'num', 'treePollenIndex', 'fcstValidLocal', 'daypartName', 'fcstValid', 'dayInd'])
    # pollen_forecast_reportDate = pollen_forecast["fcstValidLocal"]
    # pollen_forecast_reportDate = weather_date_only(pollen_forecast_reportDate)
    # # print(pollen_forecast_reportDate)
    # print("Forecasts: Tree, Grass, Weed")
    # pollen_forecast_tree = pollen_forecast["treePollenIndex"]
    # print(pollen_forecast_tree)
    # pollen_forecast_grass = pollen_forecast["grassPollenIndex"]
    # print(pollen_forecast_grass)
    # pollen_forecast_weed = pollen_forecast["ragweedPollenIndex"]
    # print(len(pollen_forecast_weed))
    # print(pollen_forecast_weed)

    # AllData = YESTERDAY.strftime(ISO_DATE_FORMAT) + "," \
    #     + str(pollen_yesterday_reportDate) + ","        \
    #     + str(pollen_yesterday_tree) + ","              \
    #     + str(pollen_yesterday_grass) + ","             \
    #     + str(pollen_yesterday_weed) + ","              \
    #     + str(pollen_yesterday_mold) + ","              \
    #     + str(pollen_yesterday_pollen) + ","            \
    #     + str(pollen_history_reportDate) + ","          \
    #     + str(pollen_history_tree) + ","                \
    #     + str(pollen_history_grass) + ","               \
    #     + str(pollen_history_weed) + ","                \
    #     + str(pollen_history_mold) + ","                \
    #     + str(pollen_history_pollen) + ","              \
    #     + str(pollen_forecast_reportDate) + ","         \
    #     + str(pollen_forecast_tree) + ","               \
    #     + str(pollen_forecast_grass) + ","              \
    #     + str(pollen_forecast_weed) + "\n"
    # AllData = AllData.replace("[", "")
    # AllData = AllData.replace("]", "")
    # AllData = AllData.replace("'", "")
    # AllData = AllData.replace(" ", "")
    # print(AllData)

    if not os.path.isfile(OUTPUTFILE_RAIN):
        print("Create new file")
        write_file(OUTPUTFILE_RAIN, 'w', RainHeaders)        # create new file with headers

    try:
        open(OUTPUTFILE_RAIN, 'r')
        print("File already exists")
    except:
        print("File does not exist")
        write_file(OUTPUTFILE_RAIN, 'w', RainHeaders)

    # write_file(OUTPUTFILE_RAIN, 'a', RainHeaders)       # Useful for testing
    write_file(OUTPUTFILE_RAIN, 'a', AllData)
    IFTTTmsg(PrecipSummary)

except:
    logging.exception("RainAmt Exception")
    logger.info("Exception Encountered", exc_info=True)
    IFTTTmsg('RainAmt Exception')
    raise
    # print("Exception")

finally:
    with open(TEMP_FILEPATH, 'r') as outputfile: 
        temp_data = outputfile.read()
    write_file(RAIN_DATADUMP_FILEPATH, 'a', temp_data)
    # if os.path.exists(TEMP_FILEPATH):
    #     os.path.remove(TEMP_FILEPATH)
    print("Done")