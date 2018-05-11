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
    OUTPUTFILE_POLLEN = "/home/pi/Documents/Code/" + str(YEAR) + "_RainAmt.csv"
    jsonfilename = "/home/pi/Documents/Code/private.json"
    with open(jsonfilename) as jsonfile:
        jsondata = json.load(jsonfile)          # read json
        Zip_Code = jsondata['weather']['zipcode']
        PollenHeaders = jsondata['Headers']['PollenHeaders']

    URL_weathercom = "https://weather.com/forecast/agriculture/l/" + Zip_Code + ":4:US"
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
        print(pollen_yesterday)
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
    print(pollen_history)
    # print(pollen_history.keys())
    pollen_history_reportDate = pollen_history["reportDate"]
    pollen_history_reportDate = weather_date_only(pollen_history_reportDate)
    # print(pollen_history_reportDate)
    print("History: Tree, Grass, Weed, Mold, Pollen")
    pollen_history_tree = pollen_history["tree"]
    print(pollen_history_tree)
    pollen_history_grass = pollen_history["grass"]
    print(pollen_history_grass)
    pollen_history_weed = pollen_history["weed"]
    print(pollen_history_weed)
    pollen_history_mold = pollen_history["mold"]
    print(pollen_history_mold)
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
    print("Forecasts: Tree, Grass, Weed")
    pollen_forecast_tree = pollen_forecast["treePollenIndex"]
    print(pollen_forecast_tree)
    pollen_forecast_grass = pollen_forecast["grassPollenIndex"]
    print(pollen_forecast_grass)
    pollen_forecast_weed = pollen_forecast["ragweedPollenIndex"]
    print(pollen_forecast_weed)

    AllData = YESTERDAY.strftime(ISO_DATE_FORMAT) + "," \
        + str(pollen_yesterday_reportDate) + ","        \
        + str(pollen_yesterday_tree) + ","              \
        + str(pollen_yesterday_grass) + ","             \
        + str(pollen_yesterday_weed) + ","              \
        + str(pollen_yesterday_mold) + ","              \
        + str(pollen_yesterday_pollen) + ","            \
        + str(pollen_history_reportDate) + ","          \
        + str(pollen_history_tree) + ","                \
        + str(pollen_history_grass) + ","               \
        + str(pollen_history_weed) + ","                \
        + str(pollen_history_mold) + ","                \
        + str(pollen_history_pollen) + ","              \
        + str(pollen_forecast_reportDate) + ","         \
        + str(pollen_forecast_tree) + ","               \
        + str(pollen_forecast_grass) + ","              \
        + str(pollen_forecast_weed) + "\n"
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

    write_file(OUTPUTFILE_POLLEN, 'a', PollenHeaders)		# Useful for testing
    write_file(OUTPUTFILE_POLLEN, 'a', AllData)

except:
    IFTTTmsg('Pollen Exception')
    logging.exception("Pollen Exception")
    raise
    # print("Exception")

finally:
    print("Done")

