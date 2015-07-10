#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Imports 
import requests
import json
import codecs
import time

## Setup
n = 50
lat1 = 59.29
lat2 = 59.40
long1  = 17.96
long2  = 18.15
delta_lat = (lat2-lat1)/(n-1)
delta_long = (long2-long1)/(n-1)


## Defining exceptions for easier troubleshooting.
class APIError(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)


## Write file headers
with codecs.open("bike_times.tsv", encoding='utf-8', mode="w") as f:
    s = '\t'.join(['node_id','long','lat','travel time[s]','Address name used in travel time'])
    f.write(s)

f = open('bike_times.tsv','w')

tic = time.time()
for current_node_id in range(1,n*n+1):
    toc =  time.time() - tic
    i =  (current_node_id-1) % n
    j =  (current_node_id-1) // n
    print current_node_id,toc,i,j
    
    p1 = (lat1 +j*delta_lat,long1+i*delta_long)

    while True:
        get_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins=Acando, Malmskillnadsgatan, Stockholm&destinations='+str(p1[0])+','+str(p1[1])+'&mode=bicycling'
        r=requests.get(get_url)
        content = r.json()
        
        
        if content['status'] == 'OK':
            # print content
            # print '1'
            if content['rows'][0]['elements'][0]['status'] == 'OK':
                try:
                    bike_time_in_seconds = content['rows'][0]['elements'][0]['duration']['value']
                    final_address = content['destination_addresses'][0]
                    with codecs.open("bike_times.tsv", encoding='utf-8', mode="a") as f:
                        s = '\t'.join([ str(current_node_id),\
                            str(p1[0]), str(p1[1]), \
                            str(bike_time_in_seconds), final_address])+'\n'
                        f.write(s)
                except KeyError:
                    raise APIError('The JSON had a strange key-set. Result:\n'+content)
            elif content['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
                bike_time_in_seconds = 'N/A'
                final_address = 'N/A'
                with codecs.open("bike_times.tsv", encoding='utf-8', mode="a") as f:
                    s = '\t'.join([ str(current_node_id),\
                        str(p1[0]), str(p1[1]), \
                        str(bike_time_in_seconds), final_address])+'\n'
                    f.write(s)
            break
        elif content['status'] == 'OVER_QUERY_LIMIT':
            print 'made an over-query limit... retrying in 10 seconds'
            time.sleep(10)
            continue
        else:
            # print 'Unknown',content
            raise APIError('Unknown querey status. Result:\n'+content)
            # print '3'



