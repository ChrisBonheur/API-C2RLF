from rest_framework import serializers, status
from .models import Volume


class VolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volume
        fields = '__all__'

    def validate_volume_year(self, value):
        volume = Volume.objects.filter(volume_year=value)
        if volume.exists():
            raise serializers.ValidationError(f"Cette année est déjà utilisé pour le volume ayant le numéro '{volume[0].number}' .", code=status.HTTP_409_CONFLICT)
        return value
    
    def validate_number(self, value):
        volume = Volume.objects.filter(number=value)
        if volume.exists():
            raise serializers.ValidationError(f"Ce numéro est déjà utilisé dans le volume ayant l'année {volume[0].volume_year}.", code=status.HTTP_409_CONFLICT)
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