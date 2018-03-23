#!/usr/bin/python3

# UpdateCheck.py

import pandas as pn
import subprocess
import datetime
import time
import os.path
import logging
from weightfunctions import read_scale, write_file, get_weather, IFTTTmsg, calculate, check_web_response

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
        # TODAY = time.strftime("%Y%m%d")
        # OUTPUTFILE = "/home/pi/Documents/Code/" + str(TODAY) + "_WeightLog.csv"
        print("File does not exist")
        IFTTTmsg("NO LOG FILE FOR TODAY")
    with open(INPUTFILENAME, 'r') as file:       # recommended way to open files to ensure the file closes properly
        filecontents = pn.read_csv(INPUTFILENAME, delimiter=',')     # nrows=5
    # print(filecontents)
    # print(filecontents['DateTime'][-1])
    # print(filecontents['DateTime'][0])

#    add print(filecontents.value_count())

    for row in filecontents["DateTime"]:        # this is inefficient but works
        # print(row)
        lastdatetime = row

    # print(lastdatetime)
    lastdatetime_parts = lastdatetime.split('-')
    lastdatetime_parts = list(map(int, lastdatetime_parts))
    print(lastdatetime_parts)

    CurrentTime = time.strftime("%Y-%m-%d-%H-%M-%S")
    CurrentTime_parts = CurrentTime.split('-')
    CurrentTime_parts = list(map(int, CurrentTime_parts))
    print(CurrentTime_parts)

    if lastdatetime_parts[0] == CurrentTime_parts[0]:
        print("Year Ok")
        if lastdatetime_parts[1] == CurrentTime_parts[1]:
            print("Month Ok")
            if lastdatetime_parts[2] == CurrentTime_parts[2]:
                print("Day Ok")
                if lastdatetime_parts[3] == CurrentTime_parts[3]:
                    print("Hour Ok")
                    if lastdatetime_parts[4] == CurrentTime_parts[4]:
                        print("Minute Ok")
                    else:
                        if (CurrentTime_parts[4] - lastdatetime_parts[4]) > UPDATETHRESHOLD:
                            print("Minute BAD")
                            IFTTTproblem = "WeightLog: Last reading +" + str(UPDATETHRESHOLD) + " min old"
                            IFTTTmsg(IFTTTproblem)
                            logger.info(IFTTTproblem)
                        else:
                            print("Acceptable Old Reading (<" + str(UPDATETHRESHOLD) + "min)")
                else:
                    if (CurrentTime_parts[3] - lastdatetime_parts[3]) > 1:
                        print("Hour BAD")
                        IFTTTproblem = "WeightLog: Last reading over an HOUR old"
                        IFTTTmsg(IFTTTproblem)
                        logger.info(IFTTTproblem)
                    else:
                        print("Acceptable Hour Old Reading???")
                        logger.info("Acceptable Hour Old Reading???")
            else:
                print("Day BAD")
                logger.info("Is the log over a day old?!!!!")
        else:
            print("Month BAD")
    else:
        print("Year BAD")

    # IFTTTmsg("Log Updating Correctly")

    # if there is old data call the Weight monitor again

except:
    IFTTTmsg("UpdateCheck Exception")
    logging.exception("UpdateCheck Exception")
    raise
    # print("Exception")

finally:
    print("Done!")
