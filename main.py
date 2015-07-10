#!/usr/bin/env python
# -*- coding: utf-8 -*-


from tsv2geojson import *
import codecs

tsv2geojson('bike_times.tsv')

# with codecs.open('bike_times.geojson',mode='r',encoding='utf-8') as f:
	# for i in range(0,30):
	# 	print f.readline()