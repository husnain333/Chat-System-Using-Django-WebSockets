from django.urls import path
from .views import MessageListAPIView

urlpatterns = [
    path('messages/<str:room_name>/', MessageListAPIView.as_view(), name='room-messages'),
]
