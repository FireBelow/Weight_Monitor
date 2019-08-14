#!/usr/bin/python3

# WeightFunctions.py
# read_scale, write_file, check_web_response, get_weather, IFTTTmsg,
# requests_retry_session, logger_setup, calculate, weather_date_only

import pandas as pd
import numpy as np
import RPi.GPIO as GPIO
import subprocess
import datetime
from hx711 import HX711     # import the class HX711
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import os.path
import time
import logging
import re

# TO DO:
# Plot daily all values
# Plot daily summary stats
# Daily stats summary

module_logger = logging.getLogger(__name__)


def read_scale(READINGS, DATAPIN, CLOCKPIN):
    '''Get n number of readings from the scale connected to Data and Clock pins'''

    logger = logging.getLogger("WeightMonitor.WeightFunctions.add")
    logger.info("reading scale")

    # initialize sensor
    hx = HX711(dout_pin=DATAPIN, pd_sck_pin=CLOCKPIN, gain=128, channel='A')

    # print("Reset")
    result = hx.reset()     # Before we start, reset the hx711 (not necessary)
    if result:          # you can check if the reset was successful
        print('Ready to use')
    else:
        print('not ready')

    # Read data several, or only one, time and return values it just returns exactly the number which hx711 sends argument times is not required default value is 1
    data = hx.get_raw_data(READINGS)
    # print('Raw data: ' + str(data))

    # if data != False: # always check if you get correct value or only False
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


def file_exists_check(FILEPATH,ACTION,INITIAL_DATA=None):

    '''Check if file in FILEPATH exists, then if a new file is needed create it, and save optional data (like file headers)
       ACTION: 'check’ will just check if the file exists
       ACTION: 'create’ will make a new file if one does not exist and write initial data if INITIAL_DATA is not blank'''

    if os.path.isfile(FILEPATH):
            print('File Exists')
    else:
        # file does not exist
        if ACTION is 'check':
            print('File Missing')
        if ACTION is 'create':
            # create new blank file
            print('Create new file')
            if INITIAL_DATA is None:
                write_file(FILEPATH, 'w', None)        # create new file with no data
                print('Blank File Created')
            else:
                write_file(FILEPATH, 'w', INITIAL_DATA)        # create new file with INITIAL_DATA written
                print('File Created with Initial Data')

    return


