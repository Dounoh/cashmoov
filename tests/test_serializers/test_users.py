import pytest

from cashmoov_api.users.models import User
from cashmoov_api.users.serializers import (
    CurrentUserDetailSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
)

pytestmark = pytest.mark.django_db


class TestUserCreateSerializer:

    def test_valid_data(self, user_data_fixture):
        data = user_data_fixture
        data["password"] = "TestPassword123!"

        serializer = UserCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
        assert user.email == data["email"]
        assert user.first_name == data["first_name"]
        assert user.last_name == data["last_name"]
        assert user.address == data["address"]
        assert user.slug is not None

    def test_duplicate_email(self):
        data = {
            "email": "test@example.com",
            "first_name": "Test2",
            "last_name": "User2",
        }
        User.objects.create_user(**data)
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_required_fields(self):
        data = {}
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors


class TestUserDetailSerializer:

    def test_serialization(self, user_fixture):
        serializer = UserDetailSerializer(user_fixture)
        data = serializer.data
        assert data["email"] == user_fixture.email
        assert data["first_name"] == user_fixture.first_name
        assert data["last_name"] == user_fixture.last_name
        assert data["address"] == user_fixture.address


class TestCurrentUserDetailSerializer:

    def test_serialization(self, user_fixture):
        serializer = CurrentUserDetailSerializer(user_fixture)
        data = serializer.data
        assert data["email"] == user_fixture.email
        assert data["first_name"] == user_fixture.first_name
        assert data["last_name"] == user_fixture.last_name
        assert data["address"] == user_fixture.address
