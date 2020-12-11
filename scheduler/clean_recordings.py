from datetime import datetime
import os
import shutil 
import requests

def datetime2epoch(dt):
    utc_time = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
    epoch_time = (utc_time - datetime(1970, 1, 1)).total_seconds()
    return int(epoch_time)

disk_high = 0.85
disk_low = 0.8

def clean(cia, log):
    stat = shutil.disk_usage('/root')
    disk_used = stat.used/stat.total
    url = "http://"+cia+'/rest/recordings'
    items_cleaned = 0
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
        print("sorted_db", sorted_db)
        rec = sorted_db.pop(0)

        # file_path_video
        try:
            del_url = url+'/'+str(rec['id'])+'/'
            print("del_url", del_url)
            r = requests.delete(url+'/'+str(rec['id'])+'/')
            if r.status_code != 204:
                log.error("cannot delete recording id {}".format(rec['id']))
        except Exception as e:
            log.error(str(e))
        path, file_extension = os.path.splitext(rec['file_path_video'])
        exts = ['.jpg', '.gif', '.mp4']
        for ext in exts:
            fn = "/root"+path+ext
            print("fn", fn)
            if os.path.exists(fn):
                os.remove(fn)
            else:
                log.error("{} does not exist, hence cannot remove".format(fn))
        stat = shutil.disk_usage('/root')
        disk_used = stat.used/stat.total        
    if items_cleaned > 0:
        log.info("cleaned up below the threshold {}".format(disk_low))
    
