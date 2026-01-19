from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
schema_view = get_schema_view(
   openapi.Info(
      title="Chatbot cashmoov API",
      default_version='v1',
      description="Un assistant ia et hummain combiner pour cashmoov",
      terms_of_service="https://www.cashmoov.net",
      contact=openapi.Contact(email="contact@cashmoov.net"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
    permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
        # Schema OpenAPI (JSON)
    # path('swagger.<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # Swagger UI
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    # ReDoc
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),


    path('admin/', admin.site.urls),
    path('api/', include('config.api_routers')),    
]