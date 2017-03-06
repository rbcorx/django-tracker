from django.contrib import admin

from .models import *

class GeoFenceAdmin(admin.ModelAdmin):
	list_display = ["label", "vertices"]


class TrackerAdmin(admin.ModelAdmin):
	list_display = ["user", "name", "created", "get_total_messages", "get_total_alerts", "active", "url",]


class MessageAdmin(admin.ModelAdmin):
	list_display = ["tracker", "timestamp", "coordinate", "alerted", "geo_fence"]

admin.site.register(GeoFence, GeoFenceAdmin)
admin.site.register(Tracker, TrackerAdmin)
admin.site.register(Message, MessageAdmin)

