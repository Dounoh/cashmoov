from django.urls import path, include
from django.urls import re_path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, 
    TokenVerifyView
)


# Authentication URLs
AUTH_URLS = [
    re_path(r'^profile/', include('djoser.urls')),
    
    path('auth/token/', TokenObtainPairView.as_view(), name='auth-token-obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='auth-token-verify'),
    ]

# Application URLs
APP_URLS = [
    path('chatbot/', include('cashmoov_api.chatbot.urls')),
    path('feedback/', include('cashmoov_api.feedback.urls')),
]

urlpatterns = AUTH_URLS + APP_URLS