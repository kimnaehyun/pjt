from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/books/(?P<book_id>\d+)/$', consumers.ReviewConsumer.as_asgi()),
    re_path(r'ws/books/(?P<book_id>\d+)/$', consumers.BookConsumer.as_asgi()),
]
