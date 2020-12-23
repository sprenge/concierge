import sys
import copy
import time
import requests

url_string = 'http://{}:{}/write?db={}'

def send_analytics_shape_data_to_influx(influx_host, camera, epoch, detected_shapes, shape_set, recording_id='', asset_type='image', video_metadata=None):
    '''
    Send detail
    '''
    url = url_string.format(influx_host, 8086, 'concierge')
    start_millis = int(epoch) * 1000
    
    measurement = "camera_shapes_detected_img"
    if asset_type == 'video':
        measurement = "camera_shapes_detected_video"
    shape_nbr = 0
    for shape_rec in detected_shapes:
        # istring = 'camera_shapes_detected,camera='+camera+" "
        istring = measurement+',shape='+shape_rec['shape']+" "
        if shape_rec['shape'] in shape_set:
            # istring += 'shape="{}",'.format(shape_rec['shape'])
            istring += 'confidence="{}",'.format(shape_rec['confidence'])
            istring += 'frame_nbr="{}",'.format(shape_rec['frame_nbr'])
            if 'snapshot' in shape_rec:
                istring += 'snapshot="{}",'.format(shape_rec['snapshot'])
            if 'snapshot_url' in shape_rec:
                istring += 'snapshot_url="{}",'.format(shape_rec['snapshot_url'])
            istring += 'camera="{}",'.format(camera)
            if recording_id:
                istring += 'recording_id="{}",'.format(recording_id)
            if shape_rec['box']:
                istring += 'startX="{}",'.format(shape_rec['box']['startX'])
                istring += 'startY="{}",'.format(shape_rec['box']['startY'])
                istring += 'endX="{}",'.format(shape_rec['box']['endX'])
                istring += 'endY="{}",'.format(shape_rec['box']['endY'])
            istring += 'epoch="{}"'.format(epoch)
            millis = start_millis
            if video_metadata:
                millis += int(int(shape_rec['frame_nbr'])/video_metadata['fps']*1000)

            istring += ' ' + str(millis) + '{0:06d}'.format(shape_nbr)
            shape_nbr += 1
            print("istring", istring)
            print("url", url)
            try:
                r = requests.post(url, data=istring, timeout=5)
            except Exception as e:
                print("influxdb post exception", str(e))


def summarize_analytic_data(data, recording_path, asset_type='image'):
    '''
    Transform data from shape detect to summary data in order to feed it influx db
    '''
    new_data = {'asset_type': asset_type, 'recording_path': recording_path}
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
