from rest_framework import serializers
from review.serializers import Base64ToFieleField
from . models import PageContent

class PageSerializer(serializers.ModelSerializer):
    pdf_file = Base64ToFieleField(required=False, allow_null=True)
    class Meta:
        model = PageContent
        fields = "__all__"