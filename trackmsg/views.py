import json

import time
import datetime
import itertools

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views import generic
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.db.models import Sum, Count
from django.utils import timezone

#from .populate import DEF_USER as DU
from .models import Tracker, Message, GeoFence, DELIMITER_COOR
from .forms import TrackerForm, UserForm
from .tasks import notify
from .utils import date_str_to_unix

#TODO login_required to views

# TODO renamve views append view, remove form
# TODO restructure file to directory package


##### LOGIN VIEWS #####


"""
Register
login
logout
"""

class RegisterView(generic.View):
	def get(self, request, *args, **kwargs):
		context = {"form":UserForm(),}
		return render(request, "registration/register.html", context)

	def post(self, request, *args, **kwargs):
		form = UserForm(request.POST)
		if form.is_valid():
			user = form.save()
			return HttpResponseRedirect(reverse("login"))
		context = {"form":form,}
		return render(request, "registration/register.html", context)


#######################



class TrackerList(LoginRequiredMixin, generic.ListView):
	template = "trackmsg/tracker_list.html"
	context_object_name = "trackers"

	def get_queryset(self):
		#TODO change user to logged in
		return Tracker.objects.filter(user=self.request.user).order_by("-created")


class TrackerDetail(LoginRequiredMixin, generic.DetailView):
	model = Tracker
	template = "trackmsg/tracker_detail.html"


class TrackerFormView(LoginRequiredMixin, generic.View):

	def get(self, request, *args, **kwargs):
		context = {}
		if "pk" in kwargs:
			# creating edit form for Tracker:pk
				context["form"] = TrackerForm(instance=get_object_or_404(Tracker, pk=kwargs["pk"]))
				context["pk"] = kwargs["pk"]
		else:
			# creating fresh form
			context["form"] = TrackerForm()
		return render(request, 'trackmsg/tracker_form.html', context)


	def post(self, request, *args, **kwargs):
		context = {}
		create = False
		if "pk" in kwargs:
			# editing Tracker:pk
				form = TrackerForm(request.POST, instance=get_object_or_404(Tracker, pk=kwargs["pk"]))
		else:
			# creating new tracker
			form = TrackerForm(request.POST)
			create = True
		if form.is_valid():
			tracker = form.save(commit=False)
			#TODO patch allow owner only edit
			if create:
				tracker.user = request.user

			tracker.save()

			# BUG: geo_fences list not rendering properly
			if "geo_fences" in request.POST:
				# fetching selected geofence instances
				geo_fences = list(map(lambda x: get_object_or_404(GeoFence, pk=int(x)), request.POST.getlist("geo_fences")))

			for gf in geo_fences:
				tracker.geo_fences.add(gf)
			# END

			return HttpResponseRedirect(reverse("trackmsg:list"))
		else:
			context["form"] = form
		return render(request, 'trackmsg/tracker_form.html', context)



class MessagePush(generic.View):
	http_method_names = ['options', 'trace', 'post']

	def post(self, request, *args, **kwargs):
		#TODO refactor this, make separate model function to fetch point
		data = json.loads(request.body)
		res = {}
		status = None
		try:
			x = float(data["x"])
			y = float(data["y"])
			point = [str(x), str(y)]

			point = DELIMITER_COOR.join(point)

			slug = kwargs["slug"]
			try:
				print [t.url for t in Tracker.objects.all()]
				tracker = Tracker.objects.get(url=slug)

				if not tracker.active:
					res["errors"] = "tracker is inactive!"
					status=400
			except Tracker.DoesNotExist:
				print slug
				res["errors"] = "Unidentified Slug!"
				status=404
		except:
			res["errors"] = "Incorrectly formed data!"
			status=400

		if not status:
			_m = Message(tracker=tracker, coordinate=point)

			alerted = _m.process()
			if not alerted:
				try:
					_m.save()
					res["message"] = "success! message stored!"
					status = 201
				except:
					res["errors"] = "Couldn't save message!"
					status=400
			else:
				fences = list(map(lambda pk: GeoFence.objects.get(pk=pk).label, _m.geo_fence)) \
							if type(_m.geo_fence) == list else GeoFence.objects.get(pk=_m.geo_fence).label
				notify.delay(request.user.pk, 'Your awesome tracker has detected coordinates: ' + \
				 '{} in geo-fence(s) {}.'.format(_m.coordinate, fences))
				#self.notify_user(request.user, _m)
				res["message"] = "success! message stored and alerted!"
				status = 201

		return JsonResponse(res, status=status)



def test(request):
	"""Testing curves views"""
	return render(request, "trackmsg/curves.html", {})

def get_data(request, pk):
	truncate_date = connection.ops.date_trunc_sql('day', 'timestamp')
	qs = Message.objects.filter(tracker=get_object_or_404(Tracker, pk=pk)).extra({'day':truncate_date})
	report = qs.values('day', 'alerted').annotate(Count('pk')).order_by('day')

	alerts = map(lambda el: [el['day'], el['pk__count']], filter(lambda r: r['alerted'], report))
	activity = map(lambda x: [x[0], reduce(lambda x, y: x + y["pk__count"], x[1], 0)],
		itertools.groupby(report, key=lambda x: x['day']))

	# putting filler data of tracker had zero activity
	if not len(activity):
		activity = [[timezone.now().strftime("%Y-%m-%d"), 0]]
		per_alerts = 0
	else:
		# TODO optimize list traversals
		per_alerts = reduce(lambda x, y: x + y[1], alerts, 0) * 100 / float(reduce(lambda x, y: x + y[1], activity, 0))


	start = activity[0][0]
	end = activity[-1][0]

	# if data for only one date is available, adding previous date as filler
	if start == end:
		prev = (datetime.datetime.strptime(start, "%Y-%m-%d") + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
		activity.insert(0, [prev, 0])

	# normalizing alerts for missing data
	alerts_filled = []
	ii = 0
	for a in activity:
		if len(alerts)>ii and a[0] == alerts[ii][0]:
			alerts_filled.append(alerts[ii])
			ii += 1
		else:
			alerts_filled.append([a[0], 0])

	max_lim = max(activity, key=lambda x: x[1])[1] + 2

	return JsonResponse({"alerts": alerts_filled, "activity": activity, "percent_alerts": per_alerts,
		"starts": start, "ends": end, "upper": max_lim})
