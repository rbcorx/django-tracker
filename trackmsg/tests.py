from django.test import TestCase
from django.contrib.auth.models import User

from .models import *
from .utils import *
from .populate import *


class UtilTest(TestCase):

	def test_points_to_str(self):
		points = TEST_VERTICES
		self.assertEqual(convert_points_to_str(points), TEST_VERTICES_STR)

class GeoFenceTest(TestCase):

	def test_geo_fence_point_conversion(self):
		vertices = TEST_VERTICES_STR
		fence = GeoFence(vertices=vertices)
		vertex = (2, 1.5)
		self.assertEqual(fence.encloses(vertex), True)

	#def test_geo_fence


class TrackerTest(TestCase):

	def setUp(self):
		# creating trackers
		create_activity()
		super(TrackerTest, self).setUp()

	def test_get_activity_def(self):
		trackers = Tracker.objects.all()

		self.assertEqual(all([t.message_set.all().count() == \
			t.get_activity(count=True) for t in trackers]), True)