def write_file(FILENAME, FILEOPERATION, SAVEDDATA):
    '''This writes data to the file specified'''

    logger = logging.getLogger("WeightMonitor.WeightFunctions.write_file.add")
    logger.info("writing file")

    try:
        with open(FILENAME, FILEOPERATION, encoding='utf-8') as outputfile:       # recommended way to open files to ensure the file closes properly
            outputfile.write(str(SAVEDDATA))
    except:
        IFTTTmsg("Write File Exception")
        logging.exception("Exception")
        logger.info("Exception Encountered", exc_info=True)
        raise

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
            Latitude = jsondata['weather']['lat']
            Longitude = jsondata['weather']['lon']
            WeatherKeyWOpen = jsondata['weather']['openkey']
            # WeatherKeyWUnder = jsondata['weather']['underkey']
            # print(Zip_Code)
            # print(WeatherKeyWOpen)
            # print(WeatherKeyWUnder)

        print("Get OpenWeather")
        logger.info("Get OpenWeather")
        weather_URL_open = "http://api.openweathermap.org/data/2.5/weather?zip=" + Zip_Code + "&appid=" + WeatherKeyWOpen + "&units=imperial"
        # print(weather_URL_open)
        weather_data_open = {}
        for i in range(3):
            WeatherStringOpen = requests.get(weather_URL_open, timeout=15)
            # print(WeatherStringOpen.json())
            if WeatherStringOpen.status_code != 200:
                print("Bad web response " + str(WeatherStringOpen.status_code))
                IFTTTmsg("Bad web response " + str(WeatherStringOpen.status_code))
                # Retry
                WeatherStringOpen = requests.get(weather_URL_open, timeout=15)
            weather_data_open = json.loads(WeatherStringOpen.text)
            # print(weather_data_open)
            # print(weather_data_open.keys())
            # print(weather_data_open["main"].keys())
            # print(weather_data_open["weather"][0].keys())

            if weather_data_open:
                # print("WeatherOpen data exists")
                # cod_response = weather_data_open["cod"]
                # print(cod_response)
                weather_output = ""
                if weather_data_open.get("weather") is "None":
                    if weather_data_open["weather"].get(0) is "None":
                        if weather_data_open["weather"][0].get("main") is "None":
                            main = ""
                        else:
                            main = weather_data_open["weather"][0]["main"]
                        if weather_data_open["weather"][0].get("description") is "None":
                            description = ""
                        else:
                            description = weather_data_open["weather"][0]["description"].replace(" ", "_")
                    else:
                        main = weather_data_open["weather"][0]["main"]
                        description = weather_data_open["weather"][0]["description"].replace(" ", "_")
                else:
                    main = weather_data_open["weather"][0]["main"]
                    description = weather_data_open["weather"][0]["description"].replace(" ", "_")
                # print(main)
                # print(description)
                weather_output = weather_output + main + "," + description + ","
                if weather_data_open.get("main") is None:
                    temp = ""
                    pressure = ""
                    humidity = ""
                else:
                    if weather_data_open["main"].get("temp") is None:
                        temp = ""
                    else:
                        temp = weather_data_open["main"]["temp"]
                        # print(temp)
                    if weather_data_open["main"].get("pressure") is None:
                        pressure = ""
                    else:
                        pressure = weather_data_open["main"]["pressure"]
                        # print(pressure)
                    if weather_data_open["main"].get("humidity") is None:
                        humidity = ""
                    else:
                        humidity = weather_data_open["main"]["humidity"]
                        # print(humidity)
                weather_output = weather_output + str(temp) + "," + str(pressure) + "," + str(humidity) + ","
                if weather_data_open.get("wind") is None:
                    WindSpeed = ""
                    WindDeg = ""
                else:
                    if weather_data_open["wind"].get("speed") is None:
                        WindSpeed = ""
                    else:
                        WindSpeed = weather_data_open["wind"]["speed"]
                        # print(WindSpeed)
                    if weather_data_open["wind"].get("deg") is None:
                        WindDeg = ""
                    else:
                        WindDeg = int(weather_data_open["wind"]["deg"])
                        # print(WindDeg)
                weather_output = weather_output + str(WindSpeed) + "," + str(WindDeg) + ","
                if weather_data_open.get("rain") is None:
                    print("No rain")
                    rain = ""
                else:
                    write_file("/home/pi/Documents/Code/000RAIN.txt", 'a', str(weather_data_open))
                    # print(weather_data_open["rain"].keys())
                    if weather_data_open["rain"].get("1h") is not None:
                        # IFTTTmsg("Rain Code is 1hr")
                        rain = weather_data_open["rain"]["1h"]
                    elif weather_data_open["rain"].get("3h") is not None:
                        IFTTTmsg("Rain Code is 3hr")
                        rain = weather_data_open["rain"]["3h"]
                    else:
                        IFTTTmsg(str(weather_data_open["rain"].keys()))
                    # print(rain)
                weather_output = weather_output + str(rain) + ","
                if weather_data_open.get("snow") is None:
                    print("No snow")
                    snow = ""
                else:
                    write_file("/home/pi/Documents/Code/000SNOW.txt", 'a', str(weather_data_open))
                    # print(weather_data_open["snow"].keys())
                    if weather_data_open["snow"].get("1h") is not None:
                        # IFTTTmsg("Snow Code is 1hr")
                        snow = weather_data_open["snow"]["1h"]
                    elif weather_data_open["snow"].get("3h") is not None:
                        IFTTTmsg("Snow Code is 3hr")
                        snow = weather_data_open["snow"]["3h"]
                    else:
                        IFTTTmsg(str(weather_data_open["snow"].keys()))
                    # print(snow)
                weather_output = weather_output + str(snow) + ","
                if weather_data_open.get("visibility") is None:
                    visibility = ""
                else:
                    visibility = weather_data_open["visibility"]
                    # print(visibility)
                weather_output = weather_output + str(visibility) + ","
                if weather_data_open.get("clouds") is None:
                    clouds = ""
                else:
                    if weather_data_open["clouds"].get("all") is None:
                        clouds = ""
                    else:
                        clouds = weather_data_open["clouds"]["all"]
                        # print(clouds)
                weather_output = weather_output + str(clouds) + ","
                if weather_data_open.get("sys") is None:
                    sunrise = ""
                    sunset = ""
                else:
                    if weather_data_open["sys"].get("sunrise") is None:
                        sunrise = ""
                    else:
                        # print(weather_data_open["sys"]["sunrise"])
                        sunrise = time.strftime("%H%M", time.localtime(int(weather_data_open["sys"]["sunrise"])))
                        # print(sunrise)
                    if weather_data_open["sys"].get("sunset") is None:
                        sunset = ""
                    else:
                        # print(weather_data_open["sys"]["sunset"])
                        sunset = time.strftime("%H%M", time.localtime(int(weather_data_open["sys"]["sunset"])))
                        # print(sunset)
                weather_output = weather_output + str(sunrise) + "," + str(sunset) + ","
                # print(weather_output)
                break

        # print("Get UnderWeather")
        # logger.info("Get UnderWeather")
        # weather_URL_under = "http://api.wunderground.com/api/" + WeatherKeyWUnder + "/conditions/q/pws:KDCWASHI255.json"
        # # print(weather_URL_under)
        # weather_data_under = {}
        # for i in range(3):
        #     WeatherStringUnder = requests.get(weather_URL_under, timeout=15)
        #     # print(WeatherStringUnder.json())
        #     # print("Parse UnderWeather")
        #     weather_data_under = json.loads(WeatherStringUnder.text)
        #     # print(weather_data)
        #     # print(weather_data_under["current_observation"].keys())

        #     if weather_data_under:
        #         # print("WeatherUnder data exists")
        #         if weather_data_under.get("current_observation") is None:
        #             solarradiation = ""
        #             UV = ""
        #             precip_1hr_in = ""
        #             precip_today_in = ""
        #         else:
        #             if weather_data_under["current_observation"].get("solarradiation") is None:
        #                 solarradiation = ""
        #             else:
        #                 solarradiation = weather_data_under["current_observation"]["solarradiation"]
        #                 # print(solarradiation)
        #             if weather_data_under["current_observation"].get("UV") is None:
        #                 UV = ""
        #             else:
        #                 UV = weather_data_under["current_observation"]["UV"]
        #                 # print(UV)
        #             if weather_data_under["current_observation"].get("precip_1hr_in") is None:
        #                 precip_1hr_in = ""
        #             else:
        #                 precip_1hr_in = weather_data_under["current_observation"]["precip_1hr_in"]
        #                 # print(precip_1hr_in)
        #             if weather_data_under["current_observation"].get("precip_today_in") is None:
        #                 precip_today_in = ""
        #             else:
        #                 precip_today_in = weather_data_under["current_observation"]["precip_today_in"]
        #                 # print(precip_today_in)
        #             if weather_data_under["current_observation"].get("observation_time") is None:
        #                 observation_time = ""
        #             else:
        #                 observation_time = weather_data_under["current_observation"]["observation_time"]
        #                 print(observation_time)
        #                 # DONT JUST ADD THIS weather_output = "," + weather_output + str(observation_time)
        #         weather_output = weather_output + str(solarradiation) + "," + str(UV) + "," + str(precip_1hr_in) + "," + str(precip_today_in)
        #         break

        # Previous Underground Weather Fields
        solarradiation = ""
        UV = ""
        precip_1hr_in = ""
        precip_today_in = ""

        # Get UV Data from Open Weather
        print("Get UV OpenWeather Reading")
        logger.info("Get UV OpenWeather")
        weather_URL_open_UV = "http://api.openweathermap.org/data/2.5/uvi?lat=" + Latitude + "&lon=" + Longitude + "&appid=" + WeatherKeyWOpen
        # print(weather_URL_open_UV)
        weather_data_open_UV = {}
        for i in range(3):
            WeatherStringOpen_UV = requests.get(weather_URL_open_UV, timeout=15)
            # print(WeatherStringOpen_UV.json())
            if WeatherStringOpen_UV.status_code != 200:
                print("Bad web response " + str(WeatherStringOpen_UV.status_code))
                IFTTTmsg("Bad web response " + str(WeatherStringOpen_UV.status_code))
                # Retry
                WeatherStringOpen_UV = requests.get(weather_URL_open_UV, timeout=15)
            weather_data_open_UV = json.loads(WeatherStringOpen_UV.text)
            # print(weather_data_open_UV)

            if weather_data_open_UV:
                if weather_data_open_UV.get("cod"):
                    print("UV Error: {}".format(weather_data_open_UV["cod"]))
                    print("UV_msg: {}".format(weather_data_open_UV["message"]))
                    break
                # print("WeatherOpen data exists")
                if weather_data_open_UV.get("value") is "None":
                    UV = ""
                else:
                    UV = weather_data_open_UV["value"]

        # print(weather_output)
        weather_output = weather_output + str(solarradiation) + "," + str(UV) + "," + str(precip_1hr_in) + "," + str(precip_today_in)

        # print(weather_output)
        return str(weather_output)

    except:
        logger.exception("Exception")
        logger.info("Exception Encountered", exc_info=True)
        IFTTTmsg('Weather Exception')
        # if weather_data_open:
        # print("weather_data_open not blank")
        write_file("/home/pi/Documents/Code/000WEATHERERROR.txt", 'a', str(weather_data_open) + "\n")
        # if weather_data_under:
        # print("weather_data_under not blank")
        # write_file("/home/pi/Documents/Code/000WEATHERERROR.txt", 'a',
        #            str(weather_data_under) + "\n")
        raise
        # print("Exception")

    finally:
        print("All Done!")


