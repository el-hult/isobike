import requests
import json

# the number of data points to look up. use 10*10 as max
nx = 10
ny = 10

long1 = 59.26
long2 = 59.40
lat1  = 17.94
lat2  = 18.03
delta_long = (long2-long1)/(nx-1)
delta_lat = (lat2-lat1)/(ny-1)

f = open('bike_times_100.tsv','w')

k =1
for i in range(0,nx):
    for j in range(0,ny):

        p1 = (long1+i*delta_long,lat1 +j*delta_lat)

        get_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins=Acando, Malmskillnadsgatan, Stockholm&destinations='+str(p1[0])+','+str(p1[1])
        r=requests.get(get_url)
        content = r.json()
        bike_time_in_seconds = content['rows'][0]['elements'][0]['duration']['value']
        #print content['rows'][0]['elements'][0]['distance']['value']


        s = '\t'.join([ str(k), str(p1[0]), str(p1[1]), str(bike_time_in_seconds)])+'\n'
        f.write(s)
        k += 1

f.close()
