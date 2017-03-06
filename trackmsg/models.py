from __future__ import unicode_literals
import ast 

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


class ListField(models.TextField):
    __metaclass__ = models.SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value
        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

class GeoFence(models.Model):
	"""
	Model for geofence representing a polygon by the list of its vertices in clockwise order
	"""
	label = models.CharField(max_length=50, default="test-fence-tria")
	vertices = ListField(max_length=100, help_text="vertices of polygon")

	def __str__(self):
		return self.label
	
	def encloses(self, point):
		"""detects if the given vertex tuple falls within the fence
			ARGS:
				point: tuple representing point as x, y
		"""
		_polygon = mtpPath.Path(np.array(self.vertices))
		return _polygon.contains_point(point)



class Tracker(models.Model):
	"""
	Model for trackers created by the user to track passed messages
	"""
	user = models.ForeignKey(User, db_index=True)
	name = models.CharField(max_length=50, unique=True, help_text="tag name for tracker, \
		has to be unique and can only contain characters, underscores and numbers")
	created = models.DateTimeField(blank=True, editable=False, default=timezone.now)
	active = models.BooleanField(blank=True, default=False, help_text="Sets this tracker to active tracking")
	# TODO: Rename this to slug.
	url = models.SlugField(help_text="the url for this tracker will be /track/<url>", db_index=True, unique=True)
	geo_fences = models.ManyToManyField(GeoFence)

	active.boolean = True

	def __str__ (self):
		return self.name

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
			kwargs["geo_fence__in"] = geo_fences
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
	# TODO: Refactor coordinate to use Django serialization
	coordinate = ListField(max_length=100, help_text="coordinates of the message")
	alerted = models.BooleanField(default=False, blank=True)
	# TODO: 
	geo_fence = models.ForeignKey(GeoFence, null=True, blank=True)

	alerted.boolean = True

	def __str__ (self):
		return "{}: {}".format(self.tracker, self.coordinate)

	def process(self):
		"""process this message to raise alerts if any"""
		geo_fences = self.tracker.geo_fences.all()
		coord = self.coordinate

		for gf in geo_fences:
			if gf.encloses(coord):
				self.alerted = True
				self.geo_fence = gf
				self.save()
				return True
		return False













