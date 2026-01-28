import pytest

from cashmoov_api.chatbot.models import Document
from cashmoov_api.chatbot.serializers import (
    ChatbotRequestSerializer,
    DocumentListSerializer,
    DocumentSerializer,
)

pytestmark = pytest.mark.django_db


class TestDocumentSerializer:

    def test_serialization(self, document_fixture):
        serializer = DocumentSerializer(document_fixture)
        data = serializer.data

        assert data["slug"] == document_fixture.slug
        assert data["title"] == document_fixture.title
        assert data["content"] == document_fixture.content
        assert data["source_type"] == document_fixture.source_type
        assert data["is_active"] == document_fixture.is_active
        assert "created_at" in data
        assert "updated_at" in data

    def test_valid_creation(self):
        data = {
            "title": "New Document",
            "content": "New content",
            "source_type": Document.training,
        }
        serializer = DocumentSerializer(data=data)
        assert serializer.is_valid()
        document = serializer.save()
        assert document.title == "New Document"
        assert document.content == "New content"
        assert document.source_type == Document.training

    def test_many_creation(self):
        data = [
            {
                "title": "Document 1",
                "content": "Content 1",
                "source_type": Document.training,
            },
            {
                "title": "Document 2",
                "content": "Content 2",
                "source_type": Document.conversation,
            },
        ]
        serializer = DocumentSerializer(data=data, many=True)
        assert serializer.is_valid()
        documents = serializer.save()
        assert len(documents) == 2


class TestDocumentListSerializer:

    def test_serialization(self, many_document_fixture):

        documents = many_document_fixture
        serializer = DocumentListSerializer(documents, many=True)
        data = serializer.data

        assert len(data) == 3

        assert data[0]["slug"] == documents[0].slug
        assert data[0]["title"] == documents[0].title
        assert data[0]["source_type"] == documents[0].source_type
        assert data[0]["is_active"] == documents[0].is_active
        assert "created_at" in data[0]


class TestChatbotRequestSerializer:

    def test_valid_request(self):
        data = {"question": "c'est quoi cashmoov?"}
        serializer = ChatbotRequestSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["question"] == "c'est quoi cashmoov?"

    def test_missing_question(self):
        data = {}
        serializer = ChatbotRequestSerializer(data=data)
        assert not serializer.is_valid()
        assert "question" in serializer.errors

    def test_empty_question(self):
        data = {"question": ""}
        serializer = ChatbotRequestSerializer(data=data)
        assert not serializer.is_valid()
        assert "question" in serializer.errors
