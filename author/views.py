#from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from django.db.utils import IntegrityError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_yasg.utils import swagger_auto_schema

from .serializers import UserSerializer, UserAuthorSerializer, UserListSerializer
from .models import Author
from django.core.exceptions import PermissionDenied

class AuthorAPIView(APIView):
    permission_classes = []

    def get(self, request, id_user: int = 0):
        """Get one user or more
        Args:
            id_user (int, optional): if id_user is past we get specific user.
        Returns:
            UserSerializer: list or single
        """
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        if(request.GET.get('user_id')):
            #user authenticate can only get his own data of user
            userSerializer = UserSerializer(request.user)
            return Response(userSerializer.data, status=status.HTTP_200_OK)
        else:
            #only admin get get user by that way many or one
            self.permission_classes = [IsAdminUser]
            self.check_permissions(request)
            if(id_user):
                user = get_object_or_404(User, pk=id_user)
                userSerializer = UserSerializer(user)
                return Response(userSerializer.data, status=status.HTTP_200_OK)
            else:
                users = User.objects.filter(is_active=True)
                userSerializer = UserListSerializer(users, many=True)
                return Response(userSerializer.data, status=status.HTTP_200_OK)
                    
    @swagger_auto_schema(
        responses={200: UserSerializer}
    )
    def post(self, request):
        authorSerializer = UserAuthorSerializer(data=request.data, context={'is_create_or_update': True})

        if authorSerializer.is_valid():
            user, author = authorSerializer.create(authorSerializer.data)
            userSerializer = UserSerializer(user)
            return Response(userSerializer.data, status=status.HTTP_201_CREATED)
        print(authorSerializer.errors)
        return Response(authorSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        responses={200: UserSerializer}
    )
    def put(self, request, id_user: int):
        authorSerializer = UserAuthorSerializer(data=request.data, context={'is_create_or_update': True})
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        if(not request.user.is_superuser and request.user.id != id_user):
            raise PermissionDenied("Vous n'avez pas les autorisation nécessaire pour modifier cet utilisateur.")
        if authorSerializer.is_valid():
            user, author = authorSerializer.update(authorSerializer.data, id_user)
            userSerializer = UserSerializer(user)
            return Response(userSerializer.data, status=status.HTTP_201_CREATED)
        print(authorSerializer.errors)

        return Response(authorSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""
class UserAPIView(APIView):
    def post(self, request):
        data = {k: v for k, v in request.data.items()}
        userSerializer = UserCreateSerailizer(data=request.data)
        
        if userSerializer.is_valid():
            try:
                user = User.objects.create_user(**request.data)
                serializer = UserSerializer(user)
            except IntegrityError as err:
                return Response({"message": "Cet email est déjà utilisé !"}, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(userSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        #if data is passed we set a filter

        print(kwargs)
        if(kwargs.get('user_id')):
            print('user_id')
            user = get_object_or_404(User, pk=kwargs['user_id'])
            serializer = UserSerializer(user, many=False)
        else:
            if(kwargs):
                authors = User.objects.filter(**kwargs)
            else:
                authors = User.objects.all()
            serializer = UserSerializer(authors, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        data = {k: v for k, v in request.data.items()}
        userSerializer = UserUpdateSerailizer(data=data)
        authorSerializer = AuthorSerializer(data=data)

        if userSerializer.is_valid() and authorSerializer.is_valid():
            data['username']=data['email']
            user = get_object_or_404(User, pk=data['user'])

            user.username = data['email']
            user.last_name = data['last_name']
            user.first_name = data['first_name']
            user.email = data['email']

            user.save()
            
            author = Author.objects.get(user=user)  
            if(author):
                author.adress = data['adress']
                author.contact = data['contact']
                author.institution = data['institution']
                author.aboutAuthor = data['aboutAuthor']
                author.save()
            else:
                author_data = {**authorSerializer.data, "user": user}
                Author.objects.create(**author_data)

            userSerializer = UserSerializer(user, many=False)
            return Response(userSerializer.data, status=status.HTTP_201_CREATED)
        
        if userSerializer.is_valid():
            return Response(userSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif authorSerializer.is_valid():
            return Response(authorSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
"""