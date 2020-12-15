import os
import logging.config
import logging

# checks if the 'log' directory exists
try:
    os.mkdir("log")
except:
    print("")

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)


def errorLogger():
    return logging.getLogger('BarnabysBrewhouseLogs')


def eventLogger():
    return logging.getLogger('BarnabysBrewhouseEventsLog')