from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from drf_yasg.utils import swagger_auto_schema

from . serializers import categorySerializer, OuvrageSerializer, OuvrageSerializerList, OuvrageRetrieveSerializer
from . models import Category, Ouvrage
from apiC2rlf.utils import CustomPagination

@swagger_auto_schema(
    responses={200: categorySerializer}
)
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = categorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []

        return [permission() for permission in permission_classes]

@swagger_auto_schema(
    responses={200: OuvrageSerializer}
)
class OuvrageViewSet(ModelViewSet):
    queryset = Ouvrage.objects.filter(is_active=True).order_by('-date_creation')

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return OuvrageSerializer
        elif self.action == 'retrieve':
            return OuvrageRetrieveSerializer
        return OuvrageSerializerList
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []

        return [permission() for permission in permission_classes]
    
    @swagger_auto_schema(
        responses={200: OuvrageSerializerList},
        request_body=OuvrageSerializer
    )
    def filter_ouvrage(self, request):
        self.permission_classes = []
        self.check_permissions(request)
        self.pagination_class = CustomPagination

        limit = request.GET.get('limit')
        if limit:
            self.pagination_class.page_size = limit        
        ouvrages = Ouvrage.objects.filter(**request.data)
        page = self.paginate_queryset(ouvrages)

        if page is not None:
            serializer = OuvrageSerializerList(page, many=True)
            return self.get_paginated_response(serializer.data)  
        serializer = OuvrageSerializerList(ouvrages, many=True)
        return Response(serializer.data)
        
    
    