import os
import sys
import random

def setup():
	"""Sets up django environment"""
	script_path = os.path.dirname(__file__)
	project_dir = os.path.abspath(os.path.join(script_path,'..'))
	sys.path.insert(0, project_dir)
	os.environ['DJANGO_SETTINGS_MODULE']='tracker.settings'

	import django
	django.setup()

# importing dependencies while making sure django is setup
try:
	from trackmsg.models import DELIMITER_VERT
except ImportError:
	setup()
finally:
	# importing local modules
	from trackmsg.models import *
	from trackmsg.utils import *

	#global constants
	TEST_VERTICES = ((1, 1), (10, 10), (20, 20), (20, 1),)
	TEST_VERTICES = list(map(lambda x: list(x), TEST_VERTICES))
	DEF_USER = User.objects.all()[0]


def clear():
	"""Clears all instances of Tracker, GeoFence, Message"""
	for t in Tracker.objects.all():
		t.delete()
	for f in GeoFence.objects.all():
		f.delete()
	for m in Message.objects.all():
		m.delete()


def create_fences(x=5):
	"""Creates 'x' geofence instances"""
	return [GeoFence.objects.create(vertices=TEST_VERTICES) for i in xrange(x)]


def create_trackers(x=5, clear_all=True):
	"""Creates 'x' trackers, clears all instances before creation if 'clear_all' is true"""
	if clear_all:
		clear()

	# default dummy data template
	_data = {
	'user': DEF_USER,
	'name': "name-{}",
	'url':"name-{}",
	}

	data = [dict(_data) for i in xrange(x)]

	# filling dummy data for each unique instance
	for i, _d in enumerate(data):
		_d['name'] = _d['name'].format(i)
		_d['url'] = _d['url'].format(i)

	geo_fences = create_fences()

	# creating trackers
	trackers = [Tracker.objects.create(**_d) for _d in data]

	# randomly assigning a single geofence to trackers
	for t in trackers:
		t.geo_fences.add(geo_fences[random.randint(0, len(geo_fences)-1)])

	return trackers

def create_activity(x=50, clear_all=True):
	"""Creates 'x' Messages, clears other instances if 'clear_all' is True"""
	if clear_all:
		clear()

	trackers = create_trackers(x=int(x/10), clear_all=False)

	# dummy data template
	_data = {
		"tracker": None,
		"coordinate": None,
	}

	data = [dict(_data) for i in xrange(x)]

	# randomly filling dummy data for each instance
	for i, _d in enumerate(data):
		_d['tracker'] = trackers[random.randint(0, len(trackers)-1)]
		_d['coordinate'] = [random.randint(1, 10), random.randint(1, 10)]

	# creating messages
	messages = [Message.objects.create(**_d) for _d in data]
	list(map(lambda x: x.process(), messages))

	return messages


def deploy():
	t = create_activity()
	print t


if __name__ == "__main__":
	deploy()