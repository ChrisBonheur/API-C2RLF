import base64
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile

from .models import Author


class UserAuthorSerializer(Serializer):
    username = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)
    id = serializers.IntegerField(required=False, allow_null=True)
    last_name = serializers.CharField(max_length=50)
    first_name = serializers.CharField(max_length=50)
    adress = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    contact = serializers.CharField(max_length=25, required=False, allow_null=True, allow_blank=True)
    institution = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    aboutAuthor = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
    email = serializers.EmailField()
    password = serializers.CharField(required=False, allow_null=True, allow_blank=True, default='1234')
    photo = serializers.CharField(required=False, allow_null=True, allow_blank=True, write_only=False)

    def create(self, validated_data):
        if User.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError("Cet e-mail est déjà utilisé.")
        photo = validated_data['photo'] if validated_data.get('photo') else ""
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            last_name=validated_data['last_name'],
            first_name=validated_data['first_name'],
        )

        author = Author.objects.create(
            user=user,
            adress=validated_data['adress'],
            contact=validated_data['contact'],
            institution=validated_data['institution'],
            aboutAuthor=validated_data['aboutAuthor']
        )

        return user, author
    
    def update(self, validated_data, pk: int):
        user = get_object_or_404(User, pk=pk)
        user.username=validated_data['email']
        user.email=validated_data['email']
        user.last_name=validated_data['last_name']
        user.first_name=validated_data['first_name']

        author = Author.objects.get_or_create(user=user)[0]

        author.adress= validated_data['adress'] if validated_data.get('adress') else ""
        author.contact=validated_data['contact'] if validated_data.get('contact') else ""
        author.institution=validated_data['institution'] if validated_data.get('institution') else "" 
        author.adress=validated_data['adress'] if validated_data.get('adress') else ""
        author.aboutAuthor=validated_data['aboutAuthor'] if validated_data.get('aboutAuthor') else ""
        
        if validated_data.get('photo'):
            try:
                format, img_str = validated_data['photo'].split(';base64,')
                extension = format.split('/')[-1]
                author.photo.save(f'{user.last_name}_{user.id}.{extension}', ContentFile(base64.b64decode(img_str)))
            except ValueError as e:
                pass
        
        user.save()
        author.save()

        #import pdb;pdb.set_trace();
        return user, author
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        author = Author.objects.filter(user__id=data['id'])
        if author.exists() and author[0].photo:
            data['photo'] = author[0].photo.url
        return data

class AuthorSerializer(ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class UserListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']

class UserSerializer(ModelSerializer):
    author = AuthorSerializer()
    class Meta:
        model = User
        fields = '__all__'


class ListUserAuthorSerializer(serializers.ListSerializer):
    child = UserAuthorSerializer()