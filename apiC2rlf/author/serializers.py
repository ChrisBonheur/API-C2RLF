from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Author


class UserAuthorSerializer(Serializer):
    username = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    first_name = serializers.CharField(max_length=50)
    adress = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    contact = serializers.CharField(max_length=25, required=False)
    institution = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    aboutAuthor = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
    email = serializers.EmailField()
    password = serializers.CharField()
    photo = serializers.FileField(required=False, allow_null=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet e-mail est déjà utilisé.")
        return value

    def create(self, validated_data):
        photo = validated_data['photo'] if validated_data.get('photo') else ""
        user = User.objects.create_user(
            username=validated_data['username'],
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
            aboutAuthor=validated_data['aboutAuthor'],
            photo=photo
        )

        return user, author
    
    def update(self, validated_data, pk: int):
        user = get_object_or_404(User, pk=pk)
        user.username=validated_data['username']
        user.email=validated_data['email']
        user.password=validated_data['password']
        user.last_name=validated_data['last_name']
        user.first_name=validated_data['first_name']

        author = get_object_or_404(Author, user=user)
        author.adress=validated_data['adress']
        author.contact=validated_data['contact']
        author.institution=validated_data['institution']
        author.adress=validated_data['adress']
        author.aboutAuthor=validated_data['aboutAuthor']
        if validated_data.get('photo'):
            author.photo = validated_data.get('photo')

        user.save()
        author.save()

        return user, author

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