import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

# Autoriser l'accès à la base de données pour tous les tests
pytestmark = pytest.mark.django_db


class TestUserModel:

    def test_create_user(self, user_data_fixture):
        user_data = user_data_fixture

        user = User.objects.create_user(**user_data)

        assert user.email == user_data["email"]
        assert user.first_name == user_data["first_name"]
        assert user.last_name == user_data["last_name"]
        assert user.address == user_data["address"]
        assert user.user_type == User.ASSISTANT
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com", password="testpass123"
        )

        assert user.email == "admin@example.com"
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_user_type_choices(self):
        assert User.USER_TYPE_CHOICE == (
            (User.ASSISTANT, "assistant"),
            (User.ADMIN, "Admin"),
        )

    def test_unique_email(self, user_data_fixture):
        user_data = user_data_fixture
        User.objects.create_user(**user_data)

        with pytest.raises(IntegrityError):
            User.objects.create_user(**user_data)
