from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from .serializers import VolumeSerializer, VolumeUpdateSerializer
from drf_yasg.utils import swagger_auto_schema
from .models import Volume


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
    


