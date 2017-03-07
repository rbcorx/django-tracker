from django.forms import ModelForm
from django.contrib.auth.models import User

from .models import Tracker

class TrackerForm(ModelForm):
	class Meta:
		model = Tracker
		exclude = ['user', 'created']

class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ["username", "password", "email", "is_active",]