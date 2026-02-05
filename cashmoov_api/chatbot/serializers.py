# Dans chatbot/serializers.py - Ajouter la documentation

from rest_framework import serializers

from cashmoov_api.chatbot.models import Chatbot, Document, Group


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = (
            "slug",
            "title",
            "content",
            "source_type",
            "is_active",
            "created_at",
            "updated_at",
            "embedding",
        )
        read_only_fields = (
            "slug",
            "created_at",
            "updated_at",
            "embedding",
        )


class DocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = (
            "slug",
            "title",
            "source_type",
            "is_active",
            "created_at",
            "updated_at",
            # "embedding",
        )
        read_only_fields = fields


class ChatbotRequestSerializer(serializers.Serializer):
    question = serializers.CharField(
        required=True, help_text="La question posée par l'utilisateur"
    )

    class Meta:
        fields = ("question",)


class ChattingSerializer(serializers.ModelSerializer):
    groupe_name = serializers.CharField(source="group.name")

    class Meta:
        fields = (
            "slug",
            "username",
            "groupe_name",
            "created_at",
            "question",
            "answers",
            "used_for_training",
            "validated_for_training",
        )
        model = Chatbot
        read_only_fields = fields


class GroupListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "slug",
            "name",
            "created_at",
        )
        model = Group
        read_only_fields = fields


class ValidateTrainingSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "validate_training"
