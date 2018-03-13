#!/usr/bin/python3

#WeightFunctions.py

import pandas as pn
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

#TO DO:
#Plot daily all values
#Plot daily summary stats
#Daily stats summary

module_logger = logging.getLogger("WeightMonitor.WeightFunctions")

###add number of reads to make for hx711*****************
def read_scale(READINGS, DATAPIN, CLOCKPIN):
    '''Get n number of readings from the scale connected to Data and Clock pins'''

    logger = logging.getLogger("WeightMonitor.WeightFunctions.add")
    logger.info("reading scale")

    #initialize sensor
    hx = HX711(dout_pin=DATAPIN, pd_sck_pin=CLOCKPIN, gain=128, channel='A')
	
    #print("Reset")
    result = hx.reset()		# Before we start, reset the hx711 (not necessary)
    if result:			# you can check if the reset was successful
        print('Ready to use')
    else:
        print('not ready')
	
    # Read data several, or only one, time and return values it just returns exactly the number which hx711 sends argument times is not required default value is 1
    data = hx.get_raw_data(READINGS)
    #print('Raw data: ' + str(data))

    #if data != False:	# always check if you get correct value or only False
    #    print('Raw data: ' + str(data))
    #else:
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

def get_weather():
    '''Get weather data from openweather and weatherunderground'''

    #TO DO:
    #use UndergroundWeather observation time to make sure measurements are current/recent

    try:
        logger = logging.getLogger("WeightMonitor.WeightFunctions.add")
        logger.info("getting weather data")

        jsonfilename = "/home/pi/Documents/Code/private.json"
        with open(jsonfilename) as jsonfile:
            jsondata = json.load(jsonfile)          #read json
            #print(jsondata)
            #json.dump(newdata, jsonfile)           #write json
            Zip_Code = jsondata['weather']['zipcode']
            WeatherKeyWOpen = jsondata['weather']['openkey']
            WeatherKeyWUnder = jsondata['weather']['underkey']
            #print(Zip_Code)
            #print(WeatherKeyWOpen)
            #print(WeatherKeyWUnder)

        # ZIP_CODE_PATH="/home/pi/Documents/Code/ZipCode.key"
        # KEY_PATH_WOPEN="/home/pi/Documents/Code/Weather.key"
        # KEY_PATH_WUNDER="/home/pi/Documents/Code/WeatherUnder.key"

        # with open(ZIP_CODE_PATH, 'r') as file:
        #     Zip_Code = file.read()
        # #print(Zip_Code)
        # with open(KEY_PATH_WOPEN, 'r') as file:
        #     WeatherKeyWOpen = file.read()
        # #print(WeatherKeyWOpen)
        # with open(KEY_PATH_WUNDER, 'r') as file:
        #     WeatherKeyWUnder = file.read()
        # #print(WeatherKeyWUnder)

        print("Get OpenWeather")
        weather_URL_open = "http://api.openweathermap.org/data/2.5/weather?zip=" + Zip_Code + "&appid=" + WeatherKeyWOpen + "&units=imperial"
        #print(weather_URL_open)
        weather_data_open = {}
        for i in range(3):
            WeatherStringOpen = requests.get(weather_URL_open, timeout=15)
            #print(WeatherStringOpen.json())
            weather_data_open = json.loads(WeatherStringOpen.text)
            #print(weather_data_open)
            #print(weather_data_open.keys())
            #print(weather_data_open["main"].keys())
            #print(weather_data_open["weather"][0].keys())

            if weather_data_open:
                print("WeatherOpen data exists")
                weather_output = ""
                main = weather_data_open["weather"][0]["main"]
                #print(main)
                weather_output = weather_output + main + ","
                description = weather_data_open["weather"][0]["description"].replace(" ","_")
                #print(description)
                weather_output = weather_output + description + ","
                temp = weather_data_open["main"]["temp"]
                #print(temp)
                weather_output = weather_output + str(temp) + ","
                pressure = weather_data_open["main"]["pressure"]
                #print(pressure)
                weather_output = weather_output + str(pressure) + ","
                humidity = weather_data_open["main"]["humidity"]
                #print(humidity)
                weather_output = weather_output + str(humidity) + ","
                WindSpeed = weather_data_open["wind"]["speed"]
                #print(WindSpeed)
                weather_output = weather_output + str(WindSpeed) + ","
                WindDeg = int(weather_data_open["wind"]["deg"])
                #print(WindDeg)
                weather_output = weather_output + str(WindDeg) + ","
                if "rain" in weather_data_open:
                    write_file("/home/pi/Documents/Code/000RAIN.txt",'w',str(weather_data_open))
                    print(weather_data_open["rain"].keys())
                    rain = weather_data_open["rain"]["3h"]
                    #print(rain)
                    weather_output = weather_output + str(rain) + ","
                else:
                    print("No rain")
                    rain = ""
                    weather_output = weather_output + str(rain) + ","
                if "snow" in weather_data_open:
                    write_file("/home/pi/Documents/Code/000SNOW.txt",'w',str(weather_data_open))
                    print(weather_data_open["snow"].keys())
                    snow = weather_data_open["snow"]["3h"]
                    #print(snow)
                    weather_output = weather_output + str(snow) + ","
                else:
                    print("No snow")
                    snow = ""
                    weather_output = weather_output + str(snow) + ","
                visibility = weather_data_open["visibility"]
                #print(visibility)
                weather_output = weather_output + str(visibility) + ","
                clouds = weather_data_open["clouds"]["all"]
                #print(clouds)
                weather_output = weather_output + str(clouds) + ","
                #print(weather_data_open["sys"]["sunrise"])
                sunrise = time.strftime("%H%M", time.localtime(int(weather_data_open["sys"]["sunrise"])))
                #print(sunrise)
                weather_output = weather_output + str(sunrise) + ","
                #print(weather_data_open["sys"]["sunset"])
                sunset = time.strftime("%H%M", time.localtime(int(weather_data_open["sys"]["sunset"])))
                #print(sunset)
                weather_output = weather_output + str(sunset) + ","
                #print(weather_output)
                break

        print("Get UnderWeather")
        weather_URL_under = "http://api.wunderground.com/api/" + WeatherKeyWUnder + "/conditions/q/pws:KDCWASHI163.json"
        #print(weather_URL_under)
        weather_data_under = {}
        for i in range(3):
            WeatherStringUnder=requests.get(weather_URL_under, timeout=15)
            #print(CurrentWeatherString.json())
            print("Parse UnderWeather")
            weather_data_under = json.loads(WeatherStringUnder.text)
            #print(weather_data)
            #print(weather_data["current_observation"].keys())

            if weather_data_under:
                print("WeatherUnder data exists")
                solarradiation = weather_data_under["current_observation"]["solarradiation"]
                #print(solarradiation)
                weather_output = weather_output + str(solarradiation) + ","
                UV = weather_data_under["current_observation"]["UV"]
                #print(UV)
                weather_output = weather_output + str(UV) + ","
                precip_1hr_in = weather_data_under["current_observation"]["precip_1hr_in"]
                #print(precip_1hr_in)
                weather_output = weather_output + str(precip_1hr_in) + ","
                precip_today_in = weather_data_under["current_observation"]["precip_today_in"]
                #print(precip_today_in)
                weather_output = weather_output + str(precip_today_in)      ######removed comma here since obs_time is not currently used
                observation_time = weather_data_under["current_observation"]["observation_time"]
                print(observation_time)
                #weather_output = "," + weather_output + str(observation_time)
                break

        #print(weather_output)
        return str(weather_output)

    except:
        IFTTTmsg('Weather Exception')
        #if weather_data_open:
        #print("weather_data_open not blank")
        write_file("/home/pi/Documents/Code/000WEATHERERROR.txt",'a', str(weather_data_open) + "\n")
        #if weather_data_under:
        #print("weather_data_under not blank")
        write_file("/home/pi/Documents/Code/000WEATHERERROR.txt",'a', str(weather_data_under) + "\n")
        raise
        #print("Exception")

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
    #print(payload)
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

#make logger setup function
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