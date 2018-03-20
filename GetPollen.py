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
from weightfunctions import read_scale, write_file, get_weather, IFTTTmsg, calculate, check_web_response, weather_date_only
from matplotlib.dates import DateFormatter      # , YEARLY, rrulewrapper, RRuleLocator, drange)
import matplotlib.dates as dates

try:
    TODAY = time.strftime("%Y%m%d")
    # print(TODAY)
    YESTERDAY = TODAY[0:6] + str((int(TODAY[6:]) - 1)).zfill(2)
    YEAR = YESTERDAY[0:4]
    OUTPUTFILE_POLLEN = "/home/pi/Documents/Code/" + str(YEAR) + "_Pollen.csv"
    jsonfilename = "/home/pi/Documents/Code/private.json"
    with open(jsonfilename) as jsonfile:
        jsondata = json.load(jsonfile)          # read json
        Zip_Code = jsondata['weather']['zipcode']
        PollenHeaders = jsondata['Headers']['PollenHeaders']

    URL_weathercom = "https://weather.com/forecast/allergy/l/" + Zip_Code + ":4:US"
    response = requests.get(URL_weathercom)
    # print(response.text)
    html_data = response.text
    # write_file("/home/pi/Documents/Code/test.html", 'w', html_data)
    prog = re.compile("\"vt1pastPollen\"[A-Za-z0-9:\-\[\]\{\"\,\. ]*}")
    # See if the pattern matches
    result_past = prog.findall(html_data)
    # print(result_past)

    # Get Yesterday Pollen data
    # "vt1pastPollen":{"reportDate":["2018-03-16T12:44:20.000-04:00"],"tree":[2],"grass":[0],"weed":[0],"mold":[1],"pollen":[25]}}
    print(result_past[0])        # pollen data for yesterday
    prog = re.compile("\:null\}")
    if bool(prog.findall(result_past[0])):
        print("null found: weekend no data")
        pollen_yesterday_reportDate = ""
        pollen_yesterday_tree = ""
        pollen_yesterday_grass = ""
        pollen_yesterday_weed = ""
        pollen_yesterday_mold = ""
        pollen_yesterday_pollen = ""
    else:
        data = result_past[0].split(":{")
        data = "{" + data[1]

        pollen_yesterday = dict(eval(data))
        # print(pollen_yesterday)
        # print(pollen_yesterday.keys())
        pollen_yesterday_reportDate = pollen_yesterday["reportDate"][0]
        pollen_yesterday_reportDate = pollen_yesterday_reportDate.split("T")[0]
        # print(pollen_yesterday_reportDate)
        pollen_yesterday_tree = pollen_yesterday["tree"]
        # print(pollen_yesterday_tree)
        pollen_yesterday_grass = pollen_yesterday["grass"]
        # print(pollen_yesterday_grass)
        pollen_yesterday_weed = pollen_yesterday["weed"]
        # print(pollen_yesterday_weed)
        pollen_yesterday_mold = pollen_yesterday["mold"]
        # print(pollen_yesterday_mold)
        pollen_yesterday_pollen = pollen_yesterday["pollen"]
        # print(pollen_yesterday_pollen)

    # All pollen history
    # "vt1pastPollen":null}     #weekend null readings
    # print(result_past[1])
    data = result_past[1].split(":{")
    # print(data)
    data = "{" + data[1]
    # print(data)
    pollen_history = dict(eval(data))
    # print(pollen_history)
    # print(pollen_history.keys())
    pollen_history_reportDate = pollen_history["reportDate"]
    pollen_history_reportDate = weather_date_only(pollen_history_reportDate)
    # print(pollen_history_reportDate)
    pollen_history_tree = pollen_history["tree"]
    # print(pollen_history_tree)
    pollen_history_grass = pollen_history["grass"]
    # print(pollen_history_grass)
    pollen_history_weed = pollen_history["weed"]
    # print(pollen_history_weed)
    pollen_history_mold = pollen_history["mold"]
    # print(pollen_history_mold)
    pollen_history_pollen = pollen_history["pollen"]
    print(pollen_history_pollen)

    # Get Pollen Forecast
    # "vt1idxPollenDayPart":{"day":{"fcstValid":[1521370800,1521457200,1521543600,1521630000,1521716400,1521802800,1521889200,1521975600,1522062000,1522148400,1522234800,1522321200,1522407600,1522494000,1522580400],"fcstValidLocal":["2018-03-18T07:00:00-0400","2018-03-19T07:00:00-0400","2018-03-20T07:00:00-0400","2018-03-21T07:00:00-0400","2018-03-22T07:00:00-0400","2018-03-23T07:00:00-0400","2018-03-24T07:00:00-0400","2018-03-25T07:00:00-0400","2018-03-26T07:00:00-0400","2018-03-27T07:00:00-0400","2018-03-28T07:00:00-0400","2018-03-29T07:00:00-0400","2018-03-30T07:00:00-0400","2018-03-31T07:00:00-0400","2018-04-01T07:00:00-0400"],"dayInd":["D","D","D","D","D","D","D","D","D","D","D","D","D","D","D"],"num":[1,3,5,7,9,11,13,15,17,19,21,23,25,27,29],"daypartName":["Today","Tomorrow","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],"grassPollenIndex":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"grassPollenCategory":["None","None","None","None","None","None","None","None","None","None","None","None","None","None","None"],"treePollenIndex":[2,2,0,0,1,2,1,1,2,1,0,0,1,1,1],"treePollenCategory":["Moderate","Moderate","None","None","Low","Moderate","Low","Low","Moderate","Low","None","None","Low","Low","Low"],"ragweedPollenIndex":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"ragweedPollenCategory":["None","None","None","None","None","None","None","None","None","None","None","None","None","None","None"]},"night"
    prog = re.compile("\"vt1idxPollenDayPart\"[A-Za-z0-9:\-\[\]\{\}\"\,\. ]*\"night\":\{\"fcstValid\"")
    result_forecast = prog.findall(html_data)
    # print(result_forecast)
    data = result_forecast[0].split("night")
    # print(data[0])
    data = data[0].replace("\"vt1idxPollenDayPart\":{\"day\":", "")
    # print(data)
    data = data.replace("},\"", "}")
    # print(data)
    # data = data + "}"
    # print(data)
    data = data.replace("null", "\"null\"")
    pollen_forecast = dict(eval(data))
    # print(pollen_forecast)
    # print(pollen_forecast.keys())
    # dict_keys(['ragweedPollenIndex', 'grassPollenCategory', 'grassPollenIndex', 'ragweedPollenCategory', 'treePollenCategory', 'num', 'treePollenIndex', 'fcstValidLocal', 'daypartName', 'fcstValid', 'dayInd'])
    pollen_forecast_reportDate = pollen_forecast["fcstValidLocal"]
    pollen_forecast_reportDate = weather_date_only(pollen_forecast_reportDate)
    # print(pollen_forecast_reportDate)
    pollen_forecast_tree = pollen_forecast["treePollenIndex"]
    print(pollen_forecast_tree)
    pollen_forecast_grass = pollen_forecast["grassPollenIndex"]
    print(pollen_forecast_grass)
    pollen_forecast_weed = pollen_forecast["ragweedPollenIndex"]
    print(pollen_forecast_weed)

    AllData = YESTERDAY + "," + str(pollen_yesterday_reportDate) + "," + str(pollen_yesterday_tree) + "," + str(pollen_yesterday_grass) + "," + str(pollen_yesterday_weed) + "," + str(pollen_yesterday_mold) + "," + str(pollen_yesterday_pollen) + "," + str(pollen_history_reportDate) + "," + str(pollen_history_tree) + "," + str(pollen_history_grass) + "," + str(pollen_history_weed) + "," + str(pollen_history_mold) + "," + str(pollen_history_pollen) + "," + str(pollen_forecast_reportDate) + "," + str(pollen_forecast_tree) + "," + str(pollen_forecast_grass) + "," + str(pollen_forecast_weed) + "\n"
    AllData = AllData.replace("[", "")
    AllData = AllData.replace("]", "")
    AllData = AllData.replace("'", "")
    # print(AllData)

    try:
        open(OUTPUTFILE_POLLEN, 'r')
        print("File already exists")
    except:
        print("File does not exist")
        write_file(OUTPUTFILE_POLLEN, 'w', PollenHeaders)

    write_file(OUTPUTFILE_POLLEN, 'a', AllData)

except:
    IFTTTmsg('Pollen Exception')
    logging.exception("Pollen Exception")
    raise
    # print("Exception")

finally:
    print("Done")