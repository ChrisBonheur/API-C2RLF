from urllib import response
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.permissions import IsAdminUser
from . serializers import LevelSerializer, CourCreateOrUpdateSerializer, CourseListSerializer, CourseRetrieveSerializer, CourseFilterSerializer
from .models import Level, Course
from apiC2rlf.utils import CustomPagination
from drf_yasg.utils import swagger_auto_schema

class LevelViewSet(ModelViewSet):
    serializer_class = LevelSerializer
    queryset = Level.objects.all().order_by('order')

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []

        return [permission() for permission in permission_classes]


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.filter(is_public=True).order_by('date_creation')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return CourCreateOrUpdateSerializer
        elif self.action == 'retrieve':
            return CourseRetrieveSerializer
        return CourseListSerializer
    
    def get_permissions(self):

        if self.action in ['create', 'update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []

        return [permission() for permission in permission_classes]
    
    def filter_cours(self, request):
        self.permission_classes = []
        self.check_permissions(request)
        self.pagination_class = CustomPagination
        data = request.data

        if data.get('levels_id'):
            level_filters = [Q(level__id=level_id) for level_id in data['levels_id']]

            # Utilisez l'opérateur OR pour combiner les filtres
            query = level_filters[0]
            for q in level_filters[1:]:
                query |= q

            # Utilisez la requête pour filtrer les cours
            limit = request.GET.get('limit')
            if limit:
                self.pagination_class.page_size = limit   
            filtered_courses = Course.objects.filter(query, is_public=True).order_by('-date_creation')
            page = self.paginate_queryset(filtered_courses)
            context = {'request': self.request}
            if page is not None:
                serializer = CourseListSerializer(page, many=True, context=context)
                return self.get_paginated_response(serializer.data)
            else:
                serializer = CourseListSerializer(filtered_courses, many=True, context=context)    

            return Response(serializer.data)
        else:
            return Response({"error": 'levels_id non trouve'})
    
