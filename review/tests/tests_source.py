from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from rest_framework import status
import json 

from review.models import TypeSource, Source
"""
class SourceTestCase(APITestCase):

    uri = reverse_lazy('source-list')

    def setUp(self):
        self.user = User.objects.create_user(username='bonheur', email='bonheur@gmail.com', password='1223')
        self.admin = User.objects.create_superuser(username='chris', email='chris@gmail.com', password='12344')

        self.type_source = TypeSource.objects.create(type_name="journal")

        self.source_data = {
            "authors": 'Darius Makeba; Milandu M',
            "title": "Au pays des loves",
            "city": "Pointe-noire",
            "year_publication": "2022",
            "editor": "Maison moralies",
            "type_source": self.type_source
        }
        self.source = Source.objects.create(**self.source_data)
    
    def test_create(self):
        self.client.force_authenticate(self.user)
        self.source_data['type_source'] = self.type_source.id
        response = self.client.post(self.uri, data=self.source_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update(self):
        type_source = TypeSource.objects.create(type_name='web')
        self.source_data = {
            "authors": 'Darius Makeba; Milandu; morizon',
            "title": "Au pays des loves 3",
            "city": "Pointe-noire 3",
            "year_publication": "2020",
            "editor": "Maison moralies3",
            "type_source": type_source.id
        }
        self.client.force_authenticate(self.user)
        response = self.client.put(f"{self.uri}{self.source.id}/", data=self.source_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_format = json.loads(response.content.decode('utf-8'))
        self.source_data['type_source'] = type_source
        [self.assertEqual(json_format[key], self.source_data[key]) for key in self.source_data.keys() if key != 'type_source']

    def test_delete(self):
        #if no admin delete
        self.client.force_authenticate(self.user)
        response = self.client.delete(f"{self.uri}{self.source.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get(self):
        #self.client.force_authenticate(self.admin)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

"""