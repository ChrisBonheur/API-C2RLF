from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAdminUser

from .serializers import PageSerializer
from .models import PageContent

class PageViewSet(ModelViewSet):
    serializer_class = PageSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return PageContent.objects.all().order_by('order')
    

class PageViewSetList(ReadOnlyModelViewSet):
    serializer_class = PageSerializer
    def get_queryset(self):
        return PageContent.objects.all().order_by('order')