# "vt1dailyForecast":[{
# "vt1dailyForecast":[{"validDate":"2018-05-10T07:00:00-0400","sunrise":"2018-05-10T06:00:10-0400","sunset":"2018-05-10T20:09:15-0400","moonIcon":"WNC","moonPhrase":"Waning Crescent","moonrise":"2018-05-10T03:33:01-0400","moonset":"2018-05-10T15:01:46-0400","dayOfWeek":"Thursday","snowQpf":0,"day":{"dayPartName":null,"precipPct":null,"precipAmt":null,"precipType":null,"temperature":null,"uvIndex":null,"uvDescription":null,"icon":null,"iconExtended":null,"phrase":null,"narrative":null,"cloudPct":null,"windDirCompass":null,"windDirDegrees":null,"windSpeed":null,"humidityPct":null,"qualifier":null,"snowRange":null,"thunderEnum":null,"thunderEnumPhrase":null},"night":{"dayPartName":"Tonight","precipPct":80,"precipAmt":0,"precipType":"rain","temperature":60,"uvIndex":0,"uvDescription":"Low","icon":47,"iconExtended":6200,"phrase":"Thunderstorms Early","narrative":"Thunderstorms early, then becoming clear after midnight. Low around 60F. Winds W at 5 to 10 mph. Chance of rain 80%.","cloudPct":24,"windDirCompass":"W","windDirDegrees":272,"windSpeed":8,"humidityPct":78,"qualifier":null,"snowRange":"","thunderEnum":2,"thunderEnumPhrase":"Thunder expected"}},{"validDate":"2018-05-11T07:00:00-0400","sunrise":"2018-05-11T05:59:12-0400","sunset":"2018-05-11T20:10:10-0400","moonIcon":"WNC","moonPhrase":"Waning Crescent","moonrise":"2018-05-11T04:03:38-0400","moonset":"2018-05-11T16:03:11-0400","dayOfWeek":"Friday","snowQpf":0,"day":{"dayPartName":"Tomorrow","precipPct":10,"precipAmt":0,"precipType":"rain","temperature":80,"uvIndex":8,"uvDescription":"Very High","icon":30,"iconExtended":3000,"phrase":"Partly Cloudy","narrative":"Partly cloudy skies in the morning will give way to cloudy skies during the afternoon. High near 80F. Winds NW at 5 to 10 mph.","cloudPct":49,"windDirCompass":"NW","windDirDegrees":326,"windSpeed":7,"humidityPct":51,"qualifier":null,"snowRange":"","thunderEnum":0,"thunderEnumPhrase":"No thunder"},"night":{"dayPartName":"Tomorrow night","precipPct":20,"precipAmt":0,"precipType":"rain","temperature":63,"uvIndex":0,"uvDescription":"Low","icon":27,"iconExtended":2700,"phrase":"Mostly Cloudy","narrative":"Mostly cloudy skies. A stray shower or thunderstorm is possible. Low 63F. Winds light and variable.","cloudPct":73,"windDirCompass":"SE","windDirDegrees":124,"windSpeed":5,"humidityPct":61,"qualifier":"A stray shower or thunderstorm is possible.","snowRange":"","thunderEnum":1,"thunderEnumPhrase":"Thunder possible"}},{"validDate":"2018-05-12T07:00:00-0400","sunrise":"2018-05-12T05:58:15-0400","sunset":"2018-05-12T20:11:05-0400","moonIcon":"WNC","moonPhrase":"Waning Crescent","moonrise":"2018-05-12T04:34:26-0400","moonset":"2018-05-12T17:06:55-0400","dayOfWeek":"Saturday","snowQpf":0,"day":{"dayPartName":"Saturday","precipPct":20,"precipAmt":0,"precipType":"rain","temperature":93,"uvIndex":7,"uvDescription":"High","icon":30,"iconExtended":3000,"phrase":"Partly Cloudy","narrative":"Sunshine and clouds mixed. A stray shower or thunderstorm is possible. High 93F. Winds SW at 10 to 15 mph.","cloudPct":50,"windDirCompass":"SW","windDirDegrees":222,"windSpeed":11,"humidityPct":48,"qualifier":"A stray shower or thunderstorm is possible.","snowRange":"","thunderEnum":1,"thunderEnumPhrase":"Thunder possible"},"night":{"dayPartName":"Saturday night","precipPct":30,"precipAmt":0.01,"precipType":"rain","temperature":65,"uvIndex":0,"uvDescription":"Low","icon":47,"iconExtended":3709,"phrase":"Isolated Thunderstorms","narrative":"A few isolated thunderstorms developing late. Low around 65F. Winds N at 5 to 10 mph. Chance of rain 30%.","cloudPct":74,"windDirCompass":"N","windDirDegrees":4,"windSpeed":7,"humidityPct":64,"qualifier":null,"snowRange":"","thunderEnum":2,"thunderEnumPhrase":"Thunder expected"}},{"validDate":"2018-05-13T07:00:00-0400","sunrise":"2018-05-13T05:57:19-0400","sunset":"2018-05-13T20:12:00-0400","moonIcon":"WNC","moonPhrase":"Waning Crescent","moonrise":"2018-05-13T05:06:53-0400","moonset":"2018-05-13T18:12:40-0400","dayOfWeek":"Sunday","snowQpf":0,"day":{"dayPartName":"Sunday","precipPct":20,"precipAmt":0,"precipType":"rain","temperature":70,"uvIndex":5,"uvDescription":"Moderate","icon":26,"iconExtended":2600,"phrase":"Cloudy","narrative":"Overcast. A stray shower or thunderstorm is possible. High around 70F. Winds E at 5 to 10 mph.","cloudPct":81,"windDirCompass":"E","windDirDegrees":86,"windSpeed":9,"humidityPct":70,"qualifier":"A stray shower or thunderstorm is possible.","snowRange":"","thunderEnum":1,"thunderEnumPhrase":"Thunder possible"},"night":{"dayPartName":"Sunday night","precipPct":60,"precipAmt":0.15,"precipType":"rain","temperature":59,"uvIndex":0,"uvDescription":"Low","icon":47,"iconExtended":6200,"phrase":"Thunderstorms Early","narrative":"Scattered thunderstorms during the evening, then cloudy skies overnight. Low 59F. Winds ENE at 5 to 10 mph. Chance of rain 60%.","cloudPct":78,"windDirCompass":"ENE","windDirDegrees":77,"windSpeed":8,"humidityPct":73,"qualifier":null,"snowRange":"","thunderEnum":2,"thunderEnumPhrase":"Thunder expected"}},{"validDate":"2018-05-14T07:00:00-0400","sunrise":"2018-05-14T05:56:24-0400","sunset":"2018-05-14T20:12:55-0400","moonIcon":"WNC","moonPhrase":"Waning Crescent","moonrise":"2018-05-14T05:41:43-0400","moonset":"2018-05-14T19:21:24-0400","dayOfWeek":"Monday","snowQpf":0,"day":{"dayPartName":"Monday","precipPct":40,"precipAmt":0.03,"precipType":"rain","temperature":84,"uvIndex":4,"uvDescription":"Moderate","icon":38,"iconExtended":7203,"phrase":"PM Thunderstorms","narrative":"Cloudy in the morning with scattered thunderstorms developing later in the day. High 84F. Winds N at 5 to 10 mph. Chance of rain 40%.","cloudPct":91,"windDirCompass":"N","windDirDegrees":352,"windSpeed":6,"humidityPct":57,"qualifier":null,"snowRange":"","thunderEnum":2,"thunderEnumPhrase":"Thunder expected"},"night":{"dayPartName":"Monday night","precipPct":20,"precipAmt":0,"precipType":"rain","temperature":65,"uvIndex":0,"uvDescription":"Low","icon":27,"iconExtended":2700,"phrase":"Mostly Cloudy","narrative":"Partly cloudy skies during the evening will give way to cloudy skies overnight. Low near 65F. Winds light and variable.","cloudPct":75,"windDirCompass":"E","windDirDegrees":80,"windSpeed":3,"humidityPct":73,"qualifier":null,"snowRange":"","thunderEnum":0,"thunderEnumPhrase":"No thunder"}},{"validDate":"2018-05-15T07:00:00-0400","sunrise":"2018-05-15T05:55:31-0400","sunset":"2018-05-15T20:13:49-0400","moonIcon":"N","moonPhrase":"New Moon","moonrise":"2018-05-15T06:19:54-0400","moonset":"2018-05-15T20:30:51-0400","dayOfWeek":"Tuesday","snowQpf":0,"day":{"dayPartName":"Tuesday","precipPct":40,"precipAmt":0.02,"precipType":"rain","temperature":87,"uvIndex":5,"uvDescription":"Moderate","icon":38,"iconExtended":7203,"phrase":"PM Thunderstorms","narrative":"Scattered thunderstorms developing during the afternoon. High 87F. Winds SSE at 5 to 10 mph. Chance of rain 40%.","cloudPct":75,"windDirCompass":"SSE","windDirDegrees":159,"windSpeed":7,"humidityPct":58,"qualifier":null,"snowRange":"","thunderEnum":2,"thunderEnumPhrase":"Thunder expected"},"night":{"dayPartName":"Tuesday night","precipPct":40,"precipAmt":0.04,"precipType":"rain","temperature":68,"uvIndex":0,"uvDescription":"Low","icon":47,"iconExtended":6200,"phrase":"Thunderstorms Early","narrative":"Scattered thunderstorms in the evening. Cloudy skies overnight. Low 68F. Winds S at 5 to 10 mph. Chance of rain 40%.","cloudPct":63,"windDirCompass":"S","windDirDegrees":189,"windSpeed":7,"humidityPct":70,"qualifier":null,"snowRange":"","thunderEnum":2,"thunderEnumPhrase":"Thunder expected"}},{"validDate":"2018-05-16T07:00:00-0400","sunrise":"2018-05-16T05:54:40-0400","sunset":"2018-05-16T20:14:42-0400","moonIcon":"WXC","moonPhrase":"Waxing Crescent","moonrise":"2018-05-16T07:04:17-0400","moonset":"2018-05-16T21:40:58-0400","dayOfWeek":"Wednesday","snowQpf":0,"day":{"dayPartName":"Wednesday","precipPct":20,"precipAmt":0,"precipType":"rain","temperature":81,"uvIndex":8,"uvDescription":"Very High","icon":30,"iconExtended":9003,"phrase":"AM Clouds/PM Sun","narrative":"Cloudy skies early will become partly cloudy later in the day. High 81F. Winds SSW at 10 to 15 mph.","cloudPct":67,"windDirCompass":"SSW","windDirDegrees":199,"windSpeed":11,"humidityPct":62,"qualifier":null,"snowRange":"","thunderEnum":0,"thunderEnumPhrase":"No thunder"},"night":{"dayPartName":"Wednesday night","precipPct":20,"precipAmt":0,"precipType":"rain","temperature":68,"uvIndex":0,"uvDescription":"Low","icon":27,"iconExtended":2700,"phrase":"Mostly Cloudy","narrative":"Mostly cloudy. Low 68F. Winds SSW at 10 to 15 mph.","cloudPct":73,"windDirCompass":"SSW","windDirDegrees":201,"windSpeed":10,"humidityPct":81,"qualifier":null,"snowRange":"","thunderEnum":0,"thunderEnumPhrase":"No thunder"}},{"validDate":"2018-05-17T07:00:00-0400","sunrise":"2018-05-17T05:53:50-0400","sunset":"2018-05-17T20:15:35-0400","moonIcon":"WXC","moonPhrase":"Waxing Crescent","moonrise":"2018-05-17T07:55:02-0400","moonset":"2018-05-17T22:47:22-0400","dayOfWeek":"Thursday","snowQpf":0,"day":{"dayPartName":"Thursday","precipPct":80,"precipAmt":0.13,"precipType":"rain","temperature":81,"uvIndex":6,"uvDescription":"High","icon":4,"iconExtended":400,"phrase":"Thunderstorms","narrative":"Scattered thunderstorms in the morning becoming more widespread in the afternoon. High 81F. Winds SSW at 5 to 10 mph. Chance of rain 80%.","cloudPct":84,"windDirCompass":"SSW","windDirDegrees":203,"windSpeed":8,"humidityPct":71,"qualifier":null,"snowRange":"","thunderEnum":2,"thunderEnumPhrase":"Thunder expected"},"night":{"dayPartName":"Thursday night","precipPct":80,"precipAmt":0.2,"precipType":"rain","temperature":66,"uvIndex":0,"uvDescription":"Low","icon":4,"iconExtended":400,"phrase":"Thunderstorms","narrative":"Thunderstorms in the evening, then variable clouds overnight with still a chance of showers. Low 66F. Winds SSW at 5 to 10 mph. Chance of rain 80%.","cloudPct":73,"windDirCompass":"SSW","windDirDegrees":202,"windSpeed":7,"humidityPct":82,"qualifier":null,"snowRange":"","thunderEnum":2,"thunderEnumPhrase":"Thunder expected"}},{"validDate":"2018-05-18T07:00:00-0400","sunrise":"2018-05-18T05:53:02-0400","sunset":"2018-05-18T20:16:28-0400","moonIcon":"WXC","moonPhrase":"Waxing Crescent","moonrise":"2018-05-18T08:52:28-0400","moonset":"2018-05-18T23:48:51-0400","dayOfWeek":"Friday","snowQpf":0,"day":{"dayPartName":"Friday","precipPct":50,"precipAmt":0.25,"precipType":"rain","temperature":72,"uvIndex":4,"uvDescription":"Moderate","icon":11,"iconExtended":1100,"phrase":"Showers","narrative":"Overcast with rain showers at times. High 72F. Winds S at 10 to 15 mph. Chance of rain 50%.","cloudPct":92,"windDirCompass":"S","windDirDegrees":178,"windSpeed":10,"humidityPct":76,"qualifier":null,"snowRange":"","thunderEnum":0,"thunderEnumPhrase":"No thunder"},"night":{"dayPartName":"Friday night","precipPct":50,"precipAmt":0.32,"precipType":"rain","temperature":60,"uvIndex":0,"uvDescription":"Low","icon":11,"iconExtended":1100,"phrase":"Showers","narrative":"Cloudy with occasional rain showers. Low around 60F. Winds E at 10 to 15 mph. Chance of rain 50%.","cloudPct":92,"windDirCompass":"E","windDirDegrees":84,"windSpeed":10,"humidityPct":84,"qualifier":null,"snowRange":"","thunderEnum":0,"thunderEnumPhrase":"No thunder"}},{"validDate":"2018-05-19T07:00:00-0400","sunrise":"2018-05-19T05:52:15-0400","sunset":"2018-05-19T20:17:20-0400","moonIcon":"WXC","moonPhrase":"Waxing Crescent","moonrise":"2018-05-19T09:55:59-0400","moonset":"","dayOfWeek":"Saturday","snowQpf":0,"day":{"dayPartName":"Saturday","precipPct":40,"precipAmt":0.11,"precipType":"rain","temperature":74,"uvIndex":4,"uvDescription":"Moderate","icon":11,"iconExtended":4600,"phrase":"Few Showers","narrative":"Cloudy with a few showers. High 74F. Winds ESE at 10 to 15 mph. Chance of rain 40%.","cloudPct":89,"windDirCompass":"ESE","windDirDegrees":112,"windSpeed":10,"humidityPct":64,"qualifier":null,"snowRange":"","thunderEnum":0,"thunderEnumPhrase":"No thunder"},"night":{"dayPartName":"Saturday night","precipPct":30,"precipAmt":0.04,"precipType":"rain","temperature":62,"uvIndex":0,"uvDescription":"Low","icon":45,"iconExtended":6100,"phrase":"Showers Early","narrative":"Showers in the evening, then cloudy overnight. Low 62F. Winds SSE at 5 to 10 mph. Chance of rain 30%.","cloudPct":89,"windDirCompass":"SSE","windDirDegrees":168,"windSpeed":8,"humidityPct":73,"qualifier":null,"snowRange":"","thunderEnum":0,"thunderEnumPhrase":"No thunder"}},{"validDate":"2018-05-20T07:00:00-0400","sunrise":"2018-05-20T05:51:30-0400","sunset":"2018-05-20T20:18:12-0400","moonIcon":"WXC","moonPhrase":"Waxing Crescent","moonrise":"2018-05-20T11:02:53-0400","moonset":"2018-05-20T00:42:32-0400","dayOfWeek":"Sunday","snowQpf":0,"day":{"dayPartName":"Sunday","precipPct":40,"precipAmt":0.08,"precipType":"rain","temperature":82,"uvIndex":7,"uvDescription":"High","icon":38,"iconExtended":3800,"phrase":"Scattered Thunderstorms","narrative":"Scattered thunderstorms, especially in the afternoon. High 82F. Winds S at 5 to 10 mph. Chance of rain 40%.","cloudPct":71,"windDirCompass":"S","windDirDegrees":169,"windSpeed":8,"humidityPct":59,"qualifier":null,"snowRange":"","thunderEnum":2,"thunderEnumPhrase":"Thunder expected"},"night":{"dayPartName":"Sunday night","precipPct":20,"precipAmt":0,"precipType":"rain","temperature":64,"uvIndex":0,"uvDescription":"Low","icon":27,"iconExtended":2700,"phrase":"Mostly Cloudy","narrative":"Mostly cloudy. Low 64F. Winds SSE at 5 to 10 mph.","cloudPct":66,"windDirCompass":"SSE","windDirDegrees":152,"windSpeed":8,"humidityPct":60,"qualifier":null,"snowRange":"","thunderEnum":0,"thunderEnumPhrase":"No thunder"}},{"validDate":"2018-05-21T07:00:00-0400","sunrise":"2018-05-21T05:50:46-0400","sunset":"2018-05-21T20:19:03-0400","moonIcon":"FQ","moonPhrase":"First Quarter","moonrise":"2018-05-21T12:10:41-0400","moonset":"2018-05-21T01:29:42-0400","dayOfWeek":"Monday","snowQpf":0,"day":{"dayPartName":"Monday","precipPct":30,"precipAmt":0.02,"precipType":"rain","temperature":84,"uvIndex":7,"uvDescription":"High","icon":37,"iconExtended":3700,"phrase":"Isolated Thunderstorms","narrative":"Partly to mostly cloudy with a slight chance of showers and thunderstorms in the afternoon. High 84F. Winds SE at 5 to 10 mph. Chance of rain 30%.","cloudPct":70,"windDirCompass":"SE","windDirDegrees":138,"windSpeed":9,"humidityPct":51,"qualifier":null,"snowRange":"","thunderEnum":2,"thunderEnumPhrase":"Thunder expected"},"night":{"dayPartName":"Monday night","precipPct":30,"precipAmt":0.09,"precipType":"rain","temperature":66,"uvIndex":0,"uvDescription":"Low","icon":47,"iconExtended":3709,"phrase":"Isolated Thunderstorms","narrative":"Partly cloudy with isolated thunderstorms possible. Low 66F. Winds SE at 5 to 10 mph. Chance of rain 30%.","cloudPct":70,"windDirCompass":"SE","windDirDegrees":145,"windSpeed":9,"humidityPct":57,"qualifier":null,"snowRange":"","thunderEnum":2,"thunderEnumPhrase":"Thunder expected"}},{"validDate":"2018-05-22T07:00:00-0400","sunrise":"2018-05-22T05:50:04-0400","sunset":"2018-05-22T20:19:53-0400","moonIcon":"WXG","moonPhrase":"Waxing Gibbous","moonrise":"2018-05-22T13:18:18-0400","moonset":"2018-05-22T02:09:53-0400","dayOfWeek":"Tuesday","snowQpf":0,"day":{"dayPartName":"Tuesday","precipPct":50,"precipAmt":0.14,"precipType":"rain","temperature":79,"uvIndex":7,"uvDescription":"High","icon":38,"iconExtended":3800,"phrase":"Scattered Thunderstorms","narrative":"Rain showers in the morning with scattered thunderstorms arriving in the afternoon. High 79F. Winds S at 5 to 10 mph. Chance of rain 50%.","cloudPct":65,"windDirCompass":"S","windDirDegrees":179,"windSpeed":8,"humidityPct":53,"qualifier":null,"snowRange":"","thunderEnum":2,"thunderEnumPhrase":"Thunder expected"},"night":{"dayPartName":"Tuesday night","precipPct":50,"precipAmt":0.17,"precipType":"rain","temperature":61,"uvIndex":0,"uvDescription":"Low","icon":47,"iconExtended":3809,"phrase":"Scattered Thunderstorms","narrative":"Scattered thunderstorms during the evening followed by occasional showers overnight. Low 61F. Winds S at 5 to 10 mph. Chance of rain 50%.","cloudPct":65,"windDirCompass":"S","windDirDegrees":179,"windSpeed":8,"humidityPct":64,"qualifier":null,"snowRange":"","thunderEnum":2,"thunderEnumPhrase":"Thunder expected"}},{"validDate":"2018-05-23T07:00:00-0400","sunrise":"2018-05-23T05:49:24-0400","sunset":"2018-05-23T20:20:43-0400","moonIcon":"WXG","moonPhrase":"Waxing Gibbous","moonrise":"2018-05-23T14:23:37-0400","moonset":"2018-05-23T02:45:50-0400","dayOfWeek":"Wednesday","snowQpf":0,"day":{"dayPartName":"Wednesday","precipPct":50,"precipAmt":0.13,"precipType":"rain","temperature":75,"uvIndex":7,"uvDescription":"High","icon":11,"iconExtended":1100,"phrase":"Showers","narrative":"Considerable cloudiness with occasional rain showers. High around 75F. Winds SSE at 5 to 10 mph. Chance of rain 50%.","cloudPct":66,"windDirCompass":"SSE","windDirDegrees":147,"windSpeed":9,"humidityPct":57,"qualifier":null,"snowRange":"","thunderEnum":0,"thunderEnumPhrase":"No thunder"},"night":{"dayPartName":"Wednesday night","precipPct":50,"precipAmt":0.25,"precipType":"rain","temperature":60,"uvIndex":0,"uvDescription":"Low","icon":11,"iconExtended":1100,"phrase":"Showers","narrative":"Cloudy with occasional rain showers. Low near 60F. Winds S at 5 to 10 mph. Chance of rain 50%.","cloudPct":68,"windDirCompass":"S","windDirDegrees":177,"windSpeed":8,"humidityPct":69,"qualifier":null,"snowRange":"","thunderEnum":0,"thunderEnumPhrase":"No thunder"}},{"validDate":"2018-05-24T07:00:00-0400","sunrise":"2018-05-24T05:48:46-0400","sunset":"2018-05-24T20:21:32-0400","moonIcon":"WXG","moonPhrase":"Waxing Gibbous","moonrise":"2018-05-24T15:28:13-0400","moonset":"2018-05-24T03:19:01-0400","dayOfWeek":"Thursday","snowQpf":0,"day":{"dayPartName":"Thursday","precipPct":50,"precipAmt":0.25,"precipType":"rain","temperature":74,"uvIndex":7,"uvDescription":"High","icon":11,"iconExtended":1100,"phrase":"Showers","narrative":"Considerable cloudiness with occasional rain showers. High 74F. Winds NW at 5 to 10 mph. Chance of rain 50%.","cloudPct":65,"windDirCompass":"NW","windDirDegrees":323,"windSpeed":9,"humidityPct":63,"qualifier":null,"snowRange":"","thunderEnum":0,"thunderEnumPhrase":"No thunder"},"night":{"dayPartName":"Thursday night","precipPct":60,"precipAmt":0.12,"precipType":"rain","temperature":59,"uvIndex":0,"uvDescription":"Low","icon":45,"iconExtended":6100,"phrase":"Showers Early","narrative":"Rain showers early with clearing later at night. Low 59F. Winds N at 5 to 10 mph. Chance of rain 60%.","cloudPct":54,"windDirCompass":"N","windDirDegrees":356,"windSpeed":6,"humidityPct":62,"qualifier":null,"snowRange":"","thunderEnum":0,"thunderEnumPhrase":"No thunder"}}]}},

