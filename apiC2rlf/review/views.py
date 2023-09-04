from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from .serializers import VolumeSerializer, VolumeUpdateSerializer, NumeroSerializer, SommaireSerializer
from drf_yasg.utils import swagger_auto_schema
from .models import Volume, Numero, Sommaire


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
        return Numero.objects.all()

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
        return Sommaire.objects.all()
    
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
    
    