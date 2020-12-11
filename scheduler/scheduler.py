import os
import time
import sys
import logging
import schedule
from clean_recordings import clean

# setup logging
try:
    log_level = os.environ['LOG_LEVEL']
except:
    log_level = "DEBUG"
FORMAT = '%(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=getattr(logging, log_level))
log = logging.getLogger()

try:
    cia = os.environ['CONCIERGE_IP_ADDRESS']
except:
    cia = '127.0.0.1'
try:
    root_dir = os.environ['ROOT_DIR']
except:
    root_dir = ''

def recordings_cleaner():
    clean(cia, log)

schedule.every().hour.do(recordings_cleaner)

while True:
    schedule.run_pending()
    time.sleep(1)