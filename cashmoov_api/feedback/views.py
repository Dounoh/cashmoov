from django.shortcuts import render

from rest_framework import viewsets
from .models import Feedback
from .serializers import FeedbackSerializer, FeedbackListSerializer, FeedbackRetrieveSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    list_serializer_class = FeedbackListSerializer
    retrieve_serializer_class = FeedbackRetrieveSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        elif self.action == 'retrieve':
            return self.retrieve_serializer_class
        return self.serializer_class
