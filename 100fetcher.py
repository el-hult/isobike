import requests
import json

# the number of data points to look up. use 10*10 as max
nx = 10
ny = 10

lat1 = 59.29
lat2 = 59.40
long1  = 17.98
long2  = 18.15
delta_lat = (lat2-lat1)/(ny-1)
delta_long = (long2-long1)/(nx-1)

f = open('bike_times_100.tsv','w')

k =1
for i in range(0,nx):
    for j in range(0,ny):

        p1 = (lat1 +j*delta_lat,long1+i*delta_long)

        get_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins=Acando, Malmskillnadsgatan, Stockholm&destinations='+str(p1[0])+','+str(p1[1])+'&mode=bicycling'
        r=requests.get(get_url)
        content = r.json()
        
        try:
            bike_time_in_seconds = content['rows'][0]['elements'][0]['duration']['value']
        except KeyError:
            bike_time_in_seconds = 99999

        s = '\t'.join([ str(k), str(p1[0]), str(p1[1]), str(bike_time_in_seconds)])+'\n'
        f.write(s)
        k += 1

f.close()
