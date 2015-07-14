import skimage
import os.path
import json
import requests
import codecs
import math
import numpy
import skimage.measure

#only for debugging
import matplotlib.pyplot as plt

class InputDataError(Exception):
     def __init__(self, message,calling_context):
         self.message = message
         self.calling_context = calling_context
     def __str__(self):
         return repr('Errorneous data fed to '+self.calling_context+':'+self.message)


def curvesfinder(array,values):

	# call the function for single values for each value
	# assemble the featueres in a feature collection
	features = []
	for value in values:
		json_features = curvefinder(array,value)
		features += json_features
	
	feature_collection = {\
            'features': features,\
            'type': "FeatureCollection"}

	# print json.dumps(feature_collection,indent=1)
	return feature_collection

def curvefinder(array,level):
	
	time_mat = array['Travel time matrix']

	contours = skimage.measure.find_contours(time_mat,\
		level, \
		fully_connected='high', \
		positive_orientation='low')
		# connected=high => assume inner is fully connecter
		#orientation=low => contour winds CCW around lower-than-level value

	features = []
	for n,contour in enumerate(contours) :


		# longitudes
		longitudes_to_interpolate = contour[:,1]
		y_vec = array['Longitudes']
		x_vec = numpy.linspace(0,len(y_vec)-1,len(y_vec))
		longtitudes_interpolated = numpy.interp(longitudes_to_interpolate,x_vec,y_vec)
		
		# latitudes
		latitudes_to_interpolate = contour[:,0]
		y_vec = array['Latitudes']
		x_vec = numpy.linspace(0,len(y_vec)-1,len(y_vec))
		latitudes_interpolated = numpy.interp(latitudes_to_interpolate,x_vec,y_vec)

		coordinates = numpy.vstack((longtitudes_interpolated,latitudes_interpolated))
		
		geom = {'type': 'LineString','coordinates': numpy.transpose(coordinates).tolist()}
		props = {'Travel time [s]': level}
  		feature = {'type':'Feature','geometry':geom,'properties': props}
  		features.append(feature)
	return features

def read_array(filename):

	# check that its a proper file
	if not(os.path.isfile(filename)):
		raise InputDataError('read_array','File '+filename+'doesn\'t exist.')

	filename_prefix, filename_suffix = os.path.splitext(filename)
	accepted_file_endings=['.geojson', '.gjson', '.json']
	if not(filename_suffix in accepted_file_endings):
		raise InputDataError('read_array','Wrong file ending. Accepted are'+str(accepted_file_endings)+'. The file ending found was:'+filename_suffix)

	# check that the file is a geojson file
	with codecs.open(filename, encoding='utf-8', mode="r") as input_file:
		input_json = json.load(input_file)

	r = requests.post("http://geojsonlint.com/validate", data=json.dumps(input_json))

	if r.json()['status'] == 'error':
		if r.json()['message'] == 'Data was not JSON serializeable.':
			raise StandardError('Something went wrong.')
		else:
			error_message = r.json()['status']
			raise InputDataError('read_array','Data failed GeoJSON validation:'+error_message)

	# create long- and lat- and time- matrices
	features = input_json['features']
	number_of_features = len(features)

	n_float = math.sqrt(number_of_features)
	n = int(n_float)
	if not(n_float == n):
		raise InputDataError('read_array','The data was not a perfect square!')

	long_min = 180
	long_max = -180
	lat_min = 180
	lat_max = -180

	time_mat = numpy.empty(shape=(n,n))
	bajs = 1
	for feature in features:
		x_i = feature['properties']['Latitude index']
		y_i = feature['properties']['Longitude index']
		travel_time = feature['properties']['Biking time [s]']
		latitude = feature['geometry']['coordinates'][1]
		longitude = feature['geometry']['coordinates'][0]
		lat_max = max(latitude,lat_max)
		long_max = max(longitude,long_max)
		lat_min = min(latitude,lat_min)
		long_min = min(longitude,long_min)
		if travel_time == -1:
			travel_time = 999999
		time_mat[x_i,y_i] = travel_time

		

	
	long_list = numpy.linspace(long_min,long_max,n)
	lat_list = numpy.linspace(lat_min,lat_max,n)
	# return the matrices
	data = {\
		'Longitudes':long_list,\
		'Latitudes': lat_list,\
		'Travel time matrix': time_mat}
	return data

if __name__ == '__main__':
	
	n=43

	# call readarray on the relevant file
	data = read_array(\
		'bike_times_'+str(n)+'.geojson')
	# print data
	levels = [10, 15, 20, 25, 30, 35]
	levels[:] = [x*60 for x in levels] 

	# call the curvesfinder with relevant values
	level_set_geojson = curvesfinder(data,levels)

	with codecs.open('level_sets_'+str(n)+'.geojson', encoding='utf-8',mode='w') as output_file:
            json.dump(level_set_geojson,output_file,indent=1,encoding="utf-8",ensure_ascii=False)

	# print level_set_geojson