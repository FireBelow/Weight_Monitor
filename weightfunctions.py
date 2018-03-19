#!/usr/bin/python3

# WeightFunctions.py

import pandas as pd
import numpy as np
import RPi.GPIO as GPIO
import subprocess
import datetime
from hx711 import HX711		# import the class HX711
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import time
import logging

# TO DO:
# Plot daily all values
# Plot daily summary stats
# Daily stats summary

module_logger = logging.getLogger("WeightMonitor.WeightFunctions")


def read_scale(READINGS, DATAPIN, CLOCKPIN):
    '''Get n number of readings from the scale connected to Data and Clock pins'''

    logger = logging.getLogger("WeightMonitor.WeightFunctions.add")
    logger.info("reading scale")

    # initialize sensor
    hx = HX711(dout_pin=DATAPIN, pd_sck_pin=CLOCKPIN, gain=128, channel='A')

    # print("Reset")
    result = hx.reset()		# Before we start, reset the hx711 (not necessary)
    if result:			# you can check if the reset was successful
        print('Ready to use')
    else:
        print('not ready')

    # Read data several, or only one, time and return values it just returns exactly the number which hx711 sends argument times is not required default value is 1
    data = hx.get_raw_data(READINGS)
    # print('Raw data: ' + str(data))

    # if data != False:	# always check if you get correct value or only False
    #    print('Raw data: ' + str(data))
    # else:
    #    print('invalid data')

#    if (int(np.std(data)) > STDEVthreshold):
#        for i in 10:
#          data = hx.get_raw_data(READINGS)
#          if (int(np.std(data)) < STDEVthreshold):
#              break

#    print(type(data))
#    print(np.average(data))
#    print(np.median(data))
#    print(np.std(data))

    return data


def write_file(FILENAME, FILEOPERATION, SAVEDDATA):
    '''This writes data to the file specified'''

    logger = logging.getLogger("WeightMonitor.WeightFunctions.add")
    logger.info("writing file")

    with open(FILENAME, FILEOPERATION) as outputfile:		#recommended way to open files to ensure the file closes properly
        outputfile.write(SAVEDDATA)

    return


def check_web_response(cod_response):
    """This function accepts the website response code and returns a string describing the status"""
    if cod_response == 200:
        web_response_status = "Good Website Response"
    if cod_response == 404:
        web_response_status = "Website Site Not Found"
    if cod_response >= 500:
        web_response_status = "Website Server Error"

    print(web_response_status)
    IFTTTmsg(web_response_status)

    return web_response_status


