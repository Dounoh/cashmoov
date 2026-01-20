# Dans chatbot/views.py - Ajouter la documentation
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from cashmoov_api.chatbot.models import Document
from cashmoov_api.chatbot.serializers import DocumentSerializer, ChatbotRequestSerializer
from cashmoov_api.chatbot.rags.retrieval import search_documents,search_documents_sync
from cashmoov_api.chatbot.rags.prompt_llm import llm_humanise

class DocumentViewSet(viewsets.ModelViewSet):
    """
    Gestion des documents pour le système RAG
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_serializer(self, *args, **kwargs):
        if self.action == 'create':
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)


class ChatbotViewSet(viewsets.GenericViewSet):
    """
    Endpoint pour interagir avec le chatbot
    """
    permission_classes = [AllowAny]
    serializer_class = ChatbotRequestSerializer
    
    def get_serializer_class(self):
        if self.action == 'ask':
            return ChatbotRequestSerializer
        return super().get_serializer_class()
    
    @action(detail=False, methods=['post'], url_path='ask')
    def ask(self, request):
        """
        Endpoint pour poser une question au chatbot
        """
        question = request.data.get('question')
        # serializer = ChatbotRequestSerializer(data=question)
        # serializer.is_valid(raise_exception=True)
        # data = serializer.validated_data

        if not question:
            return Response({'error': 'Question manquante'}, status=400)
        
        result = search_documents_sync(question)
        llm_response = llm_humanise(query=question, context=result)
        
        return Response({'response': llm_response})

    