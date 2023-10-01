from rest_framework.test import APITestCase
from django.urls import reverse_lazy
from rest_framework import status
from django.contrib.auth.models import User;
import json

from review.models import TypeSource

class TestTypeSource(APITestCase):

    uri = reverse_lazy('type_source-list')
    
    def setUp(self):
        self.type_source = TypeSource.objects.create(type_name='Journal')
        self.user = User.objects.create_superuser(username="bonheur@gmail.com", email="bonheur@gmail.com", password="1234")
        self.type_data = {
            "type_name": "Livre"
        }

    def test_create(self):
        before_create = TypeSource.objects.count()
        uri = self.uri
        self.client.force_authenticate(self.user)
        response = self.client.post(uri, data=self.type_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(before_create + 1, TypeSource.objects.count())
        #raise error if doublon
        response = self.client.post(uri, data=self.type_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        self.client.force_authenticate(self.user)
        response = self.client.put(f"{self.uri}{self.type_source.id}/", data={"type_name": "brouchure"})
        jsonFormat = json.loads(response.content.decode('utf-8'))
        self.assertEqual(jsonFormat['type_name'], "brouchure")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(f"{self.uri}{self.type_source.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
