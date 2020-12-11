import influxdb

cia = '192.168.1.59'
client = influxdb.InfluxDBClient(host=cia, port=8086)
client.switch_database('concierge')
rid = 1000
query = "select * FROM camera_shapes_detected_video WHERE \"recording_id\"='{}'".format(rid)
results = client.query(query)
print(query)
columns = results.raw['series'][0]['columns']
tt = {}
for i, name in enumerate(columns):
    tt[i] = name
recording_shape_list = []
for rec in results.raw['series'][0]['values']:
    adict = {}
    for i, aval in enumerate(rec):
        adict[tt[i]] = aval
    recording_shape_list.append(adict)
for rec in recording_shape_list:
    print(rec)