def get_open_forecast():
    # CurrentDateTime,Day1-00,Day1-03,Day1-06,Day1-09,Day1-12,Day1-15,Day1-18,Day1-21,Day1-24,Day2-00,Day2-03,Day2-06,Day2-09,Day2-12,Day2-15,Day2-18,Day2-21,Day2-24,Day3-00,Day3-03,Day3-06,Day3-09,Day3-12,Day3-15,Day3-18,Day3-21,Day3-24,Day4-00,Day4-03,Day4-06,Day4-09,Day4-12,Day4-15,Day4-18,Day4-21,Day4-24,Day5-00,Day5-03,Day5-06,Day5-09,Day5-12,Day5-15,Day5-18,Day5-21,Day5-24,Day6-00,Day6-03,Day6-06,Day6-09,Day6-12,Day6-15,Day6-18,Day6-21,Day6-24,
    # main
    # temp = FTemp
    # temp_min
    # temp_max
    # pressure = FPressure
    # sea_level
    # grnd_level
    # humidity = FHumid
    # weather
    # main = FMain
    # description = FDesc
    # clouds = FClouds
    # wind
    # speed = FWindSpd
    # deg = FWindDir
    # rain = FRain
    # snow = FSnow
    # dt_txt = Frcst_period

    logger = logging.getLogger('WeightMonitor.WeightFunctions.add')
    logger.info('getting weather data')

    jsonfilename = '/home/pi/Documents/Code/private.json'
    with open(jsonfilename) as jsonfile:
        jsondata = json.load(jsonfile)          # read json
        # print(jsondata)
        # json.dump(newdata, jsonfile)           #write json
        # Zip_Code = jsondata['weather']['zipcode']
        Latitude = jsondata['weather']['lat']
        Longitude = jsondata['weather']['lon']
        WeatherKeyWOpen = jsondata['weather']['openkey']
        ISO_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        # WeatherKeyWUnder = jsondata['weather']['underkey']
        # print(Zip_Code)
        # print(WeatherKeyWOpen)
        # print(WeatherKeyWUnder)

    try:
        print('Get OpenWeather Forecast')
        logger.info('Get OpenWeather')
        weather_URL_open_forecast = 'http://api.openweathermap.org/data/2.5/forecast?lat=' + Latitude + '&lon=' + Longitude + '&appid=' + WeatherKeyWOpen + '&units=imperial'
        # print(weather_URL_open_forecast)
        weather_data_open_forecast = {}
        for i in range(3):
            WeatherStringOpen_forecast = requests.get(weather_URL_open_forecast, timeout=15)
            # print(WeatherStringOpen_forecast.json())
            if WeatherStringOpen_forecast.status_code != 200:
                print('Bad web response ' + str(WeatherStringOpen_forecast.status_code))
                IFTTTmsg('Bad web response ' + str(WeatherStringOpen_forecast.status_code))
                # Retry
                WeatherStringOpen_forecast = requests.get(weather_URL_open_forecast, timeout=15)
            weather_data_open_forecast = json.loads(WeatherStringOpen_forecast.text)
            # print(weather_data_open_forecast)
            # print(weather_data_open_forecast.keys())
            # print(weather_data_open_forecast['main'].keys())
            # print(weather_data_open_forecast['weather'][0].keys())

            if weather_data_open_forecast:
                # print('WeatherOpen Forecast data exists')
                # print(weather_data_open_forecast)
                # cod_response = weather_data_open_forecast['cod']
                # print(cod_response)
                weather_forecast = {}
                this_periods_data = {}
                if weather_data_open_forecast.get('list') is not None:
                    i = 0
                    for threehours in weather_data_open_forecast['list']:
                        print("Current 3h period: {}".format(threehours))
                        # Get Other Weather Forecast Data
                        if weather_data_open_forecast['list'][0].get('dt_txt') is not None:
                            this_periods_data['Frcst_period'] = weather_data_open_forecast['list'][0]['dt_txt']
                        else:
                            this_periods_data['Frcst_period'] = ''
                        if weather_data_open_forecast['list'][0].get('clouds') is not None:
                            if weather_data_open_forecast['list'][0]['clouds'].get('all') is not None:
                                this_periods_data['FClouds'] = weather_data_open_forecast['list'][0]['clouds']['all']
                            else:
                                this_periods_data['FClouds'] = weather_data_open_forecast['list'][0]['clouds']
                        else:
                                this_periods_data['FClouds'] = ''
                        if weather_data_open_forecast['list'][0].get('wind') is not None:
                            if weather_data_open_forecast['list'][0]['wind'].get('speed') is not None:
                                this_periods_data['FWindSpd'] = weather_data_open_forecast['list'][0]['wind']['speed']
                            else:
                                this_periods_data['FWindSpd'] = ''
                            if weather_data_open_forecast['list'][0]['wind'].get('deg') is not None:
                                this_periods_data['FWindDir'] = weather_data_open_forecast['list'][0]['wind']['deg']
                            else:
                                this_periods_data['FWindDir'] = ''
                        else:
                            this_periods_data['FWindSpd'] = ''
                            this_periods_data['FWindDir'] = ''
                        if weather_data_open_forecast['list'][0].get('rain') is not None:
                            print(weather_data_open_forecast['list'][0].get('rain'))
                            if weather_data_open_forecast['list'][0]['rain'].get('3h') is not None:
                                this_periods_data['FRain'] = weather_data_open_forecast['list'][0]['rain']['3h']
                            else:
                                this_periods_data['FRain'] = weather_data_open_forecast['list'][0]['rain']
                        else:
                            this_periods_data['FRain'] = ''
                        if weather_data_open_forecast['list'][0].get('snow') is not None:
                            if weather_data_open_forecast['list'][0]['snow'].get('3h') is not None:
                                this_periods_data['FSnow'] = weather_data_open_forecast['list'][0]['snow']['3h']
                            else:
                                this_periods_data['FSnow'] = weather_data_open_forecast['list'][0]['snow']
                        else:
                            this_periods_data['FSnow'] = ''

                        # Get Main Forecast Data
                        main_data = {}
                        weather_types = ['temp','pressure','humidity']
                        if weather_data_open_forecast['list'][0].get('main') is not None:
                            for weather_type in weather_types:
                                if weather_data_open_forecast['list'][0]['main'].get(weather_type) is not None:
                                    main_data[weather_type] = weather_data_open_forecast['list'][0]['main'][weather_type]
                                else:
                                    main_data[weather_type] = ''
                            this_periods_data['FTemp'] = main_data['temp']
                            this_periods_data['FPressure'] = main_data['pressure']
                            this_periods_data['FHumid'] = main_data['humidity']

                        # Get Descriptive Weather Forecast Data
                        if weather_data_open_forecast['list'][0].get('weather') is not None:
                            # print(len(weather_data_open_forecast['list'][0]['weather']))
                            if len(weather_data_open_forecast['list'][0]['weather']) is 1:
                                this_periods_data['FMain0'] = weather_data_open_forecast['list'][0]['weather'][0]['main']
                                this_periods_data['FDesc0'] = weather_data_open_forecast['list'][0]['weather'][0]['description']
                            else:

                                this_periods_data['FMain1'] = weather_data_open_forecast['list'][0]['weather'][1]['main']
                                this_periods_data['FDesc1'] = weather_data_open_forecast['list'][0]['weather'][1]['description']
                        else:
                            this_periods_data['FMain0'] = ''
                            this_periods_data['FDesc0'] = ''
                            this_periods_data['FMain1'] = ''
                            this_periods_data['FDesc1'] = ''

                        # [Frcst_period+','+FClouds+','+FWindSpd+','+FWindDir+','+FRain+','+FSnow+','+FTemp+','+FPressure+','+FHumid+','+FMain0+','+FDesc0+','+FMain1+','+FDesc1]
                        print(this_periods_data)
                        weather_forecast[i] = this_periods_data
                        i = i + 1
                    Forecast = time.strftime(ISO_DATETIME_FORMAT)
                    periods = range(0, 39, 1)
                    for period in periods:
                        Forecast = Forecast + ',' + str(weather_forecast[period])
                    print('Forcast: {}'.format(Forecast))
        return str(Forecast)
    except:
        logging.exception("Exception")
        logger.info("Exception Encountered", exc_info=True)
        IFTTTmsg("OpenWeather Exception")
        raise


