from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from .serializers import VolumeSerializer, VolumeUpdateSerializer, NumeroSerializer, SommaireSerializer, NumeroSerializerList, SommaireSerializerList, TypeSourceSerializer, SourceSerializer
from drf_yasg.utils import swagger_auto_schema
from .models import Volume, Numero, Sommaire, TypeSource, Source
from django.test import override_settings

class VolumeViewSet(ModelViewSet):
    serializer_class = VolumeSerializer
    permission_classes = []

    def get_queryset(self):
        return Volume.objects.all()
    
    @swagger_auto_schema(
        responses={200: VolumeSerializer}
    )
    def create(self, request, *args, **kwargs):
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        responses={200: VolumeSerializer}
    )
    def update(self, request, *args, **kwargs):
        self.serializer_class = VolumeUpdateSerializer
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        return super().update(request, *args, **kwargs)
    

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
    

