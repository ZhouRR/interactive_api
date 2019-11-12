from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'interactive_api/activity_live/', consumers.ActivityConsumer),
]