from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, ChatbotViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='documents')
router.register(r'chatbot', ChatbotViewSet, basename='chatbot')

urlpatterns = [
    path('', include(router.urls)),
]
