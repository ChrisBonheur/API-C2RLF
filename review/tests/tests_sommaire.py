from rest_framework.test import APITestCase
from django.urls import reverse_lazy
from rest_framework import status
from django.contrib.auth.models import User
import json

from review.models import Sommaire, Volume, Numero
from author.base64_for_test import base64_file


class TestSommaire(APITestCase):
    URI = reverse_lazy('sommaire-list')
    def setUp(self):
        self.superuser =  User.objects.create_superuser(username="chris@gmail.com", email="chris@gmail.com", password="1234")
        self.user = User.objects.create(username="bonheur@gmail.com", email="bonheur@gmail.com", password="1234")
        self.user2 = User.objects.create(username="bonheur2@gmail.com", email="bonheur2@gmail.com", password="1234")
        self.volume = Volume.objects.create(**{
            "number": 1,
            "pages_number": 10,
            "volume_year": 2023,
        })
        self.numero_data = {
            "label": 'numero_1',
            "number": 1,
            "volume": self.volume
        }
        self.numero = Numero.objects.create(**self.numero_data)
        self.sommaire_data = {
            "title": "sommaire",
            "presentation": "presentation texte test",
            "numero": self.numero
        }

        self.sommaire = Sommaire.objects.create(**self.sommaire_data)
        self.sommaire.author.add(self.user)
        self.sommaire.author.add(self.user2)
        self.sommaire.save()

    def test_get_sommaire_list(self):
        sommaire = self.sommaire
        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_sommaire(self):
        numero_data = {
            "label": 'numero_2',
            "number": 2,
            "volume": self.volume
        }
        self.sommaire_data['pdf_file'] = base64_file
        self.sommaire_data['author'] = [
            {
                'username': "bonheur",
                'last_name': "maf",
                'first_name': "chris",
                'adress': 'rue',
                'institution': 'marien ngoubi',
                'aboutAuthor': 'je suis author',
                'email': 'chris@gmail.com',
                'password': '1234',
            },
            {
                'username': "bonheur2",
                'last_name': "maf2",
                'first_name': "chris2",
                'adress': 'rue2',
                'contact': '0683244332',
                'institution': 'marien ngoubi2',
                'aboutAuthor': 'je suis author2',
                'email': 'email@gmail.com2',
                'password': '12342',
            }
        ]
        numero = Numero.objects.create(**numero_data)
        self.sommaire_data['numero'] = numero.id
        #raise error if no superuser
        self.client.force_authenticate(self.user)
        response = self.client.post(self.URI, data=self.sommaire_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        #create with success for superuser
        sommaire_count_before = Sommaire.objects.count()
        self.client.force_authenticate(self.superuser)
        response = self.client.post(self.URI, data=self.sommaire_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(sommaire_count_before + 1, Sommaire.objects.count())


    def test_update_sommaire(self):
        sommaire_data = {
            "id": self.sommaire.id,
            "title": "sommaire2",
            "presentation": "presentation texte test2",
            "numero": self.numero.id,
            "author": [
            {
                'last_name': "mafdd",
                'first_name': "chris",
                'adress': 'rue',
                'contact': '068324433',
                'institution': 'marien ngoubi',
                'aboutAuthor': 'je suis author',
                'email': 'email@gmail.com',
                'password': '1234',
            },
            {
                'last_name': "maf2s",
                'first_name': "chris2",
                'adress': 'rue2',
                'contact': '0683244332',
                'institution': 'marien ngoubi2',
                'aboutAuthor': 'je suis author2',
                'email': 'email@gmail.com2',
                'password': '12342',
            }
            ],
            "pdf_file": base64_file
        }
        self.client.force_authenticate(self.user)
        #raise error if no admin
        response = self.client.put(f"{self.URI}{self.sommaire.id}/", data=sommaire_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        #update if asmin
        self.client.force_authenticate(self.superuser)
        #raise error if no admin
        response = self.client.put(f"{self.URI}{self.sommaire.id}/", data=sommaire_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_format = json.loads(response.content.decode('utf-8'))
        {self.assertEqual(json_format[key], sommaire_data[key]) for key in sommaire_data.keys() if key != 'pdf_file' and key != 'author' }
        
    def test_delete(self):
        #raise error if no admin
        self.client.force_authenticate(self.user)
        response = self.client.delete(f"{self.URI}{self.sommaire.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        #delete if admin
        self.client.force_authenticate(self.superuser)
        response = self.client.delete(f"{self.URI}{self.sommaire.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        

