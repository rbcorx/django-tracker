import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import generic

from .populate import DEF_USER as DU
from .models import *

def test(request):
	return render(request, "trackmsg/skeleton.html", {})

class TrackerList(generic.ListView):
	template = "trackmsg/tracker_list.html"
	context_object_name = "trackers"

	def get_queryset(self):
		#TODO change user to logged in
		return Tracker.objects.filter(user=DU).order_by("-created")[:10]


class TrackerDetail(generic.DetailView):
	model = Tracker
	template = "trackmsg/tracker_detail.html"


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
