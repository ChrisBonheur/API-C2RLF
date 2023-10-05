from rest_framework import serializers, status
from django.contrib.auth.models import User
from author.serializers import ListUserAuthorSerializer, UserAuthorSerializer
from review.serializers import Base64ToFieleField
from ouvrage.models import Category
from . models import Category, Ouvrage

class categorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

    def validate(self, attrs):
        catgories = Category.objects.filter(name=attrs['name'])
        if catgories.exists():
            raise serializers.ValidationError('Cette categorie existe déjà')
        return super().validate(attrs)

class OuvrageSerializer(serializers.ModelSerializer):
    author = ListUserAuthorSerializer()
    pdf_file = Base64ToFieleField()
    cover_image = Base64ToFieleField(required=False, allow_null=True)

    class Meta:
        model = Ouvrage
        exclude = ['date_creation', 'user']
    
    def create(self, validated_data):
        authors = validated_data.pop('author', None)
        validated_data['user'] = self.context['request'].user
        ouvrage = super().create(validated_data)
        for data in authors:
            user = User.objects.filter(email=data['email'])
            if not user.exists():
                author_serializer = UserAuthorSerializer(data=data)
                if author_serializer.is_valid():
                    user, author = author_serializer.create(author_serializer.data)
            else:
                user = user[0]
            ouvrage.author.add(user)
        return ouvrage
    
    def update(self, instance, validated_data):
        nesteed_authors = validated_data.pop('author', None)
        ouvrage = super().update(instance, validated_data)
        for data in nesteed_authors:
            user_in = User.objects.filter(email=data['email'])
            author_serializer = UserAuthorSerializer(data=data)
            if author_serializer.is_valid():
                if user_in.exists():
                    user = user_in[0]
                    user, author = author_serializer.update(author_serializer.data, user.id)
                else:
                    user, author = author_serializer.create(author_serializer.data)
            ouvrage.author.add(user)
        return ouvrage

class OuvrageSerializerList(serializers.ModelSerializer):
    class Meta:
        model = Ouvrage
        fields = ["title", 'id', 'year_parution', 'version']

class OuvrageRetrieveSerializer(serializers.ModelSerializer):
    author = ListUserAuthorSerializer()
    user = UserAuthorSerializer()
    
    class Meta:
        model = Ouvrage
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['category_retrieve'] = categorySerializer(instance.category).data
        data['author_retrieve'] = UserAuthorSerializer(instance.author, many=True).data
        return data