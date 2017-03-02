from __future__ import unicode_literals

import matplotlib.path as mtpPath
import numpy as np

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from .apps import app_label

# global constants
DELIMITER_VERT = ':'
DELIMITER_COOR = ','

#TODO validators


class GeoFence(models.Model):
	"""
	Model for geofence representing a polygon by the list of its vertices in clockwise order
	#TODO add get_vertices method to model post processing just like datetime field
	"""
	label = models.CharField(max_length=50, default="test-fence-tria")
	vertices = models.CharField(max_length=300, 
		help_text="Concatenated list of vertices delimited by '{}' , coordinates of a \
			vertex are delimited by '{}'".format(DELIMITER_VERT, DELIMITER_COOR))

	def __str__(self):
		return self.label

	def set_vertices(self):
		"""sets self.vertices to the return value of get_vertices"""
		self.vertices = self.get_vertices()

	def get_vertices(self):
		"""returns list of vertices (x, y) decompresed and converted to float"""
		return list(map(lambda x: x.split(DELIMITER_COOR), self.vertices.split(DELIMITER_VERT)))

	get_vertices.short_description = "Vertices"
	
	def encloses(self, point):
		"""detects if the given vertex tuple falls within the fence
			ARGS:
				point: tuple representing point as x, y
		"""
		_polygon = mtpPath.Path(np.array(self.get_vertices()))
		return _polygon.contains_point(point)



class Tracker(models.Model):
	"""
	Model for trackers created by the user to track passed messages
	"""
	user = models.ForeignKey(User, db_index=True)
	tag = models.CharField(max_length=50, unique=True, help_text="tag name for tracker, \
		has to be unique and can only contain characters, underscores and numbers")
	created = models.DateTimeField(blank=True, editable=False, default=timezone.now)
	active = models.BooleanField(blank=True, default=False, help_text="Sets this tracker to active tracking")
	url = models.SlugField(help_text="the url for this tracker will be /track/<url>", db_index=True, unique=True)
	geo_fences = models.ManyToManyField(GeoFence)

	active.boolean = True

	def __str__ (self):
		return self.tag

	def get_activity(self, start=None, end=None, alerts_only=False, geo_fences=None, order_by=None, count=False):
		"""Returns list of messages within the given constraint
			Params:
				start (datetime)
				end (datetime)
				alerts_only (bool)
				geofences (list of GeoFence)
				order_by (string)
				count (bool)
		"""
		start = self.created if start is None else start
		end = timezone.now() if end is None else end
		order_by = "-timestamp" if order_by is None else order_by

		kwargs = {
			"timestamp__gte": start,
			"timestamp__lte": end,
		}

		if geo_fences:
			kwargs["geo_fences__in"] = geo_fences
		if alerts_only:
			kwargs["alerted"] = True

		_qset = self.message_set.filter(**kwargs).order_by(order_by)
		
		if count:
			return _qset.count()
		return _qset

	def get_total_messages(self):
		"""Returns total number of messages passed"""
		return self.get_activity(count=True)

	get_total_messages.short_description = "Activity"

	def get_total_alerts(self):
		"""Returns total number of alerts raised"""
		return self.get_activity(alerts_only=True, count=True)

	get_total_alerts.short_description = "Alerts"

class Message(models.Model):
	"""
	Model for messages passed to Tracker
	#TODO CHECK AND REFACTOR
		geofence processing should be carried our asynchronously and 

	#TODO add coordinate conversion to model post processing just like datetime field
	coordinate: (charfield) concatenated tuple of vertex (x, y) by COOR_DELIMITER
	
	#TODO send email to user
	"""
	tracker = models.ForeignKey(Tracker, db_index=True)
	timestamp = models.DateTimeField(blank=True, editable=False, default=timezone.now, db_index=True)
	coordinate = models.CharField(max_length=100, help_text="cocatenated tuple of coordinates delimited \
		by {}".format(DELIMITER_COOR))
	alerted = models.BooleanField(default=False, blank=True)
	geo_fence = models.ForeignKey(GeoFence, null=True, blank=True)

	alerted.boolean = True

	def __str__ (self):
		return "{}: {}".format(self.tracker, self.coordinate)

	def process(self):
		"""process this message to raise alerts if any"""
		geo_fences = self.tracker.geo_fences.all()
		coord = self.get_coordinates()

		for gf in geo_fences:
			if gf.encloses(coord):
				self.alerted = True
				self.geo_fence = gf
				self.save()
				return True
		return False

	def get_coordinates(self):
		"""Returns a coordinate tuple of floats as (x, y)"""
		return tuple(map(float, self.coordinate.split(DELIMITER_COOR)))

	get_coordinates.short_description = "Coordinates"













