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

from review.views import VolumeViewSet, NumeroViewSet, SommaireViewset, SommaireListView, NumeroListView, TypeSourceView, SourceView, ArticleViewSet, ArticleListView, ValidSubmitArticle, PublicationtArticle, MostDownloadsArticle

from pageContent.views import *

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
router.register('sommaire-list', SommaireListView, basename='sommaire_list')
router.register('numero', NumeroViewSet, basename='numero')
router.register('numero-list', NumeroListView, basename='numero_list')
router.register('type_source-list', TypeSourceView, basename='type_source')
router.register('source', SourceView, basename='source')
#page content
router.register('pages', PageViewSet, basename="page")
router.register('pages-list', PageViewSetList, basename="pages_list")
router.register('article', ArticleViewSet, basename='article')
router.register('article-list', ArticleListView, basename='articles_list')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('author.urls')),
    path('api/valide/article/<int:pk>/', ValidSubmitArticle.as_view(), name='validate-article'),
    path('api/publication/article/<int:pk>/', PublicationtArticle.as_view(), name='publication-article'),
    path('api/popular/article/', MostDownloadsArticle.as_view(), name='popular-article'),
    path('api/article/filter/', ArticleViewSet.as_view({'post': 'filter_article'}), name='filter-article'),
    path('api/numero/filter/', NumeroViewSet.as_view({'post': 'filter_numero'}), name='numero-filter'),
    #path('api/article/', include('review.urls')),
    path('api/volume-numero/', NumeroViewSet.as_view({'get': 'get_numero_with_volume'}), name='volume-numero'),
    path('api/', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
