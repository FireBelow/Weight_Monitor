#!/usr/bin/python3

# UpdateCheck.py

import pandas as pn
import subprocess
import datetime
import time
import os.path
import logging
from weightfunctions import read_scale, write_file, get_weather, IFTTTmsg, calculate, check_web_response

# TODO:
# UpdateCheck should also check Running Log

try:
    logger = logging.getLogger("WeightMonitor.UpdateCheck.add")
    logger.info("Checking if data is Current and Updating")

    UPDATETHRESHOLD = 20
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
    INPUTFILENAME = "/home/pi/Documents/Code/" + TODAY.strftime(FILE_DATE_FORMAT) + "_WeightLog.csv"
    try:
        open(INPUTFILENAME, 'r')
        print("File exists")
    except:
        print("File does not exist")
        IFTTTmsg("NO LOG FILE FOR TODAY")
    with open(INPUTFILENAME, 'r') as file:       # recommended way to open files to ensure the file closes properly
        filecontents = pn.read_csv(INPUTFILENAME, delimiter=',')     # nrows=5
    # print(filecontents)

    # add print(filecontents.value_count())

    if filecontents["DateTime"].count() > 0:
        lastdatetime = filecontents["DateTime"].iloc[-1]
        # print(lastdatetime, type(lastdatetime))

        lastdatetime = datetime.datetime.strptime(lastdatetime, ISO_DATETIME_FORMAT)
        # print(lastdatetime, type(lastdatetime))
        CurrentTime = time.strftime(ISO_DATETIME_FORMAT)
        # print(CurrentTime, type(CurrentTime))
        CurrentTime = datetime.datetime.strptime(CurrentTime, ISO_DATETIME_FORMAT)
        # print(CurrentTime, type(CurrentTime))
        current_update_time_delta = CurrentTime - lastdatetime
        # print(current_update_time_delta, type(current_update_time_delta))
        update_time_delta_threshold = datetime.timedelta(minutes=UPDATETHRESHOLD)
        # print(update_time_delta_threshold, type(update_time_delta_threshold))
        if current_update_time_delta < update_time_delta_threshold:
            problem_msg = str(current_update_time_delta) + " min since last reading"
            print(problem_msg)
            # IFTTTmsg(problem_msg)
            # logger.info(problem_msg)
        else:
            problem_msg = "OLD DATA: " + str(current_update_time_delta) + " min since last reading (>20min)"
            print(problem_msg)
            IFTTTmsg(problem_msg)
            logger.info(problem_msg)
    else:
        problem_msg = "***EMPTY LOG FILE***"
        print(problem_msg)
        IFTTTmsg(problem_msg)
        logger.info(problem_msg)

    # IFTTTmsg("Log Updating Correctly")

    # if there is old data call the Weight monitor again

except:
    IFTTTmsg("UpdateCheck Exception")
    logging.exception("UpdateCheck Exception")
    raise
    # print("Exception")

finally:
    print("Done!")
