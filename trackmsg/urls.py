from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from .views import TrackerList, TrackerDetail, MessagePush, TrackerFormView

app_name = "trackmsg"

urlpatterns = [
    # tracker list view
    url(r'^list/', TrackerList.as_view(), name='list'),
    # tracker detail view
    url(r'^detail/(?P<pk>[0-9]+)/', TrackerDetail.as_view(), name='detail'),
    # tracker message push API
    url(r'^track/(?P<slug>\w[\w\-\d]+)/', csrf_exempt(MessagePush.as_view()), name='track'),
    # tracler form
    url(r'^form/$', TrackerFormView.as_view(), name='form'),
    url(r'^form/(?P<pk>[0-9]+)/$', TrackerFormView.as_view(), name='form-edit'),

]