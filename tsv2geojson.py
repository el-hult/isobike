#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import codecs
import os.path

class InputDataError(Exception):
     def __init__(self, value,calling_context):
         self.value = value
         self.calling_context = calling_context
     def __str__(self):
         return repr('Errorneous data fed to '+self.calling_context+':'+self.value)

def tsv2geojson(input_filename):

	if not(os.path.isfile(input_filename)):
		raise InputDataError('tsv2gjson','File doesn\'t esist.')

	input_filename_prefix, input_filename_suffix = os.path.splitext(input_filename)

	if input_filename_suffix != 'tsv':
		raise InputDataError('tsv2gjson','Wrong file ending.')
		
	output_filename = filename_prefix+'.geojson'


	with codecs.open(output_filename, encoding='utf-8',mode='w') as output_file:
		json_object = {};
		
		features = []
		with codecs.open(input_filename, encoding='utf-8',mode='r') as input_file:
			for line in input_file:
				parsing_array = line.split('\t')

				if parsing_array[3] == "N/A":
					biking_time = -1
				else:
					biking_time = int(parsing_array[3])

				next_geom = dict(type = 'Point', \
					coordinates=[float(parsing_array[2]),float(parsing_array[1])])
				next_props = {'Destination name': parsing_array[4].strip(), \
					'Biking time [s]':biking_time}

				feature = dict(type = 'Feature', \
					geometry = next_geom, \
					properties = next_props )

				features.append(feature)

		json_object = dict(features=features, \
			type="FeatureCollection")
		json.dump(json_object,output_file,indent=1,encoding="utf-8",ensure_ascii=False)
