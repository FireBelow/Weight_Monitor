#!/usr/bin/python3

#Weight_Monitor.py

import pandas as pn
import numpy as np
import RPi.GPIO as GPIO
import subprocess
import datetime
import time
import Adafruit_DHT
import os.path
import logging
from hx711 import HX711                             # import the class HX711
from weightfunctions import read_scale, write_file, get_weather, IFTTTmsg

#TO DO:
#read last reading and look for crazy deltas
#watch for huge and negative weights
#initialize variables
#log exceptions details and errors
#make script to check if log updates are current, use tail()

try:
    LogFileName = "/home/pi/Documents/Code/Log/Monitor.log"
    logger = logging.getLogger("WeightMonitor")
    logger.setLevel(logging.INFO)

    # create the logging file handler
    LogHandler = logging.FileHandler(LogFileName)
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
    LogHandler.setFormatter(formatter)

    # # add handler to logger object
    logger.addHandler(LogHandler)
    logger.info("Program started")

    # start = time.time()
    # end = time.time() - start

    TODAY = time.strftime("%Y%m%d")
    OUTPUTFILE = "/home/pi/Documents/Code/" + str(TODAY) + "_WeightLog.csv"
    #print(OUTPUTFILE)
    Headers = "DateTime,WBigMed,WSmlMed,BigTemp,BigHum,SmlTemp,SmlHum,WMain,WDesc,WTemp,WPressure,WHumid,WWindSpd,WWindDir,WRain,WSnow,WVisible,WClouds,WSunrise,WSunset,Solar,UV,Precip1hr,PrecipToday,RawReadB,WBigStd,RawReadS,WSmlStd,Notes\n"
    try:
        open(OUTPUTFILE, 'r')
        print("File already exists")
    except:
        #TODAY = time.strftime("%Y%m%d")
        #OUTPUTFILE = "/home/pi/Documents/Code/" + str(TODAY) + "_WeightLog.csv"
        print("File does not exist")
        write_file(OUTPUTFILE, 'w', Headers)


    #WeatherData = subprocess.check_output(['/home/pi/Documents/Code/weather.sh'], universal_newlines=True)      #univ lines makes the output a text stream
    #WeatherData = WeatherData.replace("\n","")
    #print(WeatherData)

    WeatherData = get_weather()
    print(WeatherData)

    def read_retry_multi(sensor, pin, retries=15, delay_seconds=2, platform=None, num_reads=5):
        """Reads sensor using "read_retry" multiple times (num_reads) and returns
        data as a list"""
        data_list = []
        while len(data_list) < num_reads:
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin, retries, delay_seconds, platform)
            if humidity is not None and temperature is not None:
                TempHum = (round(humidity,2), round(temperature,2))
                data_list.append(TempHum)

        return data_list

    SENSOR_TYPE = Adafruit_DHT.DHT22
    BIG_TEMPHUM_PIN = 16    #change to big Pin
    DHT_NUM_READS = 5
    #BIGhumidity, BIGtemperature = Adafruit_DHT.read_retry(sensortype, BIG_TEMPHUM_PIN)       #def read_retry(sensor, pin, retries=15, delay_seconds=2, platform=None):
    #print(Adafruit_DHT.read_retry(sensortype, BIG_TEMPHUM_PIN))
    print("Read BIGtemphum")
    BIGtemphum = read_retry_multi(SENSOR_TYPE, BIG_TEMPHUM_PIN, DHT_NUM_READS)        #def read_retry(sensor, pin, retries=15, delay_seconds=2, platform=None):
    #print(BIGtemphum)
    #print(BIGtemphum[0][0])
    #print(BIGtemphum[:][0])
    BIGtemperature = [temp * (9 / 5) + 32 for temp, humid in BIGtemphum]       #convert from Celcius to F
    BIGhumidity = [humid for temp, humid in BIGtemphum]
    #print(BIGtemperature)
    #print(BIGhumidity)
    print(round(np.mean(BIGtemperature), 2), 
        round(np.median(BIGtemperature), 2), 
        round(np.std(BIGtemperature), 2))
    print(round(np.mean(BIGhumidity), 2), 
        round(np.median(BIGhumidity), 2), 
        round(np.std(BIGhumidity), 2))

    SML_TEMPHUM_PIN = 13
    print("Read SMLtemphum")
    SMLtemphum = [(0, 0)]#read_retry_multi(SENSOR_TYPE, SML_TEMPHUM_PIN, DHT_NUM_READS)        #def read_retry(sensor, pin, retries=15, delay_seconds=2, platform=None):
    #print(SMLtemphum)
    #print(SMLtemphum[0][0])
    #print(SMLtemphum[:][0])
    SMLtemperature = [temp * (9 / 5) + 32 for temp, humid in SMLtemphum]       #convert from Celcius to F
    SMLhumidity = [humid for temp, humid in SMLtemphum]
    #print(SMLtemperature)
    #print(SMLhumidity)
    print(round(np.mean(SMLtemperature), 2), 
        round(np.median(SMLtemperature), 2), 
        round(np.std(SMLtemperature), 2))
    print(round(np.mean(SMLhumidity), 2), 
        round(np.median(SMLhumidity), 2), 
        round(np.std(SMLhumidity), 2))


