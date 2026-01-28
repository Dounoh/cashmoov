import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from cashmoov_api.chatbot.models import Document

pytestmark = pytest.mark.django_db


class TestAPIIntegrationFlow:
    """Integration tests for complete API workflows."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup API client for all tests."""
        self.client = APIClient()

    def test_complete_document_workflow(self, regular_user, admin_user):
        self.client.force_authenticate(user=admin_user)

        documents_data = [
            {
                "title": "Python Basics",
                "content": "Python is a high-level programming language.",
                "source_type": Document.training,
            },
            {
                "title": "Django Framework",
                "content": "Django is a Python web framework.",
                "source_type": Document.training,
            },
        ]

        url = reverse("document-list")
        response = self.client.post(url, documents_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data) == 2

        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

        document_slug = response.data["results"][0]["slug"]
        detail_url = reverse("document-detail", kwargs={"slug": document_slug})
        response = self.client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert "content" in response.data

        response = self.client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        response = self.client.get(url)
        assert response.data["count"] == 1
