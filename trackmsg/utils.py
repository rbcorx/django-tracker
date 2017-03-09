import datetime
import time

from .models import DELIMITER_VERT, DELIMITER_COOR

def date_str_to_unix(date):
	"""converts date string to unix timestamp. format of str: YYYY-MM-DD"""
	return time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple())

def convert_points_to_str(points):
	"""converts points to a delimited concatenated string"""
	if not type(points[0]) == list:
		# single point only
		points = [points,]
	return DELIMITER_VERT.join(map(lambda x: DELIMITER_COOR.join(map(str, x)), points))

#TODO refactor

def universal_order(converter):
	"""order is the order of magnitutes of 10 the whole point space
	was multiplied to convert to integer without loosing float precision"""
	order = [0] # using list as wrapper to get access to mutable and outer non-global scope variables
	def converter_uni(points):
		order_zero, points = converter(points, order[0])
		order[0] = order_zero
		return points

	return converter_uni

@universal_order
def convert_points_to_int(points, order):
	"""converts list of tuple of x, y points from float to int without loosing
	precision by increasing the order of the space"""
	if len(points) <= 0:
		return points

	if not hasattr(points[0], "__iter__"):
		#if single point passed, convert it to a list of points
		points = [points,]
	order += 1
	return (order, points)

def test():
	#convert_points_to_int([1, 1])

	import matplotlib.path as mplPath
	import numpy as np

	poly = [190.1, 50.34, 500.545, 310.55]
	bbPath = mplPath.Path(np.array([[poly[0], poly[1]],
	                     [poly[1], poly[2]],
	                     [poly[2], poly[3]],
	                     [poly[3], poly[0]]]))

	print bbPath.contains_point((200.33, 100))

if __name__ == "__main__":
	test()