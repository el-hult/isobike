#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Imports 
import requests
import json
import codecs
import time

def fetch(n,origin,filename):

    lat1 = 59.29
    lat2 = 59.37
    long1  = 17.96
    long2  = 18.15
    delta_lat = (lat2-lat1)/(n-1)
    delta_long = (long2-long1)/(n-1)

    json_object = {};
    features = []

    for current_node_id in range(1,n*n+1):
        i =  (current_node_id-1) % n
        j =  (current_node_id-1) // n
        print 'i j n = ',i,j,current_node_id
        
        destination_lat  = lat1 +i*delta_lat
        destination_long = long1+j*delta_long

        while True:
            get_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'+\
                'origins='+origin+\
                '&destinations='+str(destination_lat)+','+str(destination_long)+\
                '&mode=bicycling'
            r=requests.get(get_url)
            content = r.json()
            
            
            if content['status'] == 'OK':

                if content['rows'][0]['elements'][0]['status'] == 'OK':
                    biking_time = content['rows'][0]['elements'][0]['duration']['value']
                    final_address = content['destination_addresses'][0]
                elif content['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
                    biking_time = -1
                    final_address = 'N/A'
                else:
                    raise ValueError('This element status is not handled. Result:\n'+content)

                geom = {\
                    'type': 'Point', \
                    'coordinates': [destination_long,\
                                    destination_lat]}
                props = {\
                    'Destination name': final_address, \
                    'Biking time [s]': biking_time,\
                    'Longitude index': j,\
                    'Latitude index': i}

                feature = dict(\
                    type = 'Feature', \
                    geometry = geom, \
                    properties = props )

                features.append(feature)
                break
                
            elif content['status'] == 'OVER_QUERY_LIMIT':
                print 'made an over-query limit... retrying in 10 seconds'
                time.sleep(10)
                continue

            else:
                raise ValueError('Unknown querey status. Result:\n'+content)

    json_object = {\
        'features': features,\
        'type': "FeatureCollection"}

    with codecs.open(filename+'.geojson', encoding='utf-8',mode='w') as output_file:
        json.dump(json_object,output_file,indent=1,encoding="utf-8",ensure_ascii=False)


## Setup

if __name__ == '__main__':
    n = 50
    fetch(n,\
        'Sergels torg, Norrmalm, Stockholm, Sverige',\
        'bike_times_'+str(n))
