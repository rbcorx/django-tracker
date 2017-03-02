from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from .views import *

app_name = "trackmsg"

urlpatterns = [
    url(r'^$', test, name='test'),
    url(r'^list/', TrackerList.as_view(), name='list'),
    url(r'^detail/(?P<pk>[0-9]+)/', TrackerDetail.as_view(), name='detail'),
    url(r'^track/(?P<slug>\w[\w\-\d]+)/', csrf_exempt(MessagePush.as_view()), name='track'),
]