def get_weather():
    '''Get weather data from openweather and weatherunderground'''

    # TO DO:
    # use UndergroundWeather observation time to make sure measurements are current/recent

    try:
        logger = logging.getLogger("WeightMonitor.WeightFunctions.add")
        logger.info("getting weather data")

        jsonfilename = "/home/pi/Documents/Code/private.json"
        with open(jsonfilename) as jsonfile:
            jsondata = json.load(jsonfile)          # read json
            # print(jsondata)
            # json.dump(newdata, jsonfile)           #write json
            Zip_Code = jsondata['weather']['zipcode']
            WeatherKeyWOpen = jsondata['weather']['openkey']
            WeatherKeyWUnder = jsondata['weather']['underkey']
            # print(Zip_Code)
            # print(WeatherKeyWOpen)
            # print(WeatherKeyWUnder)

        print("Get OpenWeather")
        weather_URL_open = "http://api.openweathermap.org/data/2.5/weather?zip=" + Zip_Code + "&appid=" + WeatherKeyWOpen + "&units=imperial"
        # print(weather_URL_open)
        weather_data_open = {}
        for i in range(3):
            WeatherStringOpen = requests.get(weather_URL_open, timeout=15)
            # print(WeatherStringOpen.json())
            weather_data_open = json.loads(WeatherStringOpen.text)
            # print(weather_data_open)
            # print(weather_data_open.keys())
            # print(weather_data_open["main"].keys())
            # print(weather_data_open["weather"][0].keys())

            if weather_data_open:
                print("WeatherOpen data exists")
                cod_response = weather_data_open["cod"]
                # print(cod_response)
                if cod_response != 200:
                    print("bad web response")
                    IFTTTmsg(check_web_response(cod_response))
                weather_output = ""
                main = weather_data_open["weather"][0]["main"]
                # print(main)
                weather_output = weather_output + main + ","
                description = weather_data_open["weather"][0]["description"].replace(" ","_")
                # print(description)
                weather_output = weather_output + description + ","
                temp = weather_data_open["main"]["temp"]
                # print(temp)
                weather_output = weather_output + str(temp) + ","
                pressure = weather_data_open["main"]["pressure"]
                # print(pressure)
                weather_output = weather_output + str(pressure) + ","
                humidity = weather_data_open["main"]["humidity"]
                # print(humidity)
                weather_output = weather_output + str(humidity) + ","
                WindSpeed = weather_data_open["wind"]["speed"]
                # print(WindSpeed)
                weather_output = weather_output + str(WindSpeed) + ","
                WindDeg = int(weather_data_open["wind"]["deg"])
                # print(WindDeg)
                weather_output = weather_output + str(WindDeg) + ","
                if "rain" in weather_data_open:
                    write_file("/home/pi/Documents/Code/000RAIN.txt",'w',str(weather_data_open))
                    print(weather_data_open["rain"].keys())
                    rain = weather_data_open["rain"]["3h"]
                    # print(rain)
                    weather_output = weather_output + str(rain) + ","
                else:
                    print("No rain")
                    rain = ""
                    weather_output = weather_output + str(rain) + ","
                if "snow" in weather_data_open:
                    write_file("/home/pi/Documents/Code/000SNOW.txt",'w',str(weather_data_open))
                    print(weather_data_open["snow"].keys())
                    snow = weather_data_open["snow"]["3h"]
                    # print(snow)
                    weather_output = weather_output + str(snow) + ","
                else:
                    print("No snow")
                    snow = ""
                    weather_output = weather_output + str(snow) + ","
                visibility = weather_data_open["visibility"]
                # print(visibility)
                weather_output = weather_output + str(visibility) + ","
                clouds = weather_data_open["clouds"]["all"]
                # print(clouds)
                weather_output = weather_output + str(clouds) + ","
                # print(weather_data_open["sys"]["sunrise"])
                sunrise = time.strftime("%H%M", time.localtime(int(weather_data_open["sys"]["sunrise"])))
                # print(sunrise)
                weather_output = weather_output + str(sunrise) + ","
                # print(weather_data_open["sys"]["sunset"])
                sunset = time.strftime("%H%M", time.localtime(int(weather_data_open["sys"]["sunset"])))
                # print(sunset)
                weather_output = weather_output + str(sunset) + ","
                # print(weather_output)
                break

        print("Get UnderWeather")
        weather_URL_under = "http://api.wunderground.com/api/" + WeatherKeyWUnder + "/conditions/q/pws:KDCWASHI163.json"
        # print(weather_URL_under)
        weather_data_under = {}
        for i in range(3):
            WeatherStringUnder=requests.get(weather_URL_under, timeout=15)
            # print(CurrentWeatherString.json())
            print("Parse UnderWeather")
            weather_data_under = json.loads(WeatherStringUnder.text)
            # print(weather_data)
            # print(weather_data["current_observation"].keys())

            if weather_data_under:
                print("WeatherUnder data exists")
                solarradiation = weather_data_under["current_observation"]["solarradiation"]
                # print(solarradiation)
                weather_output = weather_output + str(solarradiation) + ","
                UV = weather_data_under["current_observation"]["UV"]
                # print(UV)
                weather_output = weather_output + str(UV) + ","
                precip_1hr_in = weather_data_under["current_observation"]["precip_1hr_in"]
                # print(precip_1hr_in)
                weather_output = weather_output + str(precip_1hr_in) + ","
                precip_today_in = weather_data_under["current_observation"]["precip_today_in"]
                # print(precip_today_in)
                weather_output = weather_output + str(precip_today_in)      ######removed comma here since obs_time is not currently used
                observation_time = weather_data_under["current_observation"]["observation_time"]
                print(observation_time)
                # weather_output = "," + weather_output + str(observation_time)
                break

        # print(weather_output)
        return str(weather_output)

    except:
        IFTTTmsg('Weather Exception')
        # if weather_data_open:
        # print("weather_data_open not blank")
        write_file("/home/pi/Documents/Code/000WEATHERERROR.txt",'a', str(weather_data_open) + "\n")
        # if weather_data_under:
        # print("weather_data_under not blank")
        write_file("/home/pi/Documents/Code/000WEATHERERROR.txt",'a', str(weather_data_under) + "\n")
        raise
        # print("Exception")

    finally:
        print("All Done!")


def IFTTTmsg(MSG):
    '''Send IFTTT message'''

    jsonfilename = "/home/pi/Documents/Code/private.json"
    with open(jsonfilename) as jsonfile:
        jsondata = json.load(jsonfile)          #read json
        IFTTTKey = jsondata['IFTTT']['key']
        #print(IFTTTKey)

    payload = {'value1': MSG}
    # print(payload)
    print("Send IFTTT msg")
    IFTTT_website = "http://maker.ifttt.com/trigger/WeightMonitor/with/key/" + str(IFTTTKey)
    requests.post(IFTTT_website, data=payload)


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# make logger setup function
def  logger_setup(SCRIPTNAME, logger_level="info"):
    if logger_level == "debug":
        logger.setLevel(logging.DEBUG)
    if logger_level == "info":
        logger.setLevel(logging.INFO)
    if logger_level == "warning":
        logger.setLevel(logging.WARNING)
    if logger_level == "error":
        logger.setLevel(logging.ERROR)
    if logger_level == "critical":
        logger.setLevel(logging.CRITICAL)
    else:
        IFTTTmsg("Error setting loglevel: " + str(SCRIPTNAME))


