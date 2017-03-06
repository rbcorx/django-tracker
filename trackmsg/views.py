import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views import generic
from django.core.urlresolvers import reverse
from django.core.mail import send_mail

from .populate import DEF_USER as DU
from .models import Tracker, Message, GeoFence, DELIMITER_COOR
from .forms import TrackerForm

#TODO login_required to views

# TODO renamve views append view, remove form
# TODO restructure file to directory package

class TrackerList(generic.ListView):
	template = "trackmsg/tracker_list.html"
	context_object_name = "trackers"

	def get_queryset(self):
		#TODO change user to logged in
		return Tracker.objects.filter(user=DU).order_by("-created")[:10]


class TrackerDetail(generic.DetailView):
	model = Tracker
	template = "trackmsg/tracker_detail.html"


class TrackerFormView(generic.View):

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
		except:
			res["errors"] = "Incorrectly formed data!"
			status=400
		
		try:
			tracker = Tracker.objects.get(url=slug)
		except Tracker.DoesNotExist:
			res["errors"] = "Unidentified Slug!"
			status=404

		if not tracker.active:
			res["errors"] = "tracker is inactive!"
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
				self.notify_user(request.user, _m)
				res["message"] = "success! message stored and alerted!"
				status = 201		

		return JsonResponse(res, status=status)


	def notify_user(self, user, message):
		"""Emails user of the message alert"""
		# TODO HANDLE rest security and annonymous user
		try:
			email = user.email
		except:
			email = "ronniebhase@gmail.com"
		
		send_mail(
		    'Tracker alert!',
		    'You awesome tracker has detected coordinates: {} in geo-fence {}.'.format(message.coordinate, message.geo_fence),
		    'admin@localhost.com',
		    [email,],
		    fail_silently=False,
		)

#TODO tracker create and edit
