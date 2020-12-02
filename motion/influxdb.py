import sys
import copy
import time
import requests

url_string = 'http://{}:{}/write?db={}'

def summarize_analytic_data(data, recording_path, asset_type='image', motion=False):
    '''
    Transform data from shape detect to summary data in order to feed it influx db
    '''
    new_data = {'asset_type': asset_type, 'recording_path': recording_path}
    if motion:
        new_data['detect_motion'] = 1
    nbr_rec = 0
    for rec in data:
        if 'shape' in rec:
            key_name = "detect_"+rec['shape']
            if key_name not in new_data:
                new_data[key_name] = 1
            else:
                new_data[key_name] += 1
        if 'faces' in rec:
            for face in rec['faces']:
                if 'detect_face' not in new_data:
                    new_data['detect_face'] = 1
                else:
                    new_data['detect_face'] += 1
        nbr_rec += 1
    if nbr_rec == 0 and not motion: 
        return {}
    return new_data


def send_recording_to_influx_db(host, camera, kv_data, epoch, user=None, password=None):
    url = url_string.format(host, 8086, 'concierge')
    millis = epoch * 1000
    current_time = str(millis) + '000000'
    istring = 'camera_analytics,camera='+camera+" "
    for akey in kv_data:
        if isinstance(kv_data[akey], str):
            istring += '{}="{}",'.format(akey, kv_data[akey])
        else:
            istring += '{}={},'.format(akey, kv_data[akey])
    istring = istring[:-1]
    istring += ' ' + current_time
    try:
        r = requests.post(url, data=istring, timeout=5)
        print(r)
    except Exception as e:
        print("influxdb post exception", str(e))

if __name__ == '__main__':
    kv_data = {"detect_person": 10, "recording_path": "name_recording3"}
    send_recording_to_influx_db('192.168.1.59', "CameraLisa", kv_data, int(time.time()))