#    if BIGhumidity is not None and BIGtemperature is not None:
#        print('Temp={0:0.1f}*F  Humidity={1:0.1f}%'.format(BIGtemperature, BIGhumidity))
#    else:
#        print('Failed to get reading. Try again!')

    HX_NUM_READS = 15
    RETRY_ATTEMPTS = 7       #number of times to reread sensor to get normal StDev
    HX_STDEV_THRESHOLD = 2000
    BIG_DATA_PIN = 21
    BIG_CLOCK_PIN  = 20

    BIGdata_raw = read_scale(READINGS=HX_NUM_READS, DATAPIN=BIG_DATA_PIN, CLOCKPIN=BIG_CLOCK_PIN)        #Read big scale
    if np.std(BIGdata_raw) > HX_STDEV_THRESHOLD:
        for i in range(2, RETRY_ATTEMPTS+2):
            print("Scale StDev is too high (" + str(round(np.std(BIGdata_raw), 2)) + "), reading again...")
            BIGdata_raw1 = BIGdata_raw
            time.sleep(2)
            BIGdata_raw = read_scale(READINGS=HX_NUM_READS, DATAPIN=BIG_DATA_PIN, CLOCKPIN=BIG_CLOCK_PIN)        #Read big scale again
            if np.std(BIGdata_raw) > HX_STDEV_THRESHOLD:
                print("Scale StDev is still too high")
                if np.std(BIGdata_raw) < np.std(BIGdata_raw1):
                    BIGdata_raw = BIGdata_raw1
                else:
                    BIGdata_raw1 = BIGdata_raw
            else:
                print("Better reading recorded after " + str(i) + " tries")
                break
    else:
        print("StDev is below threshold of " + str(HX_STDEV_THRESHOLD))
    print(np.median(BIGdata_raw))
    print(round(np.std(BIGdata_raw), 2))
    BIGdata = 0.0002311996 * np.median(BIGdata_raw) + 7.4413911706      #convert raw to meaningful
    #print(round(np.median(BIGdata), 2))
    #BIGoffset = 0.0249121084 * np.median(BIGtemperature) - 2.4013925301        #temp calibration with slightly larger temp range but also more nosie
    BIGoffset = 0.0206347975 * np.median(BIGtemperature) - 2.0311528126     #temp calibration with smaller range but really good R^2
    #print(round(np.median(BIGoffset), 2))
    BIGdata = BIGdata + BIGoffset
    #print(round(np.median(BIGdata), 2))

    SML_DATA_PIN = 26
    SML_CLOCK_PIN = 19
    #print("Read Small Scale")
    SMLdata_raw = read_scale(READINGS=HX_NUM_READS, DATAPIN=SML_DATA_PIN, CLOCKPIN=SML_CLOCK_PIN)      #Read small scale
    if np.std(SMLdata_raw) > HX_STDEV_THRESHOLD:
        for i in range(2, RETRY_ATTEMPTS+2):
            print("Scale StDev is too high (" + str(round(np.std(SMLdata_raw), 2)) + "), reading again...")
            SMLdata_raw1 = SMLdata_raw
            time.sleep(2)
            SMLdata_raw = read_scale(READINGS=HX_NUM_READS, DATAPIN=SML_DATA_PIN, CLOCKPIN=SML_CLOCK_PIN)        #Read small scale again
            if np.std(SMLdata_raw) > HX_STDEV_THRESHOLD:
                print("Scale StDev is still too high")
                if np.std(SMLdata_raw) < np.std(SMLdata_raw1):
                    SMLdata_raw = SMLdata_raw1
                else:
                    SMLdata_raw1 = SMLdata_raw
            else:
                print("Better reading recorded after " + str(i) + " tries")
                break
    else:
        print("StDev is below threshold of " + str(HX_STDEV_THRESHOLD))
    print(np.median(SMLdata_raw))
    print(round(np.std(SMLdata_raw), 2))
    SMLdata = 0.0001398789 * np.median(SMLdata_raw) + 208.9558945667      #convert raw to meaningful
    print(round(np.median(SMLdata), 2))
    SMLoffset = -0.0033135985 * np.median(BIGtemperature) + 0.357458148      #temp calibration with fewer data points than big scale
    #print(round(np.median(SMLoffset), 2))
    SMLdata = SMLdata + SMLoffset
    #print(round(np.median(SMLdata), 2))

    COMMA = ','
    AllData = time.strftime("%Y-%m-%d-%H-%M-%S")+COMMA                 \
                    +str(round(np.median(BIGdata),2))+COMMA                \
                    +str(round(np.median(SMLdata),2))+COMMA                \
                    +str(round(np.median(BIGtemperature), 2))+COMMA        \
                    +str(round(np.median(BIGhumidity), 2))+COMMA           \
                    +str(round(np.median(SMLtemperature), 2))+COMMA        \
                    +str(round(np.median(SMLhumidity), 2))+COMMA           \
                    +str(WeatherData)+COMMA                                \
                    +str(np.median(BIGdata_raw))+COMMA                     \
                    +str(round(np.std(BIGdata_raw), 1))+COMMA              \
                    +str(np.median(SMLdata_raw))+COMMA                     \
                    +str(round(np.std(SMLdata_raw), 1))+"\n"        #add rawread

    #write_file(OUTPUTFILE, 'a', Headers)       #to update headers in the middle of the file
    write_file(OUTPUTFILE, 'a', AllData)
    # IFTTTmsg("WeightMonitor Success!")

except:
    IFTTTmsg("WeightMonitor Exception")
    logging.exception("WeightMonitor Exception")
    raise
    #print("Exception")

finally:
    GPIO.cleanup()