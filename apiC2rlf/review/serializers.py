from rest_framework import serializers, status
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.core.files.base import ContentFile
from datetime import datetime
from django.contrib.auth.models import User
import base64
import uuid

from rest_framework.fields import empty

from .models import Volume, Numero, Sommaire, TypeSource
from apiC2rlf.enum import RequestMethod
from author.serializers import ListUserAuthorSerializer, UserAuthorSerializer

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
                raise serializers.ValidationError("Ceci n'est pas un format base64 préfixé par 'data:image/'. ")

        return super(Base64ToFieleField, self).to_internal_value(data)

class VolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volume
        fields = '__all__'

    def validate_volume_year(self, value):
        volume = Volume.objects.filter(volume_year=value)
        if volume.exists():
            raise serializers.ValidationError(f"Cette année est déjà utilisé pour le volume ayant le volume numéro '{volume[0].number}' .", code=status.HTTP_409_CONFLICT)
        return value
    
    def validate_number(self, value):
        volume = Volume.objects.filter(number=value)
        if volume.exists():
            raise serializers.ValidationError(f"Ce numéro de volume est déjà utilisé dans le volume ayant l'année {volume[0].volume_year}.", code=status.HTTP_409_CONFLICT)
        return value
    

class VolumeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volume
        fields = '__all__'

    def update(self, instance, validated_data):
        volume = Volume.objects.filter(volume_year=validated_data['volume_year'])
        #verification if conflict that is already used (not by the same object)
        if volume.exists() and instance.id != volume[0].id:
            raise serializers.ValidationError(f"Cette année est déjà utilisé pour le volume ayant le numéro '{volume[0].number}' .", code=status.HTTP_409_CONFLICT)
        
        volume = Volume.objects.filter(number=validated_data['number'])
        if volume.exists() and instance.id != volume[0].id:
            raise serializers.ValidationError(f"Ce numéro est déjà utilisé dans le volume ayant l'année {volume[0].volume_year}.", code=status.HTTP_409_CONFLICT)

        return super().update(instance, validated_data)
    

class NumeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Numero
        fields = "__all__"

    def validate(self, data, *args, **kwargs):
        #check that number isn't exist in volume
        request = self.context['request']
        number = Numero.objects.filter(number=data['number'], volume=data['volume'])
        volume = data['volume']
        if (number.exists() and request.method == RequestMethod.POST.value) or (request.method == RequestMethod.PUT.value and number.exists() and number[0].id != int(request.data['id'])):
            raise serializers.ValidationError(f"Ce nombre de numéro existe déjà pour le volume ({volume.volume_year} n॰{volume.number}).")

        return super().validate(data)
    
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
            sommaire.author.add(user)
        return sommaire
    
    def update(self, instance, validated_data):
        nesteed_authors = validated_data.pop('author', None)
        sommaire = super().update(instance, validated_data)
        for data in nesteed_authors:
            user = User.objects.filter(email=data['email'])
            author_serializer = UserAuthorSerializer(data=data)
            if author_serializer.is_valid():
                if user.exists():
                    user, author = author_serializer.update(author_serializer.data)
                else:
                    user, author = author_serializer.create(author_serializer.data)
            sommaire.author.add(user)
        return sommaire
    

class SommaireSerializerList(serializers.ModelSerializer):

    class Meta:
        model = Sommaire
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['numero_ordre'] = instance.numero.number
        return data
    
    # Définissez la documentation pour l'attribut supplémentaire
    extra_attribute = serializers.CharField(
        help_text="Ceci est l'attribut supplémentaire ajouté manuellement."
    )

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
    