from rest_framework import serializers
from .models import Level, Course
from review.serializers import Base64ToFieleField
from author.serializers import UserAuthorSerializer
from django.contrib.auth.models import User

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = "__all__"


class CourCreateOrUpdateSerializer(serializers.ModelSerializer):
    cover_image = Base64ToFieleField(required=False, allow_null=True)
    pdf_file = Base64ToFieleField()
    authors = UserAuthorSerializer(many=True)

    class Meta:
        model = Course
        exclude = ['date_creation', 'cover_image_min']

    def create(self, validated_data):
        authors = validated_data.pop('authors', None)
        validated_data['user'] = self.context['request'].user
        course = super().create(validated_data)
        for data in authors:
            user = User.objects.filter(email=data['email'])
            if not user.exists():
                author_serializer = UserAuthorSerializer(data=data)
                if author_serializer.is_valid():
                    user, author = author_serializer.create(author_serializer.data)
            else:
                user = user[0]
            course.authors.add(user)
        return course
    
    def update(self, instance, validated_data):
        nesteed_authors = validated_data.pop('authors', None)
        course = super().update(instance, validated_data)
        for data in nesteed_authors:
            user_in = User.objects.filter(email=data['email'])
            author_serializer = UserAuthorSerializer(data=data)
            if author_serializer.is_valid():
                if user_in.exists():
                    user = user_in[0]
                    user, author = author_serializer.update(author_serializer.data, user.id)
                else:
                    user, author = author_serializer.create(author_serializer.data)
            course.authors.add(user)
        return course
    

    

class CourseListSerializer(serializers.ModelSerializer):
    authors = UserAuthorSerializer(many=True)
    class Meta:
        model = Course
        fields = ['title', 'cover_image_min', 'date_creation', 'cover_image_min', 'id', 'authors', 'presentation', 'date_creation']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        if instance.level:
            data['level_codes'] = ', '.join([f'{level.code}' for level in instance.level.all()])
        if instance.cover_image:
            data['cover_image'] = request.build_absolute_uri(instance.cover_image.url)
        if instance.cover_image_min:
            data['cover_image_min'] = request.build_absolute_uri(instance.cover_image_min.url)
        return data
    

class CourseRetrieveSerializer(serializers.ModelSerializer):
    authors = UserAuthorSerializer(many=True)

    class Meta:
        model = Course
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.level:
            data['level_codes'] = ', '.join([f'{level.label}' for level in instance.level.all()])
            data['level_retrieve'] = LevelSerializer(instance.level.all(), many=True).data
        return data

class CourseFilterSerializer(serializers.ModelSerializer):
    levels_id = serializers.IntegerField(required=False, allow_null=True)
