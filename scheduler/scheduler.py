import os
import time
import sys
import logging
import schedule
from clean_recordings import clean
import requests

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

def create_deep_data():
    url = "http://"+cia+":8000/rest/known_objects/"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            for rec in r.json():
                print("rec", rec)
                if not rec['deep_learning_done']:
                    if rec['object_type'] == 16:
                        url = "http://"+cia+":5106/deep_analysis/api/v1.0/create_deep_data"
                        data = {"record_id": rec['id']}
                        r = requests.post(url, json=data, timeout=120)

    except Exception as e:
        log.error(str(e))

def recordings_cleaner():
    clean(cia, log)

schedule.every().hour.do(recordings_cleaner)
schedule.every().minute.do(create_deep_data)

while True:
    schedule.run_pending()
    time.sleep(1)
