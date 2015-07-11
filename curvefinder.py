import skimage


def curvesfinder(array,values):
	call the function for single values for each value
	assemble the featueres in a feature collection

def curvefinder(array,value):
	check that the value is indeed a float
	call the find contours function
	format the output as a geojson feature 

def read_array(filename):
	check that its a file
	check that the file is a geojson file
	create long- and lat- and time- matrices
	return the matrices

if __name__ == '__main__':
	
	call readarray on the relevant file
	call the curvesfinder with relevant values