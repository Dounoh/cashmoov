from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from cashmoov_api.chatbot.models import Chatbot, Document, Group
from cashmoov_api.chatbot.rags.prompt_llm import llm_humanise
from cashmoov_api.chatbot.rags.retrieval import search_documents_sync
from cashmoov_api.chatbot.serializers import (
    ChatbotRequestSerializer,
    ChattingSerializer,
    DocumentListSerializer,
    DocumentSerializer,
    GroupListSerializer,
)
from cashmoov_api.common.utils import MultipleSerializerMixin
from cashmoov_api.users.permissions import IsAdminUser


class DocumentViewSet(MultipleSerializerMixin, viewsets.ModelViewSet):
    # """
    #     Cet endpoint est utiliser pour inserer des donnees dans la base de connaissance du RAG\n
    #     et avoir access aux informations dejà disponible dans sa base.\n
    #     La possibiliter de desactiver une connaissance qui nest plus pertinante \n

    #     ###FONCTIONNEMENT:

    #     \n GET: pour Afficher la liste des informations disponible
    #     \n GET/{slug}: Affiche les details de linforamtion
    #     \n PATCH/{slug}: Desactiver une informations
    #     \n PATCH/{slug}: Modifier les informations mineurs de l'application (titre,source_type)
    #     \n DELETE/{slug}: Supprimer une iformation de la base de donnee.
    #     \n POST: Ajouter des informations dans la base de connaissance du RAG.\n
    #         il est conseiller de decouper les mots de chaque context en maximum 500 mots pour faciliter la recherche vectorielle \n
    #         et de trouver les resultats pertinent lors de la recherche.
    #         --champs obligatoirs: context,source_type.

    # """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    list_serializer_class = DocumentListSerializer
    update_serializer_class = DocumentSerializer
    detail_serializer_class = DocumentSerializer

    permission_classes = [IsAdminUser]
    lookup_field = "slug"

    def get_serializer(self, *args, **kwargs):
        if self.action == "create":
            kwargs["many"] = True
        return super().get_serializer(*args, **kwargs)


class ChatbotViewSet(viewsets.GenericViewSet):
    """
    Endpoint pour interagir avec le RAG poser vos question de façon
    synchrone optenir une reponse.
    ce endpoint est utiliser pour tester la performance du RAG.
    """

    permission_classes = [AllowAny]
    serializer_class = ChatbotRequestSerializer

    def get_serializer_class(self):
        if self.action == "ask":
            return ChatbotRequestSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["post"], url_path="ask")
    def ask(self, request):
        """
        Endpoint pour poser une question au chatbot
        """
        serializer = ChatbotRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if not data:
            return Response(
                {"error": "Veillez bien saisir la question"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = search_documents_sync(data["question"])
        llm_response = llm_humanise(query=data["question"], context=result)

        return Response({"response": llm_response})


class TrainingViewSet(
    mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    """
    Cette collection de view est pour l'entrainement du model.
    La liste affiche les groupes de discussion ayant été effectuer sur la platforme
    et vous avez la possibilité d'afficher les details du groupe pour voir les conversations
    qui ont été effectuer dans ce groupe et puis valider une conversation si elle peut etre utiliser pour
    entrainier le model ou pas.
    """

    serializer_class = GroupListSerializer
    queryset = Group.objects.all().prefetch_related("chatbots")
    lookup_field = "slug"

    @swagger_auto_schema(
        method="get",
        responses={200: GroupListSerializer},
        operation_description="afficher le detail d'un groupe de discussion",
    )
    @action(detail=True, methods=["GET"], url_path="retrieve_group")
    def retrive_group(self, request, slug):
        """
        Endpoint pour afficher le detail d'un groupe avec ses discussions.
        il prend en GET le slug du groupe.
        """
        group = self.get_object()

        chats = group.chatbots.all()
        serializer = ChattingSerializer(chats, many=True).data

        return Response(data=serializer, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        methods=["patch"],
        responses={200: f"status:success"},
        operation_description="endpoint pour la validation des discussion pour q'uil soit valable pour l'entrainement",
    )
    @action(detail=True, methods=["patch"], url_name="validate_chat_for_training")
    def validate_chat_for_training(self, request, slug):
        """
        la view pour valider si une conversation peut etre utiliser pour entrainer le model ou pas.
        Elle prend en GET le slug de la conversation à valider
        """

        try:
            chat = Chatbot.objects.get(slug=slug)
            chat.validate_chat_for_training = True
            chat.save()

        except Chatbot.DoesNotExist:
            return Response(
                data={"error": "le slug saisi ne correspond à aucune conversation."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({"status": "success"}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        methods=["get"],
        responses={200: f"status:success"},
        operation_description="Debuter l'entrainement du model avec les conversation valider.",
    )
    @action(detail=False, methods=["get"], url_path="start_training")
    def start_training(self, request, slug):
        """
        Debuter l'entrainement du model avec les conversation valider.
        """
        with transaction.atomic():
            chats = Chatbot.objects.filter(
                validate_chat_for_training=True, used_for_training=False
            )

            docs = [
                {
                    "title": chat.question,
                    "content": chat.content,
                    "source_type": Document.conversation,
                }
                for chat in chats
            ]

            serializer = DocumentSerializer(data=docs, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            chats.update(used_for_training=True)

        return Response(data={"status": "success"}, status=status.HTTP_201_CREATED)
