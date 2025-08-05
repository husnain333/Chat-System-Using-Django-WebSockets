from django.shortcuts import render
from rest_framework import generics
from .models import Message
from .serializers import MessageSerializer

class MessageListAPIView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        room_name = self.kwargs['room_name']
        return Message.objects.filter(room__name=room_name).order_by('timestamp')