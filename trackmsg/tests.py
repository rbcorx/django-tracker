from datetime import timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from .models import *
from .utils import *
from .populate import *



class GeoFenceTest(TestCase):

	def setUp(self):
		vertices = [(1,1), (10, 1), (10, 10), (1, 10)] # square
		self.point_in = (2, 2)
		self.point_out = (1, 0)
		self.point_on = (2,1)
		self.point_vertex = (1, 1)
		self.geo_fence = GeoFence(vertices=vertices)

		super(GeoFenceTest, self).setUp()

	def test_geo_fence_point_conversion(self):
		vertices = TEST_VERTICES
		fence = GeoFence(vertices=vertices)
		vertex = (2, 1.5)
		self.assertEqual(fence.encloses(vertex), True)

	def test_encloses_yes(self):
		self.assertEqual(self.geo_fence.encloses(self.point_in), True)

	def test_ecloses_no(self):
		self.assertEqual(self.geo_fence.encloses(self.point_out), False)

	def test_encloses_no_on_line(self):
		self.assertEqual(self.geo_fence.encloses(self.point_on), False)

	def test_encloses_no_on_vertex(self):
		self.assertEqual(self.geo_fence.encloses(self.point_vertex), False)


class TrackerTest(TestCase):

	def setUp(self):
		# creating trackers
		create_activity()
		super(TrackerTest, self).setUp()

	def test_get_activity_def(self):
		trackers = Tracker.objects.all()

		self.assertEqual(all([t.message_set.all().count() == \
			t.get_activity(count=True) for t in trackers]), True)

	def test_get_activity_start_future(self):
		trackers = Tracker.objects.all()
		future = timezone.now() + timedelta(hours=6)

		self.assertEqual(all(map(lambda t: not len(t.get_activity(start=future)), trackers)), True)

	def test_get_activity_sane_start_end(self):
		trackers = Tracker.objects.all()
		start = timezone.now() + timedelta(days=-8)
		end = timezone.now()
		res = []
		for t in trackers:
			x = list(t.get_activity(start=start, order_by="timestamp"))
			y = list(t.message_set.all().filter(timestamp__lte=end, timestamp__gte=start).order_by("timestamp"))

			res.extend(map(lambda x: x[0] == x[1], zip(x, y)))
		
		self.assertEqual(all(res), True)

	def test_get_activity_alerts_only_all(self):
		trackers = Tracker.objects.all()
		res = []
		for t in trackers:
			x = list(t.get_activity(order_by="timestamp", alerts_only=True))
			y = list(t.message_set.all().filter(alerted=True).order_by("timestamp"))

			res.extend(map(lambda x: x[0] == x[1], zip(x, y)))
		
		self.assertEqual(all(res), True)

	def test_get_activity_alerts_only_sane_start_end(self):
		trackers = Tracker.objects.all()
		start = timezone.now() + timedelta(days=-8)
		end = timezone.now()
		res = []
		for t in trackers:
			x = list(t.get_activity(start=start, order_by="timestamp", alerts_only=True))
			y = list(t.message_set.all().filter(timestamp__lte=end, timestamp__gte=start, alerted=True).order_by("timestamp"))

			res.extend(map(lambda x: x[0] == x[1], zip(x, y)))
		
		self.assertEqual(all(res), True)

	def test_get_activity_geo_fences_none(self):
		trackers = Tracker.objects.all()
		geo_fences = []
		res = []
		for t in trackers:
			x = list(t.get_activity(order_by="timestamp", alerts_only=True, geo_fences=geo_fences))
			y = list(t.message_set.all().filter(alerted=True, geo_fence__in=geo_fences).order_by("timestamp"))

			res.extend(map(lambda x: x[0] == x[1], zip(x, y)))
		
		self.assertEqual(all(res), True)

	def test_get_activity_geo_fences_sane(self):
		trackers = Tracker.objects.all()
		geo_fences = GeoFence.objects.all()[:2]
		res = []
		for t in trackers:
			x = list(t.get_activity(order_by="timestamp", alerts_only=True, geo_fences=geo_fences))
			y = list(t.message_set.all().filter(alerted=True, geo_fence__in=geo_fences).order_by("timestamp"))

			res.extend(map(lambda x: x[0] == x[1], zip(x, y)))
		
		self.assertEqual(all(res), True)

	def test_get_activity_count_sane(self):
		trackers = Tracker.objects.all()
		geo_fences = GeoFence.objects.all()[:2]
		res = []
		for t in trackers:
			x = t.get_activity(order_by="timestamp", alerts_only=True, geo_fences=geo_fences, count=True)
			y = t.message_set.all().filter(alerted=True, geo_fence__in=geo_fences).count()

			res.append(x==y)
		
		self.assertEqual(all(res), True)


class MessageTest(TestCase):

	def setUp(self):
		create_activity()
		super(MessageTest, self).setUp()

	def test_process_enclosed_detected(self):
		messages = Message.objects.all()
		res = []
		for m in messages:
			coor = m.coordinate
			detected = any(map(lambda g: g.encloses(coor), m.tracker.geo_fences.all()))
			if detected:
				res.append(all([m.process(), detected]))
				res[len(res)-1] &= m.alerted
		self.assertEqual(all(res), True)

	def test_process_outside_undetected(self):
		messages = Message.objects.all()
		res = []
		for m in messages:
			coor = m.coordinate
			detected = any(map(lambda g: g.encloses(coor), m.tracker.geo_fences.all()))
			if not detected:
				res.append(all([m.process(), detected]))
				res[len(res)-1] &= m.alerted
		self.assertEqual(all(res), False)




