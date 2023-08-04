#from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import json

from .serializers import UserSerializer, AuthorSerializer
from .models import Author

class AuthorAPIView(APIView):

    def post(self, request, id_user):
        data = {k: v for k, v in request.data.items()}
        user = get_object_or_404(User, pk=id_user)
        print(user)
        authorSerializer = AuthorSerializer(data=data)

        if authorSerializer.is_valid():
            author = Author.objects.create(**data, user=user)
            serializer = AuthorSerializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(authorSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAPIView(APIView):
    def post(self, request):
        data = {k: v for k, v in request.data.items()}
        userSerializer = UserSerializer(data=data)
        
        if userSerializer.is_valid():
            user = User.objects.create_user(data)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(userSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        authors = User.objects.all()
        serializer = UserSerializer(authors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        data = {k: v for k, v in request.data.items()}
        userSerializer = UserSerializer(data=data)
        authorSerializer = AuthorSerializer(data=data)
        
        if userSerializer.is_valid() and authorSerializer.is_valid():
            user = User.objects.create_user()
            author = Author.objects.create(user=user)
            userSerializer = AuthorSerializer(author)
            return Response(userSerializer.data, status=status.HTTP_201_CREATED)
        
        if userSerializer.is_valid():
            return Response(userSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif authorSerializer.is_valid():
            return Response(authorSerializer.errors, status=status.HTTP_400_BAD_REQUEST)