import os
import copy
import pandas as pd

fr = open("all_tz.txt", "r")
all_zones = fr.read().splitlines()
fr.close()
all_cities = []
for zone in all_zones:
    s = zone.split('/')
    if len(s)==2:
        city = s[1]
    if len(s)==3:
        city = s[2]
    city = city.replace("_", " ")
    all_cities.append(city)
    

copy_cities = copy.deepcopy(all_cities)
fn = "worldcities.csv"

df = pd.read_csv(fn)
list_world_cities = df.to_dict('records')
# lat, lng
cnt = 0
for rec in list_world_cities:
    city = rec['city_ascii']
    if city in all_cities:
        cnt += 1
        try:
            copy_cities.remove(city)
        except:
            print("{} already removed".format(city))

    city = rec['admin_name']
    if city in all_cities:
        cnt += 1
        try:
            copy_cities.remove(city)
        except:
            print("{} already removed".format(city))
print(cnt)
print(copy_cities)
