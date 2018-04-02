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
    TODAY = time.strftime("%Y%m%d")
    INPUTFILENAME = "/home/pi/Documents/Code/" + str(TODAY) + "_WeightLog.csv"
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

        lastdatetime = datetime.datetime.strptime(lastdatetime, "%Y-%m-%d-%H-%M-%S")
        # print(lastdatetime, type(lastdatetime))
        CurrentTime = time.strftime("%Y-%m-%d-%H-%M-%S")
        # print(CurrentTime, type(CurrentTime))
        CurrentTime = datetime.datetime.strptime(CurrentTime, "%Y-%m-%d-%H-%M-%S")
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

    # print(lastdatetime)
    # lastdatetime_parts = lastdatetime.split('-')
    # lastdatetime_parts = list(map(int, lastdatetime_parts))
    # print(lastdatetime_parts)

    # CurrentTime = time.strftime("%Y-%m-%d-%H-%M-%S")
    # CurrentTime_parts = CurrentTime.split('-')
    # CurrentTime_parts = list(map(int, CurrentTime_parts))
    # print(CurrentTime_parts)

    # if lastdatetime_parts[0] == CurrentTime_parts[0]:
    #     print("Year Ok")
    #     if lastdatetime_parts[1] == CurrentTime_parts[1]:
    #         print("Month Ok")
    #         if lastdatetime_parts[2] == CurrentTime_parts[2]:
    #             print("Day Ok")
    #             if lastdatetime_parts[3] == CurrentTime_parts[3]:
    #                 print("Hour Ok")
    #                 if lastdatetime_parts[4] == CurrentTime_parts[4]:
    #                     print("Minute Ok")
    #                 else:
    #                     if (CurrentTime_parts[4] - lastdatetime_parts[4]) > UPDATETHRESHOLD:
    #                         print("Minute BAD")
    #                         IFTTTproblem = "WeightLog: Last reading +" + str(UPDATETHRESHOLD) + " min old"
    #                         IFTTTmsg(IFTTTproblem)
    #                         logger.info(IFTTTproblem)
    #                     else:
    #                         print("Acceptable Old Reading (<" + str(UPDATETHRESHOLD) + "min)")
    #             else:
    #                 if (CurrentTime_parts[3] - lastdatetime_parts[3]) > 1:
    #                     print("Hour BAD")
    #                     IFTTTproblem = "WeightLog: Last reading over an HOUR old"
    #                     IFTTTmsg(IFTTTproblem)
    #                     logger.info(IFTTTproblem)
    #                 else:
    #                     print("Acceptable Hour Old Reading???")
    #                     logger.info("Acceptable Hour Old Reading???")
    #         else:
    #             print("Day BAD")
    #             logger.info("Is the log over a day old?!!!!")
    #     else:
    #         print("Month BAD")
    # else:
    #     print("Year BAD")

    # IFTTTmsg("Log Updating Correctly")

    # if there is old data call the Weight monitor again

except:
    IFTTTmsg("UpdateCheck Exception")
    logging.exception("UpdateCheck Exception")
    raise
    # print("Exception")

finally:
    print("Done!")
