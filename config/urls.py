from django.contrib import admin
from django.urls import path, include
from django.urls import reverse
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
schema_view = get_schema_view(
    openapi.Info(
        title="Chatbot cashmoov API",
        default_version='v1.0.0',
        description=
    """
        API CashMoov Assistant IA et Humain

        DESCRIPTION
        API permettant l'intégration d'un assistant intelligent combinant IA et support
        humain pour la plateforme CashMoov.


        FONCTIONNALITÉS PRINCIPALES
        - Authentification et gestion des utilisateurs
        - Interface chatbot avec traitement NLP
        - Transfert vers support humain
        - Historique des conversations
        - Gestion des feedbacks utilisateur
        - Conversion de money


        CODES DE STATUT HTTP
        - 200 : Succès
        - 201 : Créé avec succès
        - 400 : Requête invalide
        - 401 : Non authentifié
        - 403 : Non autorisé
        - 404 : Non trouvé
        - 500 : Erreur serveur


        TECHNOLOGIES UTILISÉES
        - Django & Django REST Framework
        - Djoser pour l'authentification
        - PostgreSQL
        - Redis pour Django Channels (WebSocket)
        - Celery pour les tâches asynchrones
        - django-redis pour le cache
##LA DOCUMENTATION DE DJANGO SHANELL (socket) la messagerie instanté est [ici](/api/shannel/)"
    """"",
        terms_of_service="https://www.cashmoov.net",
        contact=openapi.Contact(
            email="contact@cashmoov.net",
            name="Support CashMoov",
            url="https://www.cashmoov.net/contact"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
        permission_classes=(permissions.IsAdminUser,),
    )

from django.views.generic import TemplateView

urlpatterns = [
        # Schema OpenAPI (JSON)
    # path('swagger.<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # Swagger UI
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    # ReDoc
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('api/shannel/', TemplateView.as_view(template_name="channel_docs.html"), name='channel'),

    # path('', TemplateView.as_view(template_name="home.html"), name='home'),

    path('api/admin-cashmoov/', admin.site.urls),
    path('api/', include('config.api_routers')),    
]