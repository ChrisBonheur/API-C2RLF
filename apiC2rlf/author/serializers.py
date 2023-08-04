from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User

from .models import Author

class AuthorSerializer(ModelSerializer):
    class Meta:
        model = Author
        fields = ['adress', 'contact', 'institution', 'aboutAuthor', 'photo']


class UserSerializer(ModelSerializer):
    author = AuthorSerializer()
    class Meta:
        model = User
        fields = '__all__'

