import django_filters
from cashmoov_api.chatbot.models import Document

class DocumentFilters(django_filters.FilterSet):

    class Meta:
        model = Document
        fields = ('source_type','is_active',)