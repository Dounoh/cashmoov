from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ChatbotViewSet, DocumentViewSet, TrainingViewSet

router = DefaultRouter()
router.register(r"documents", DocumentViewSet, basename="document")
router.register(r"chatbots", ChatbotViewSet, basename="chatbot")
router.register(r"trainings", TrainingViewSet, basename="training")

urlpatterns = [
    path("", include(router.urls)),
]
