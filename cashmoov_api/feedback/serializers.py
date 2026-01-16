from rest_framework import serializers
from .models import Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['first_name', 'last_name', 'email', 'message']
        read_only_fields = ['id','slug', 'created_at', 'updated_at']


class FeedbackListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['first_name', 'last_name', 'email']
        read_only_fields = fields


class FeedbackRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['first_name', 'last_name', 'email', 'message']
        read_only_fields = fields
