from rest_framework import serializers, status
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.core.files.base import ContentFile
from datetime import datetime
import base64
import uuid

from .models import Volume, Numero, Sommaire
from apiC2rlf.enum import RequestMethod

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
        if (number.exists() and request.method == RequestMethod.POST.value) or (request.method == RequestMethod.PUT.value and number[0].id != int(request.data['id'])):
            raise serializers.ValidationError(f"Ce nombre de numéro existe déjà pour le volume sélectioné ({volume.volume_year} n॰{volume.number}).")

        return super().validate(data)
    
class SommaireSerializer(serializers.ModelSerializer):
    pdf_file = Base64ToFieleField()
    picture = Base64ToFieleField(required=False, allow_null=True)

    class Meta:
        model = Sommaire
        fields = "__all__"

    def validate(self, attrs):
        request = self.context['request']
        numero = attrs['numero']
        sommaire = Sommaire.objects.filter(numero=numero)
        #verify conflict
        if (sommaire.exists() and request.method == RequestMethod.POST.value) or (request.method == RequestMethod.PUT.value and sommaire[0].id != int(request.data['id'])):
            raise serializers.ValidationError(f"Ce numéro est déjà lié au ({sommaire[0].label}.")
        
        return super().validate(attrs)
    