# "ReportedConditions":{"prevDayHighF":78,"prevDayHighC":25,"prevDayLowF":50,"prevDayLowC":10,"prevDayPrecipIn":0,"prevDayPrecipMm":0,"sevenDayHighF":91,"sevenDayHighC":32,"sevenDayLowF":50,"sevenDayLowC":10,"sevenDayPrecipIn":0.11,"sevenDayPrecipMm":2.79,"mtdHighF":91,"mtdHighC":32,"mtdLowF":42,"mtdLowC":5,"mtdPrecipIn":0.11,"mtdPrecipMm":2.79}

# "HistoricalMonthlyAvg":{"currentMonthAvgHighF":77,"currentMonthAvgHighC":25,"currentMonthAvgLowF":55,"currentMonthAvgLowC":13,"currentMonthAvgPrecipIn":4.28,"currentMonthAvgPrecipMm":108.71,"nextMonthAvgHighF":86,"nextMonthAvgHighC":30,"nextMonthAvgLowF":65,"nextMonthAvgLowC":18,"nextMonthAvgPrecipIn":4.08,"nextMonthAvgPrecipMm":103.63,"monthAfterNextAvgHighF":90,"monthAfterNextAvgHighC":32,"monthAfterNextAvgLowF":70,"monthAfterNextAvgLowC":21,"monthAfterNextAvgPrecipIn":4.32,"monthAfterNextAvgPrecipMm":109.73}}},"ttl":3526,"date":1525988722000}},"CurrentDateTime":{