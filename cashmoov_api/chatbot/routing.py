from django.urls import re_path
from cashmoov_api.chatbot.consumers import ChatConsumer,NotificationConsumer,OnlineUser

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/online/$', OnlineUser.as_asgi()),
]
