import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views import generic
from django.core.urlresolvers import reverse

from .populate import DEF_USER as DU
from .models import Tracker, Message, GeoFence, DELIMITER_COOR
from .forms import TrackerForm

#TODO login_required to views

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
			return HttpResponseRedirect(reverse("trackmsg:list"))
		else:
			context["form"] = form
		return render(request, 'trackmsg/tracker_form.html', context)



class MessagePush(generic.View):
	http_method_names = ['options', 'trace', 'post']

	def post(self, request, *args, **kwargs):
		data = json.loads(request.body)
		res = {}
		try:
			x = float(data["x"])
			y = float(data["y"])
			point = [str(x), str(y)]

			print kwargs
			point = DELIMITER_COOR.join(point)
			print kwargs
			
			slug = kwargs["slug"]
		except:
			res["errors"] = "Incorrectly formed data!"
			return JsonResponse(res, status=400)
		
		try:
			tracker = Tracker.objects.get(url=slug)
		except Tracker.DoesNotExist:
			res["errors"] = "Unidentified Slug!"
			return JsonResponse(res, status=404)

		if not tracker.active:
			res["errors"] = "tracker is inactive!"
			return JsonResponse(res, status=400)

		_m = Message(tracker=tracker, coordinate=point)
		
		if not _m.process():
			try:
				_m.save()
			except:
				res["errors"] = "Couldn't save message!"
				return JsonResponse(res, status=400)

		res["message"] = "success! message stored!"

		return JsonResponse(res, status=201)

#TODO tracker create and edit
