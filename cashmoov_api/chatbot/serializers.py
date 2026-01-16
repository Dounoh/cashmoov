# Dans chatbot/serializers.py - Ajouter la documentation

from rest_framework import serializers
from cashmoov_api.chatbot.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer pour les documents du système RAG
    """
    class Meta:
        model = Document
        fields = (
            'slug', 
            'title',
            'content',
            'source_type',
            'is_active',
            'created_at',
            'updated_at',
            'embedding',
        )
        read_only_fields = ('slug', 'created_at', 'updated_at')


class ChatbotRequestSerializer(serializers.Serializer):
    """
    Serializer pour les requêtes du chatbot
    """
    question = serializers.CharField(required=True, help_text="La question posée par l'utilisateur")
    
    class Meta:
        fields = ('question',)
