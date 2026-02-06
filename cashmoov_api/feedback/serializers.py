from rest_framework import serializers

from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["first_name", "last_name","phone_number", "email", "message"]
        read_only_fields = ["slug", "created_at", "updated_at"]


class FeedbackListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["slug","first_name", "last_name","phone_number", "email"]
        read_only_fields = fields


class FeedbackRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["slug","first_name", "last_name", "phone_number","email", "message"]
        read_only_fields = fields
