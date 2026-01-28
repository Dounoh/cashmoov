import pytest
from rest_framework.test import APIClient

from cashmoov_api.chatbot.models import Document, Group
from cashmoov_api.users.models import User


@pytest.fixture
def document_fixture(db):
    return Document.objects.create(
        title="fixture document",
        content="fixture content",
        source_type=Document.conversation,
    )


@pytest.fixture
def many_document_fixture(db):
    docs = [
        {
            "title": "fixture document 1",
            "content": "fixture content 1",
            "source_type": Document.training,
        },
        {
            "title": "fixture document 2",
            "content": "fixture content 2",
            "source_type": Document.conversation,
        },
        {
            "title": "fixture document 3",
            "content": "fixture content 3",
            "source_type": Document.training,
        },
    ]
    Document.objects.bulk_create([Document(**doc) for doc in docs])
    return Document.objects.all()


@pytest.fixture
def group_fixture(db):
    return Group.objects.create(name="Fixture Group")


@pytest.fixture
def user_fixture(db):
    return User.objects.create_user(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        address="Test Address",
    )


@pytest.fixture
def user_data_fixture():
    return {
        "email": "test1@example.com",
        "first_name": "Test",
        "last_name": "User",
        "address": "Test Address",
    }


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        email="admin@example.com", password="adminpass123"
    )


@pytest.fixture
def regular_user():
    return User.objects.create_user(
        email="user@example.com",
        password="userpass123",
        first_name="Regular",
        last_name="User",
    )


@pytest.fixture
def document():
    return Document.objects.create(
        title="Test Document", content="Test content", source_type=Document.training
    )
