import pytest

from cashmoov_api.chatbot.models import Chatbot, Document, Group

pytestmark = pytest.mark.django_db


class TestDocumentModel:
    """Test cases for Document model."""

    def test_create_document(self):
        """Test pour la création d'un document."""
        document = Document.objects.create(
            title="Test Document", content="Test content", source_type=Document.training
        )

        assert document.title == "Test Document"
        assert document.content == "Test content"
        assert document.source_type == Document.training
        assert document.is_active is True
        assert document.embedding_model == "intfloat/multilingual-e5-base"
        assert document.slug is not None

    def test_source_type_choices(self):
        """Test pour les choix de source_type."""
        assert Document.source_type_choices == (
            (Document.training, "training"),
            (Document.conversation, "conversation"),
        )

    def test_unique_slug(self):
        """test pour s'assurer que les slugs sont uniques."""
        doc1 = Document.objects.create(
            title="Document 1", content="Content 1", source_type=Document.training
        )
        doc2 = Document.objects.create(
            title="Document 2", content="Content 2", source_type=Document.training
        )

        assert doc1.slug != doc2.slug


class TestGroupModel:
    """Test pour le modèle Group."""

    def test_create_group(self):
        """Test pour la création d'un groupe."""
        group = Group.objects.create(name="Test Group")

        assert group.name == "Test Group"
        assert group.slug is not None
        assert isinstance(group.slug, str)
        groups = Group.objects.all()
        assert len(groups) == 1


class TestChatbotModel:
    """Test cases for Chatbot model."""

    def test_create_chatbot(self, group_fixture):
        """Test creating a chatbot."""
        chatbot = Chatbot.objects.create(
            username="cashmoov_bot",
            group=group_fixture,
            question="Test question",
            answers="Test answer",
        )

        assert chatbot.username == "cashmoov_bot"
        assert chatbot.group == group_fixture
        assert chatbot.question == "Test question"
        assert chatbot.answers == "Test answer"
        assert chatbot.slug is not None
