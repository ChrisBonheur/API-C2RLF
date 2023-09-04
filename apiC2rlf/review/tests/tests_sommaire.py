from rest_framework.test import APITestCase
from django.urls import reverse_lazy
from rest_framework import status
from django.contrib.auth.models import User

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
            "label": "sommaire du numero 1",
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
        self.sommaire_data['author'] = [
            self.user.id,
            self.user2.id
        ]
        numero = Numero.objects.create(**numero_data)
        self.sommaire_data['numero'] = numero.id
        self.sommaire_data['pdf_file'] = base64_file
        #raise error if no superuser
        self.client.force_authenticate(self.user)
        response = self.client.post(self.URI, data=self.sommaire_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        #create with success for superuser 
        self.client.force_authenticate(self.superuser)
        response = self.client.post(self.URI, data=self.sommaire_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_sommaire(self):
        pass


