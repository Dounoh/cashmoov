# Dans config/api_routers.py - Remplacer tout le contenu

from django.urls import path, include
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, 
    TokenVerifyView
)

# Documentation URLs
DOCS_URLS = [
    # Schema OpenAPI (JSON)
    path('swagger.<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # Swagger UI
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    # ReDoc
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]

# Authentication URLs
AUTH_URLS = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    #DJOSER FOR AUTHENTICATION
    re_path(r'^auth/', include('djoser.urls')),
    # re_path(r'^auth/', include('djoser.urls.authtoken')),
]

# Application URLs
APP_URLS = [
    path('chatbot/', include('cashmoov_api.chatbot.urls')),
]

urlpatterns = DOCS_URLS + AUTH_URLS + APP_URLS