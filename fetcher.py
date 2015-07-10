#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Imports 
import requests
import json
import codecs
import time

## Defining exceptions for easier troubleshooting.
class APIError(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)


def fetch(n,origin,filename,format):

    lat1 = 59.29
    lat2 = 59.40
    long1  = 17.96
    long2  = 18.15
    delta_lat = (lat2-lat1)/(n-1)
    delta_long = (long2-long1)/(n-1)

    if format == 'tsv':

        with codecs.open(filename+'.tsv', encoding='utf-8', mode="w") as output_file:
            header = '\t'.join(['node_id','long','lat','travel time[s]','Address name used in travel time'])
            output_file.write(header)

        for current_node_id in range(1,n*n+1):
            i =  (current_node_id-1) % n
            j =  (current_node_id-1) // n
            
            destination_coordinates = (lat1 +j*delta_lat,long1+i*delta_long)

            while True:
                get_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins='+origin+'&destinations='+str(destination_coordinates[0])+','+str(destination_coordinates[1])+'&mode=bicycling'
                r=requests.get(get_url)
                content = r.json()
                
                
                if content['status'] == 'OK':

                    if content['rows'][0]['elements'][0]['status'] == 'OK':
                        try:
                            bike_time_in_seconds = content['rows'][0]['elements'][0]['duration']['value']
                            final_address = content['destination_addresses'][0]
                            with codecs.open(filename+'.tsv', encoding='utf-8', mode="a") as output_file:
                                s = '\t'.join([ str(current_node_id),\
                                    str(destination_coordinates[0]), str(destination_coordinates[1]), \
                                    str(bike_time_in_seconds), final_address])+'\n'
                                output_file.write(s)
                        except KeyError:
                            raise APIError('The JSON had a strange key-set. Result:\n'+content)


                    elif content['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
                        bike_time_in_seconds = 'N/A'
                        final_address = 'N/A'
                        with codecs.open(filename+'.tsv', encoding='utf-8', mode="a") as output_file:
                            s = '\t'.join([ str(current_node_id),\
                                str(destination_coordinates[0]), str(destination_coordinates[1]), \
                                str(bike_time_in_seconds), final_address])+'\n'
                            output_file.write(s)
                    break

                elif content['status'] == 'OVER_QUERY_LIMIT':
                    print 'made an over-query limit... retrying in 10 seconds'
                    time.sleep(10)
                    continue

                else:
                    raise APIError('Unknown querey status. Result:\n'+content)

    elif format == 'geojson':
        json_object = {};
        features = []

        for current_node_id in range(1,n*n+1):
            i =  (current_node_id-1) % n
            j =  (current_node_id-1) // n
            print 'i j n = 'i,j,n
            
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
                        raise NotImplementedError('This element status is not handled. Result:\n'+content)

                    geom = {\
                        'type': 'Point', \
                        'coordinates': [destination_lat,\
                                        destination_long]}
                    props = {\
                        'Destination name': final_address, \
                        'Biking time [s]': biking_time,\
                        'Longitude index': i,\
                        'Latitude index': j}

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
                    raise APIError('Unknown querey status. Result:\n'+content)

        json_object = {\
            'features': features,\
            'type': "FeatureCollection"}

        with codecs.open(filename+'.geojson', encoding='utf-8',mode='w') as output_file:
            json.dump(json_object,output_file,indent=1,encoding="utf-8",ensure_ascii=False)

    else:
        raise SyntaxError('The only allowed formats are tsv and geojson!')


## Setup
n = 3
fetch(n,'Acando, Malmskillnadsgatan, Stockholm','bike_times','geojson')