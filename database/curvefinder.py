import skimage
import os.path
import json
import requests
import codecs
import math
import numpy
import scipy.interpolate
import skimage.measure

#only for debugging
import matplotlib.pyplot as plt

class InputDataError(Exception):
     def __init__(self, message,calling_context):
         self.message = message
         self.calling_context = calling_context
     def __str__(self):
         return repr('Errorneous data fed to '+self.calling_context+':'+self.message)

def eliminate_nans(array):

	# check input
	n,ny = array.shape
	if n != ny:
		raise ValueError('Not square array!')

	# reshape the data for griddata
	nan_filter = numpy.isnan(array)
	not_nan = array[~nan_filter]
	x_mat = numpy.tile(numpy.array(range(0,n)),[n,1])
	y_mat = numpy.transpose(x_mat)
	
	xpoints = x_mat[~nan_filter]
	ypoints = y_mat[~nan_filter]

	# create the interpolant
	points = (xpoints, ypoints)

	values = not_nan
	out_xpoints = range(0,n)
	out_ypoints = range(0,n)
	grid_x, grid_y = numpy.mgrid[0:n:1, 0:n:1]
	xi = (grid_x, grid_y)
	array_without_nan = \
		scipy.interpolate.griddata(points, values, xi,\
		 method='linear', fill_value=numpy.nan, rescale=False)
	return array_without_nan

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
	
	time_mat_with_nans = array['Travel time matrix']

	## replace nans with mean of neightbours
	time_mat = eliminate_nans(time_mat_with_nans)



	contours = skimage.measure.find_contours(time_mat,\
		level, \
		fully_connected='low', \
		positive_orientation='low')
		# connected=high => assume inner is fully connecter
		#orientation=low => contour winds CCW around lower-than-level value

	features = []
	for n,contour in enumerate(contours) :

		# longitudes
		long_int_range = numpy.arange(len(array['Longitudes']))
		longitudes_to_interpolate = contour[:,1]
		longitudes_interpolated = numpy.interp(longitudes_to_interpolate,long_int_range,array['Longitudes'])
		
		# latitudes
		lat_int_range = numpy.arange(len(array['Latitudes']))
		latitudes_to_interpolate = contour[:,0]
		latitudes_interpolated = numpy.interp(latitudes_to_interpolate,lat_int_range,array['Latitudes'])

		coordinates = numpy.vstack((longitudes_interpolated,latitudes_interpolated))
		coordinates = numpy.transpose(coordinates).tolist()

		# check if it bites its tail!
		if coordinates[0] == coordinates[-1]:
			feature_type = 'Polygon'
			coordinates_bundle = [ coordinates ] # polygons need extra 'wrapping'
		else:
			feature_type = 'LineString'
			coordinates_bundle = coordinates

		geom = {'type': feature_type,'coordinates': coordinates_bundle}
		props = {'Biking time [s]': level}
  		feature = {'type':'Feature','geometry':geom,'properties': props}
  		features.append(feature)
	return features

def read_array(filename):

	# check that its a proper file
	if not(os.path.isfile(filename)):
		raise InputDataError('read_array','File '+filename+'doesn\'t exist.')

	# check the file ending
	filename_prefix, filename_suffix = os.path.splitext(filename)
	accepted_file_endings=['.geojson', '.gjson', '.json']
	if not(filename_suffix in accepted_file_endings):
		raise InputDataError('read_array','Wrong file ending. Accepted are'+str(accepted_file_endings)+'. The file ending found was:'+filename_suffix)

	# check that the file is a geojson file
	with codecs.open(filename, encoding='utf-8', mode="r") as input_file:
		input_json = json.load(input_file)

	# validate the GeoJSON
	r = requests.post("http://geojsonlint.com/validate", data=json.dumps(input_json))
	if r.json()['status'] == 'error':
		if r.json()['message'] == 'Data was not JSON serializeable.':
			raise StandardError('Something went wrong.')
		else:
			error_message = r.json()['status']
			raise InputDataError('read_array','Data failed GeoJSON validation:'+error_message)

	# validate the number of data points and allocate some space
	features = input_json['features']
	n_float = math.sqrt(len(features))
	n = int(n_float)
	if not(n_float == n):
		raise InputDataError('read_array','The data was not a perfect square!')
	long_min = lat_min = 180
	long_max = lat_max = -180
	time_mat = numpy.empty(shape=(n,n))



	for feature in features:

		y_i = feature['properties']['Latitude index']
		x_i = feature['properties']['Longitude index']
		travel_time = feature['properties']['Biking time [s]']
		latitude = feature['geometry']['coordinates'][1]
		longitude = feature['geometry']['coordinates'][0]

		lat_max = max(latitude,lat_max)
		long_max = max(longitude,long_max)
		lat_min = min(latitude,lat_min)
		long_min = min(longitude,long_min)

		if travel_time == -1:
			travel_time = numpy.nan

		time_mat[x_i,y_i] = travel_time

		

	# return the matrices
	
	long_list = numpy.linspace(long_min,long_max,n)
	lat_list = numpy.linspace(lat_min,lat_max,n)
	data = {\
		'Longitudes':long_list,\
		'Latitudes': lat_list,\
		'Travel time matrix': time_mat}
	return data

if __name__ == '__main__':
	
	n=50

	# call readarray on the relevant file
	data = read_array(\
		'bike_times_'+str(n)+'.geojson')
	
	# call the curvesfinder with relevant values
	levels = [5*60, 10*60, 15*60, 20*60, 25*60, 30*60]
	level_set_geojson = curvesfinder(data,levels)

	with codecs.open('level_sets_'+str(n)+'.geojson', encoding='utf-8',mode='w') as output_file:
            json.dump(level_set_geojson,output_file,indent=1,encoding="utf-8",ensure_ascii=False)

	# print level_set_geojson