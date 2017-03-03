from django.forms import ModelForm

from .models import Tracker

class TrackerForm(ModelForm):
	class Meta:
		model = Tracker
		exclude = ['user', 'created']