from rest_framework import serializers, status
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from datetime import datetime
from django.contrib.auth.models import User
import base64
import uuid

from rest_framework.fields import empty

from .models import Reference ,Volume, Numero, Sommaire, TypeSource, Source, Article
from apiC2rlf.enum import ArticleState, RequestMethod
from author.serializers import ListUserAuthorSerializer, UserAuthorSerializer, UserSerializer

class Base64ToFieleField(serializers.FileField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if isinstance(data, str):
            # If the data is in base64 format, decode it and create a ContentFile
            try:
                format, imgstr = data.split(';base64,')  # Ensure that 'data' is prefixed by 'data:image/'
                ext = format.split('/')[-1]
                name = format.split('/')[-2]
                nowtime = datetime.now()
                nowtime = nowtime.strftime("%d-%m-%Y%H:%M%S")
                # Create a unique filename using a UUID
                filename = f"{uuid.uuid4()}.{ext}"

                data = ContentFile(base64.b64decode(imgstr), name=filename)
            except ValueError as e:
                #raise serializers.ValidationError("Ceci n'est pas un format base64 préfixé par 'data:image/'. ")
                return data

        return super(Base64ToFieleField, self).to_internal_value(data)

class VolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volume
        fields = '__all__'

    def validate(self, data):
        request = self.context['request']
        volume = Volume.objects.filter(volume_year=data['volume_year'])
        if volume.exists():
            if request.data.get('id') and request.method == RequestMethod.PUT.value:
                #verif if volume_year conflict is not for the same model
                if volume[0].id != request.data['id']:
                    raise serializers.ValidationError(f"Cette année est déjà utilisée pour le volume ayant le volume numéro '{volume[0].number}' .", code=status.HTTP_409_CONFLICT)
            else:
                raise serializers.ValidationError(f"Cette année est déjà utilisée dans le volume ayant le volume numéro '{volume[0].number}' .", code=status.HTTP_409_CONFLICT)

        volume = Volume.objects.filter(number=data['number'])
        if volume.exists():
            if request.data.get('id') and request.method == RequestMethod.PUT.value:
                #verif if numero conflict is not for the same model
                if volume[0].id != request.data['id']:
                    raise serializers.ValidationError(f"Ce numéro de volume est déjà utilisé dans le volume ayant l'année {volume[0].volume_year}.", code=status.HTTP_409_CONFLICT)
            else: 
                raise serializers.ValidationError(f"Ce numéro de volume est déjà utilisé dans le volume ayant l'année {volume[0].volume_year}.", code=status.HTTP_409_CONFLICT)
        
        return data    


class NumeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Numero
        fields = "__all__"

    def validate(self, data, *args, **kwargs):
        #check that number isn't exist in volume
        request = self.context['request']
        number = Numero.objects.filter(number=data['number'])
        if (number.exists() and request.method == RequestMethod.POST.value) or (request.method == RequestMethod.PUT.value and number.exists() and number[0].id != int(request.data['id'])):
            raise serializers.ValidationError(f"Ce nombre de numéro existe déjà.")

        return super().validate(data)
    
class NumeroRetrieveSerializer(serializers.ModelSerializer):
    volume = VolumeSerializer()

    class Meta:
        model = Numero
        fields = "__all__"
    
class NumeroSerializerList(serializers.ModelSerializer):
    class Meta:
        model = Numero
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['volume_label'] = f"Vol n॰{instance.volume.number} {instance.volume.volume_year}"
        return data
    
class SommaireSerializer(serializers.ModelSerializer):
    pdf_file = Base64ToFieleField()
    picture = Base64ToFieleField(required=False, allow_null=True)
    author = ListUserAuthorSerializer()

    class Meta:
        model = Sommaire
        fields = "__all__"

    def validate(self, attrs):
        request = self.context['request']
        
        numero = attrs['numero']
        sommaire = Sommaire.objects.filter(numero=numero)
        #verify conflict
        if (sommaire.exists() and request.method == RequestMethod.POST.value) or (request.method == RequestMethod.PUT.value and sommaire.exists() and sommaire[0].id != int(request.data['id'])):
            raise serializers.ValidationError(f"Ce numéro est déjà lié au ({sommaire[0].label}.")
        
        return super().validate(attrs)
    
    def create(self, validated_data):
        nesteed_authors = validated_data.pop('author', None)
        sommaire = Sommaire.objects.create(**validated_data)
        for data in nesteed_authors:
            user = User.objects.filter(email=data['email'])
            if not user.exists():
                author_serializer = UserAuthorSerializer(data=data)
                if author_serializer.is_valid():
                    user, author = author_serializer.create(author_serializer.data)
            else:
                user = user[0]
            sommaire.author.add(user)
        return sommaire
    
    def update(self, instance, validated_data):
        nesteed_authors = validated_data.pop('author', None)
        sommaire = super().update(instance, validated_data)
        for data in nesteed_authors:
            user_in = User.objects.filter(email=data['email'])
            author_serializer = UserAuthorSerializer(data=data)
            if author_serializer.is_valid():
                if user_in.exists():
                    user = user_in[0]
                    user, author = author_serializer.update(author_serializer.data, user.id)
                else:
                    user, author = author_serializer.create(author_serializer.data)
            sommaire.author.add(user)
        
        #remove not extisting author in new list authors
        emails_in_nesteed = [author['email'] for author in nesteed_authors]

        for email_obj in sommaire.author.values('email'):
            if not email_obj['email'] in emails_in_nesteed:
                #import pdb;pdb.set_trace()
                author_to_rmv = User.objects.get(email=email_obj['email'])
                sommaire.author.remove(author_to_rmv)
        return sommaire
    

class SommaireSerializerList(serializers.ModelSerializer):

    class Meta:
        model = Sommaire
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['numero_ordre'] = instance.numero.number
        return data


class TypeSourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = TypeSource
        fields = "__all__"

    def validate(self, attrs):
        request = self.context['request']
        type_name = attrs['type_name']
        type_elt = TypeSource.objects.filter(type_name=type_name)
        #import pdb; pdb.set_trace()
        #verify conflict
        if (type_elt.exists() and request.method == RequestMethod.POST.value) or (request.method == RequestMethod.PUT.value and type_elt.exists() and type_elt[0].id != int(request.data['id'])):
            raise serializers.ValidationError(f"Ce type de source existe déjà.")
        
        return super().validate(attrs)
    

class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(instance, Source):
            if instance.type_source:
                data['type_source_name'] = instance.type_source.type_name
        return data

class ReferenceSerializer(serializers.ModelSerializer):
    source = SourceSerializer()
    class Meta:
        model = Reference
        fields = '__all__'

class ListReferenceSerializer(serializers.ListSerializer):
    child = ReferenceSerializer()

class ArticleSerializer(serializers.ModelSerializer):
    authors = ListUserAuthorSerializer()
    file_submit = Base64ToFieleField(required=False, allow_null=True)
    pdf_file = Base64ToFieleField(required=False, allow_null=True)
    references = ListReferenceSerializer(required=False)

    class Meta:
        model = Article
        fields = '__all__'

    def create(self, validated_data):
        
        nesteed_authors = validated_data.pop('authors', None)
        nesteed_references = validated_data.pop('references', None)
        article = Article.objects.create(**validated_data)
        for data in nesteed_authors:
            user = User.objects.filter(email=data['email'])
            if not user.exists():
                author_serializer = UserAuthorSerializer(data=data)
                if author_serializer.is_valid():
                    user, author = author_serializer.create(author_serializer.data)
            else:
                user = user[0]
            article.authors.add(user)
        
        if nesteed_references:
            for data in nesteed_references:
                source = Source.objects.create(**data['source'])
                data['source'] = source
                reference = Reference.objects.create(**data)
                article.references.add(reference)
        return article
    
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        article = instance
        if (user == article.user and article.state == ArticleState.INITIALISATION.value) or user.is_superuser:
            nesteed_authors = validated_data.pop('authors', None)
            nesteed_references = validated_data.pop('references', None)
            #validated_data['user'] = get_object_or_404(User, pk=validated_data['user'])
            #if validated_data.get('numero'):
                #validated_data['numero'] = get_object_or_404(Numero, pk=validated_data['numero'])
            
            article = super().update(instance, validated_data)
            for data in nesteed_authors:
                user_in = User.objects.filter(email=data['email'])
                author_serializer = UserAuthorSerializer(data=data)
                if author_serializer.is_valid():
                    if user_in.exists():
                        user = user_in[0]
                        user, author = author_serializer.update(author_serializer.data, user.id)
                    else:
                        user, author = author_serializer.create(author_serializer.data)
                article.authors.add(user)
            
            #remove not extisting author in new list authors
            emails_in_nesteed = [author['email'] for author in nesteed_authors]

            for email_obj in article.authors.values('email'):
                if not email_obj['email'] in emails_in_nesteed:
                    #import pdb;pdb.set_trace()
                    author_to_rmv = User.objects.get(email=email_obj['email'])
                    article.authors.remove(author_to_rmv)

            #remove old:
            for data in article.references.all():
                article.references.remove(data)

            if nesteed_references:
                for data in nesteed_references:
                    source = Source.objects.create(**data['source'])
                    data['source'] = source
                    reference = Reference.objects.create(**data)
                    article.references.add(reference)
            return article
        raise PermissionDenied("Vous n'avez pas l'abilitation requise pour effectuer cette action.", code=status.HTTP_403_FORBIDDEN)
    

class UserListSerializer(serializers.ListSerializer):
    child = UserSerializer()


class ArticleSerializerViewOne(serializers.ModelSerializer):
    user = UserSerializer()
    authors = UserListSerializer()
    numero = NumeroRetrieveSerializer()
    references = ListReferenceSerializer()
    file_submit = Base64ToFieleField(required=False, allow_null=True)
    pdf_file = Base64ToFieleField(required=False, allow_null=True)
    class Meta:
        model = Article
        fields = '__all__'


    
class ArticleSerializerList(serializers.ModelSerializer):
    authors = ListUserAuthorSerializer()
    class Meta:
        model = Article
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.numero:
            data['numero_ordre'] = instance.numero.number
        if instance.page_begin and instance.page_end:
            data['interval_page'] = f"{instance.page_begin}-{instance.page_end}"
        return data
    
class statisitiqueSerializer(serializers.Serializer):
    numero = serializers.IntegerField()
    sommaire = serializers.IntegerField()
    article_init = serializers.IntegerField()
    article_parution = serializers.IntegerField()
    article_publication = serializers.IntegerField()
    cours_pdf = serializers.IntegerField()
    authors_active = serializers.IntegerField()
    ouvrage = serializers.IntegerField()