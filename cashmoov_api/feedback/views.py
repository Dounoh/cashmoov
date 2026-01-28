from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from cashmoov_api.common.utils import MultipleSerializerMixin
from cashmoov_api.users.permissions import IsAdminUser

from .models import Feedback
from .serializers import (
    FeedbackListSerializer,
    FeedbackRetrieveSerializer,
    FeedbackSerializer,
)


class FeedbackViewSet(
    MultipleSerializerMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Cette viewSet est pour gerer les retours client
    \n GET: pour la liste des commentaire laisser par les clients
    \n GET/{slug}: afficher les details d'un commentaire
    \n POST: Ajouter un commentaire
    \n DELETE: Supprimer un commentaire

    """

    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    list_serializer_class = FeedbackListSerializer
    retrieve_serializer_class = FeedbackRetrieveSerializer
    lookup_field = "slug"
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        else:
            return [IsAdminUser()]