def IFTTTmsg(MSG):
    '''Send IFTTT message'''

    jsonfilename = "/home/pi/Documents/Code/private.json"
    with open(jsonfilename) as jsonfile:
        jsondata = json.load(jsonfile)          # read json
        IFTTTKey = jsondata['IFTTT']['key']
        # print(IFTTTKey)

    payload = {'value1': MSG}
    # print(payload)
    print("Send IFTTT msg")
    IFTTT_website = "http://maker.ifttt.com/trigger/WeightMonitor/with/key/" + str(IFTTTKey)
    requests.post(IFTTT_website, data=payload)


def requests_retry_session(retries=3, backoff_factor=0.3,
                           status_forcelist=(500, 502, 504),
                           session=None):
    session = session or requests.Session()
    retry = Retry(total=retries, read=retries, connect=retries,
                  backoff_factor=backoff_factor,
                  status_forcelist=status_forcelist)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def logger_setup(SCRIPTNAME, logger_level="info"):
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
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # create the logging file handler
        LogHandler = logging.FileHandler(LogFileName)
        formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
        LogHandler.setFormatter(formatter)

        # # add handler to logger object
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

        inputfilepath = "/home/pi/Documents/Code/" + YESTERDAY.strftime(FILE_DATE_FORMAT) + "_WeightLog.csv"
        # inputfilepath = "/home/pi/Documents/Code/20180331_WeightLog.csv"
        outputfilepath_Daily = "/home/pi/Documents/Code/" + str(YEAR) + "_DailyStats.csv"
        outputfilepath_Yearly_csv = "/home/pi/Documents/Code/" + str(YEAR) + "_WeightLog.csv"
        outputfilepath_Yearly_xlsx = "/home/pi/Documents/Code/" + str(YEAR) + "_WeightLog.xlsx"
        COMMA = ","
        datatosave = ""
        headers = ""
        observationthreshold = (12 * 24) * 0.9  # 90% of observation every 5 min each hour times 24 hrs

        jsonfilename = "/home/pi/Documents/Code/private.json"
        with open(jsonfilename) as jsonfile:
            jsondata = json.load(jsonfile)          # read json
            # print(jsondata)
            # json.dump(newdata, jsonfile)           #write json
            Headers_yearly = jsondata['Headers']['All']
            # print(Headers)
        # Headers = "DateTime,WBigMed,WSmlMed,BigTemp,BigHum,SmlTemp,SmlHum,WMain,WDesc,WTemp,WPressure,WHumid,WWindSpd,WWindDir,WRain,WSnow,WVisible,WClouds,WSunrise,WSunset,Solar,UV,Precip1hr,PrecipToday,RawReadB,WBigStd,RawReadS,WSmlStd,Notes\n"

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
            print("Filename and Datalog Dates Not a match")
            IFTTTmsg("Filename and Datalog Dates Not a match")
            logger.info("Filename and Datalog Dates Not a match")
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
                Q3 = str(round(filecontents[column].quantile(.75), 2))
                IQR = str(round(float(Q3) - float(Q1), 2))      # Inner Quartile Range (spread measure with Median)
                Count = str(round(filecontents[column].count(), 2))
                headers = headers+column+"-Mean,"+column+"-Median,"+column+"-Std,"+column+"-Min,"+column+"-Max,"+column+"-Q1,"+column+"-Q3,"+column+"-IQR,"+column+"-Count"+COMMA
                currentcolumndata = Mean + COMMA + Median + COMMA + Stdev + COMMA + Min + COMMA + Max + COMMA + Q1 + COMMA + Q3 + COMMA + IQR + COMMA + Count
                datatosave = datatosave + COMMA + currentcolumndata

                # print("Mean:" + Mean)
                # print("Median:" + Median)
                # print("Stdev:" + Stdev)
                # print("Min:" + Min)
                # print("Max:" + Max)
                # print("Q1:" + Q1)
                # print("Q3:" + Q3)
                # print("Count:" + Count)
                # print(headers)
                # print(currentcolumndata)
            else:
                if column == "DateTime":
                    print("Skip " + column)
                else:
                    if not filecontents[column].dtypes == np.float or not filecontents[column].dtypes == np.int:
                        print("Add string column: " + column)
                        headers = headers+column+"-Mean,"+column+"-Median,"+column+"-Std,"+column+"-Min,"+column+"-Max,"+column+"-Q1,"+column+"-Q3,"+column+"-IQR,"+column+"-Count"+COMMA
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
            open(outputfilepath_Yearly_csv, 'r')
            print("File already exists")
        except:
            print("File does not exist")
            write_file(outputfilepath_Yearly_csv, 'w', Headers_yearly)

        try:
            open(outputfilepath_Yearly_xlsx, 'r')
            print("File already exists")
        except:
            print("File does not exist")
            write_file(outputfilepath_Yearly_xlsx, 'w', Headers_yearly)

        logger.info("Write calc data to file")
        # write_file(outputfilepath_Daily, 'a', headers)       #useful for testing header changes
        write_file(outputfilepath_Daily, 'a', datatosave)

        filecontents.to_csv(outputfilepath_Yearly_csv, mode='a', header=False, index=False, sep=",")
        excel_writer = pd.ExcelWriter(outputfilepath_Yearly_xlsx)
        filecontents.to_excel(excel_writer, header=False, index=False)

    except:
        logging.exception("Calculate Exception")
        logger.info("Exception Encountered", exc_info=True)
        IFTTTmsg("Calculate Exception")
        raise
        # print("Exception")

    finally:
        print("Done!")


