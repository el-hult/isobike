from skimage import data, io, filter


def curvefinder(array):
	print 'lol'


if __name__ == '__main__':
	image = data.coins() # or any NumPy array!
	edges = filter.sobel(image)
	io.imshow(edges)
	io.show()