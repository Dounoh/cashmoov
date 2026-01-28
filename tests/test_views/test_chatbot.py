import pytest
from django.urls import reverse
from rest_framework import status

from cashmoov_api.chatbot.models import Document

pytestmark = pytest.mark.django_db


class TestDocumentViewSet:

    def test_list_documents_unauthorized(self, api_client):
        url = reverse("document-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_documents_regular_user(self, api_client, regular_user):
        api_client.force_authenticate(user=regular_user)
        url = reverse("document-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_documents_admin(self, api_client, admin_user, document):
        api_client.force_authenticate(user=admin_user)
        url = reverse("document-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["title"] == document.title

    def test_retrieve_document_admin(self, api_client, admin_user, document):
        api_client.force_authenticate(user=admin_user)
        url = reverse("document-detail", kwargs={"slug": document.slug})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == document.title
        assert response.data["content"] == document.content

    def test_create_document_admin(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse("document-list")
        data = [
            {
                "title": "New Document",
                "content": "New content",
                "source_type": Document.conversation,
            }
        ]
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Document.objects.count() == 1

    def test_delete_document_admin(self, api_client, admin_user, document):
        api_client.force_authenticate(user=admin_user)
        url = reverse("document-detail", kwargs={"slug": document.slug})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Document.objects.count() == 0


class TestChatbotViewSet:

    def test_ask_question_with_data(self, api_client, document_fixture):
        url = reverse("chatbot-ask")
        data = {"question": "string"}
        response = api_client.post(url, data=data, format="json")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

    def test_ask_question_missing_data(self, api_client):
        url = reverse("chatbot-ask")
        response = api_client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_ask_question_empty_question(self, api_client):
        url = reverse("chatbot-ask")
        response = api_client.post(url, {"question": ""}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