def weather_date_only(date_list):
        history_dates = []
        for i in date_list:
            history_dates.append(i.split("T")[0])
            # print(history_dates)
        return history_dates


def get_rain_json(forecast, zipcode):
    TEMP_FILEPATH = "/home/pi/Documents/Code/rain_temp.html"
    if forecast is "allergy":
        URL_weathercom = "https://weather.com/forecast/allergy/l/" + zipcode + ":4:US"
    if forecast is "agriculture":
        URL_weathercom = "https://weather.com/forecast/agriculture/l/" + zipcode + ":4:US"
    else:
        print("wrong forecast format")
        return
    response = requests.get(URL_weathercom)
    # print(response.text)
    html_data = response.text
    write_file(TEMP_FILEPATH, 'w', html_data)

    prog = re.compile("<div class=\"lifestyle-precip-soil\">[A-Za-z ]*</div>")
    # See if the pattern matches
    result_past = prog.findall(html_data)
    # print(result_past)
    soil_moisture = []
    for i in result_past:
        soil_moisture.append(i.split("<div class=\"lifestyle-precip-soil\">")[1])
    result_past = soil_moisture
    soil_moisture = []
    for i in result_past:
        soil_moisture.append(i.split("</div>")[0])
    print(soil_moisture)

    html_data = html_data.split("window.__data=")
    # print(data[1])
    html_data = html_data[1].split(";window.experience={")
    # print(html_data[0])

    return [json.loads(html_data[0]), soil_moisture]
