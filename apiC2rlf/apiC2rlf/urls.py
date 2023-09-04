import statistics
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from review.views import VolumeViewSet, NumeroViewSet, SommaireViewset


schema_view = get_schema_view(
    openapi.Info(
        title="C2RLF API",
        default_version='v1',
        description="api For review",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="bonheurmafoundou@gmail.com"),
        license=openapi.License(name=""),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = routers.SimpleRouter()

router.register('volume', VolumeViewSet, basename='volume')
router.register('sommaire', SommaireViewset, basename='sommaire')
router.register('numero', NumeroViewSet, basename='numero')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('author.urls')),
    path('api/', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
