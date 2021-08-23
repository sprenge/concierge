from datetime import datetime
import os
import glob
import shutil 
import requests

def datetime2epoch(dt):
    utc_time = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
    epoch_time = (utc_time - datetime(1970, 1, 1)).total_seconds()
    return int(epoch_time)

disk_high = 0.85
disk_low = 0.79

def clean(cia, log, root_dir):
    stat = shutil.disk_usage('/root')
    disk_used = stat.used/stat.total
    url = "http://"+cia+':8000/rest/recordings'
    items_cleaned = 0
    print(disk_used, disk_low)
    while disk_used > disk_low:
        stat = shutil.disk_usage('/root')
        disk_used = stat.used/stat.total
        items_cleaned += 1

        # get all recording records
        db = []
        try:
            r = requests.get(url)
            if r.status_code == 200:
                for rec in r.json():
                    rec['recording_date_time'] = datetime2epoch(rec['recording_date_time'])
                    db.append(rec)
            else:
                log.error("error code not 200 {}".format(r.status_code))
        except Exception as e:
            log.error(str(e))
        
        # no record to remove, strange that we don't get the lower threshold
        if len(db) == 0:
            log.error("Cannot clean up recording resources enough, why ?")
            return

        sorted_db = sorted(db, key = lambda i: i['recording_date_time'])
        rec = sorted_db.pop(0)

        # file_path_video
        try:
            del_url = url+'/'+str(rec['id'])+'/'
            r = requests.delete(url+'/'+str(rec['id'])+'/')
            if r.status_code != 204:
                log.error("cannot delete recording id {}".format(rec['id']))
            else:
                log.debug("removed_recording id {}".format(rec['id']))
        except Exception as e:
            log.error(str(e))
        path, file_extension = os.path.splitext(rec['file_path_video'])
        jp = os.path.join('/root', path.strip('/')) + "*"
        file_list = glob.glob(jp)
        print("espr_file_list", jp, file_list)
        for fn in file_list:
            if os.path.exists(fn):
                log.debug("cleaned up file {}".format(fn))
                os.remove(fn)
            else:
                log.error("{} does not exist, hence cannot remove".format(fn))
        stat = shutil.disk_usage('/root')
        disk_used = stat.used/stat.total        
    if items_cleaned > 0:
        log.info("cleaned up below the threshold {}".format(disk_low))

class local_logger():
    def __init__(self):
        pass
    def error(self, msg):
        print(msg)
    def info(self, msg):
        print(msg)
    def debug(self, msg):
        print(msg)

if __name__ == "__main__":
    local_log = local_logger()
    clean("192.168.1.59", local_log, '/camera')