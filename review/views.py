from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, IsAuthenticated

from apiC2rlf.utils import CustomPagination
from .serializers import VolumeSerializer, NumeroSerializer, SommaireSerializer, NumeroSerializerList, SommaireSerializerList, TypeSourceSerializer, SourceSerializer, ArticleSerializer, ArticleSerializerList, ArticleSerializerViewOne, statisitiqueSerializer
from drf_yasg.utils import swagger_auto_schema
from .models import Volume, Numero, Sommaire, TypeSource, Source, Article
from django.test import override_settings
from apiC2rlf.enum import ArticleState
from datetime import datetime
from django.contrib.auth.models import User
from pageContent.models import PageContent
from ouvrage.models import Ouvrage, Category as CategoryOuvrage
from cours.models import Course, Level

class VolumeViewSet(ModelViewSet):
    serializer_class = VolumeSerializer
    queryset = Volume.objects.all().order_by('-volume_year')

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]


@swagger_auto_schema(
    responses={200: NumeroSerializer}
)
class NumeroViewSet(ModelViewSet):
    serializer_class = NumeroSerializer
    permission_classes = []

    def get_queryset(self, volume_id: int=0):
        if volume_id != 0: #get numero for volume_id given
            return Numero.objects.filter(volume=volume_id)
        return Numero.objects.all().order_by('-number')
 
    def get_permissions(self, active_perm=True):
        if self.action in ['create', 'update', 'destroy'] and active_perm:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        responses={200: NumeroSerializer}
    )
    def filter_numero(self, request):
        self.permission_classes = []
        self.get_permissions(False)
        self.check_permissions(request)
        filter_obj = {}
        #transform queryDict to json
        for key, value in request.data.items():
            filter_obj[key] = value
        numeros = Numero.objects.filter(**filter_obj).order_by('-number')
        serializer = NumeroSerializer(numeros, many=True)
        return Response(serializer.data)
    

@swagger_auto_schema(
    responses={200: SommaireSerializer}
)
class SommaireViewset(ModelViewSet):
    serializer_class = SommaireSerializer
    permission_classes = []

    def get_queryset(self):
        return Sommaire.objects.all().order_by('-numero__number')
    
    def create(self, request, *args, **kwargs):
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        return super().destroy(request, *args, **kwargs)
    
    def filter_sommaires(self, request):
        self.permission_classes = []
        self.check_permissions(request)
        self.pagination_class = CustomPagination

        limit = request.GET.get('limit')
        filter_obj = {} 
        #transform queryDict to json
        for key, value in request.data.items():
            filter_obj[key] = value

        if limit:
            self.pagination_class.page_size = limit        
        sommaires = Sommaire.objects.filter(**filter_obj).order_by('-numero__number')
        page = self.paginate_queryset(sommaires)

        if page is not None:
            serializer = SommaireSerializerList(page, many=True)
            return self.get_paginated_response(serializer.data)  
        serializer = SommaireSerializerList(sommaires, many=True)
        return Response(serializer.data)
        

@swagger_auto_schema(
    responses={200: SommaireSerializer}
)
class NumeroListView(ReadOnlyModelViewSet):
    serializer_class = NumeroSerializerList

    def get_queryset(self):
        return Numero.objects.all().order_by('-number')
    
@swagger_auto_schema(
    responses={200: SommaireSerializerList}
)
class SommaireListView(ReadOnlyModelViewSet):
    serializer_class = SommaireSerializerList

    def get_queryset(self):
        return Numero.objects.all().order_by('-number')
    
class TypeSourceView(ModelViewSet):
    serializer_class = TypeSourceSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        self.permission_classes = []
        return TypeSource.objects.all()
    
class SourceView(ModelViewSet):
    serializer_class = SourceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Source.objects.all()
    

class ArticleViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Article.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update'] or self.request.GET.get('retrieve'):
            return ArticleSerializer
        return ArticleSerializerViewOne
    

    def filter_article(self, request):
        self.permission_classes = []
        self.check_permissions(request)
        filter_obj = {}
        #transform queryDict to json
        for key, value in request.data.items():
            filter_obj[key] = value
        article = Article.objects.filter(**filter_obj).order_by('-date_publication')
        serializer = ArticleSerializerList(article, many=True)
        return Response(serializer.data)
    
    def get_permissions(self):
        if self.action in ['create', 'update']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = []

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        responses={200: None},
    )
    def destroy(self, request, format=None,*args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs['pk'])
        user = request.user
        if (user == article.user and article.state == ArticleState.INITIALISATION.value) or user.is_superuser:
            article.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"Interdit": "Vous n'avez pas l'abilitation requise pour effectuer cette action."}, status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(
        responses={200: statisitiqueSerializer},
    )
    def getSatat(self, request):
        data = {
            'numero': Numero.objects.count(),
            'sommaire': Sommaire.objects.count(),
            'article_init': Article.objects.filter(state=ArticleState.INITIALISATION.value).count(),
            'article_parution': Article.objects.filter(state=ArticleState.PARRUTION.value).count(),
            'article_publication': Article.objects.filter(state=ArticleState.PUBLICATION.value).count(),
            'cours_pdf': Course.objects.count(),
            'ouvrage': Ouvrage.objects.count(),
            'authors_active': User.objects.filter(is_active=True).count(),
            'volume': Volume.objects.count(),
            'page': PageContent.objects.count(),
            'type_source': TypeSource.objects.count(),
            'categorie_ouvrage': CategoryOuvrage.objects.count(),
            'niveau': Level.objects.count(),
        }
        
        serialializer = statisitiqueSerializer(data=data)
        if serialializer.is_valid():
            return Response(serialializer.data)
        return Response(serialializer.errors)
    


    """ 
    @swagger_auto_schema(
        responses={200: ArticleSerializerViewOne},
        request_body=ArticleSerializer
    )
    def update(self, request, format=None, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs['pk'])
        user = request.user
        if (user == article.user and article.state == ArticleState.INITIALISATION.value) or user.is_superuser:
            serializer = ArticleSerializer(data=request.data)
            serializer.file_submit = request.data.get('file_submit')
            import pdb;pdb.set_trace()
            if serializer.is_valid():
                article = serializer.update(article, serializer.data)
                serializer = ArticleSerializerViewOne(article)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Interdit": "Vous n'avez pas l'abilitation requise pour effectuer cette action."}, status=status.HTTP_403_FORBIDDEN)"""
        

@swagger_auto_schema(
    responses={200: ArticleSerializerList}
)
class ArticleListView(ReadOnlyModelViewSet):
    serializer_class = ArticleSerializerList
    permission_classes = []
    def get_queryset(self,*args, **kwargs):
        request = self.request
        if request.GET.get('state'):
            state = request.GET.get('state')
            return Article.objects.filter(state=state).order_by('numero__number')
        return Article.objects.all().order_by('numero__number')
    
  
@swagger_auto_schema(
    responses={200: ArticleSerializerViewOne},
    request_body=ArticleSerializer
)
class ValidSubmitArticle(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        article.state = ArticleState.PARRUTION.value
        article.date_accept = datetime.now()
        article.save()
        serializer = ArticleSerializerViewOne(article)
        return Response(serializer.data)

@swagger_auto_schema(
    responses={200: ArticleSerializerViewOne},
    request_body=ArticleSerializer
) 
class PublicationtArticle(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        if article.state != ArticleState.PUBLICATION.value:
            article.state = ArticleState.PUBLICATION.value
            article.date_publication = datetime.now()
            article.save()
            serializer = ArticleSerializerViewOne(article)
            return Response(serializer.data)
        serializer = ArticleSerializerViewOne(article)
        return Response(serializer.data)


@swagger_auto_schema(
    responses={200: ArticleSerializerList},
    request_body=ArticleSerializer
) 
class MostDownloadsArticle(APIView):
    permission_classes = []
    def get(self, request):
        articles = Article.objects.filter(state=ArticleState.PUBLICATION.value).order_by('-counter_download')[:5]
        serializer = ArticleSerializerList(articles, many=True)
        return Response(serializer.data)


@swagger_auto_schema(
    responses={200: ArticleSerializerList},
    request_body=ArticleSerializer
) 
class LastArticlePublication(APIView):
    permission_classes = []
    def get(self, request):
        articles = Article.objects.filter(state=ArticleState.PUBLICATION.value).order_by('-id')[:3]
        serializer = ArticleSerializerList(articles, many=True)
        return Response(serializer.data)
    