def calculate():
    """Calculate stats on yesterday data"""
    # TO DO:
    # Use dictionary to read and edit/save daily values
    # use shape attribute to store number of readings for each day

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
        # print(TODAY)
        YESTERDAY = TODAY[0:6] + str((int(TODAY[6:]) - 1)).zfill(2)
        YEAR = YESTERDAY[0:4]
        # print(YESTERDAY)
        inputfilepath = "/home/pi/Documents/Code/" + YESTERDAY + "_WeightLog.csv"
        # inputfilepath = "/home/pi/Documents/Code/20180314_WeightLog.csv"
        outputfilepath_Daily = "/home/pi/Documents/Code/" + YEAR + "_DailyStats.csv"
        outputfilepath_Yearly = "/home/pi/Documents/Code/" + YEAR + "_WeightLog.csv"
        COMMA = ","
        datatosave = ""
        headers = ""
        observationthreshold = 12 * 24  # obs every 5 min per hour times 24 hrs

        print("Calculate Stats on Daily Readings")
        logger.info("Read CSV")
        with open(inputfilepath, "r") as inputfile:
            # print(inputfile)
            filecontents = pd.read_csv(inputfile, delimiter=',', parse_dates=True, dayfirst=False)      # nrows=5
        filecontents.WMain.astype("category")
        filecontents.WDesc.astype("category")
        # print(type(filecontents))
        # print(filecontents)
        # print(filecontents.columns)
        # print(filecontents.loc[:,["WSmlMed"]])
        # print(filecontents.info())
        # df.describe()
        # df.column.value_counts()

        # DateTime,WBigMed,WSmlMed,BigTemp,BigHum,SmlTemp,SmlHum,WMain,WDesc,WTemp,WPressure,WHumid,WWindSpd,WWindDir,WRain,WSnow,WVisible,WClouds,WSunrise,WSunset,Solar,UV,Precip1hr,PrecipToday,RawReadB,WBigStd,RawReadS,WSmlStd,Notes

        observationcount = filecontents.iloc[0].count()
        if observationcount < observationthreshold:
            print("missing datapoints")
            IFTTTmsg("Missing datapoints yesterday")

        # print(filecontents.DateTime)
        filedate = inputfilepath.split('_')
        # print(filedate)
        filedate = filedate[0].split('/')
        # print(filedate)
        filedate = filedate[-1]
        # print(filedate)
        filedate = filedate[0:4] + '-' + filedate[4:6] + '-' + filedate[6:8]
        # print(filedate)
        firstdateinfile = filecontents.iloc[0][0]
        firstdateinfile = firstdateinfile[0:10]
        # print(firstdateinfile)
        if filedate == firstdateinfile:
            print("Filename and Datalog Dates Match!")
        else:
            print("Not a match")
        logger.info("Calc Stats")
        for column in filecontents.columns:
            # print(type(filecontents[column]))
            print(column)
            # print(filecontents[column].dtypes)
            if filecontents[column].dtypes == np.float or filecontents[column].dtypes == np.int:
                # print(round(filecontents[column][0]))
                Mean = str(round(filecontents[column].mean(), 2))
                Median = str(round(filecontents[column].median(), 2))
                Stdev = str(round(filecontents[column].std(), 2))
                Min = str(round(filecontents[column].min(), 2))
                Max = str(round(filecontents[column].max(), 2))
                Q1 = str(round(filecontents[column].quantile(.25), 2))
                Q4 = str(round(filecontents[column].quantile(.75), 2))
                IQR = str(round(float(Q4) - float(Q1), 2))      # Inner Quartile Range (spread measure with Median)
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
                    if not filecontents[column].dtypes == np.float or not filecontents[column].dtypes == np.int:
                        print("Add string column: " + column)
                        headers = headers+column+"-Mean,"+column+"-Median,"+column+"-Std,"+column+"-Min,"+column+"-Max,"+column+"-Q1,"+column+"-Q4,"+column+"-IQR,"+column+"-Count"+COMMA
                        currentcolumndata = ",,,,,,,,"
                        datatosave = datatosave + COMMA + currentcolumndata
        headers = "DateTime," + headers + "\n"
        datatosave = filedate + datatosave + "\n"
        # print(headers)
        # print(currentcolumndata)
        # print(datatosave)

        # if filecontents.column.max() > filecontents.column.quartile(.75):
        #     print(str(filecontents.column.name) + " contains outliers")
        #     IFTTTmsg(str(filecontents.column.name) + " contains outliers")

        try:
            open(outputfilepath_Daily, 'r')
            print("File already exists")
        except:
            print("File does not exist")
            write_file(outputfilepath_Daily, 'w', headers)

        try:
            open(outputfilepath_Yearly, 'r')
            print("File already exists")
        except:
            print("File does not exist")
            write_file(outputfilepath_Yearly, 'w', headers)

        logger.info("Write data to file")
        # write_file(outputfilepath_Daily, 'a', headers)       #useful for testing header changes
        write_file(outputfilepath_Daily, 'a', datatosave)

        filecontents.iloc[1:].to_csv(outputfilepath_Yearly, mode='a', index=False, sep=",")

    except:
        IFTTTmsg("Calculate Exception")
        logging.exception("Calculate Exception")
        raise
        # print("Exception")

    finally:
        print("Done!")