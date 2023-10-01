from rest_framework.test import APITestCase
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from rest_framework import status
import json
from  review.models import Volume, Numero
from apiC2rlf.settings import BASE_URI_API_FOR_TEST

class TestNumero(APITestCase):
    URI = reverse_lazy('numero-list')
    def setUp(self):
        self.superuser = User.objects.create_superuser("bonheur@gmail.com", "bonheur@gmail.com", "1234")
        self.user = User.objects.create_user("chris@gmail.com", "chris@gmail.com", "1234")
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

    def test_create(self):
        numero_count_before = Numero.objects.count()
        #raise error if not admin
        self.client.force_authenticate(self.user)
        response = self.client.post(self.URI, data=self.numero_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        #no raise if admin and return 201
        self.client.force_authenticate(self.superuser)
        self.numero_data['volume'] = self.volume.id
        self.numero_data['number'] = 2
        response = self.client.post(self.URI, data=self.numero_data)
        numero_count_after = Numero.objects.count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(numero_count_before + 1, numero_count_after)

    def test_update(self):
        #raise error if not admin
        uri = f'{self.URI}{self.numero.id}/'
        self.numero_data['volume'] = self.volume.id
        self.numero_data['id'] = self.numero.id
        self.client.force_authenticate(self.user)
        response = self.client.put(uri, data=self.numero_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        #no raise if admin and return 201
        self.client.force_authenticate(self.superuser)
        response = self.client.put(uri, data=self.numero_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_format = json.loads(response.content.decode('utf-8'))
        self.assertEqual(json_format['number'], self.numero_data['number'])

    def test_delete(self):
        uri = f"{self.URI}{self.numero.id}/"
        self.client.force_authenticate(self.user)
        response = self.client.delete(uri)
        #raise 403 forbiden if no admin user
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        #delete if admin user
        self.client.force_authenticate(self.superuser)
        response = self.client.delete(uri)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_list(self):
        numero = self.numero#create numero by calling it on setup
        response = self.client.get(self.URI)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_filter(self):
        uri = reverse_lazy('numero-filter')
        self.numero_data = {
            "number": 1,
            "volume": self.volume.id
        }
        response = self.client.post(uri, data=self.numero_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_format = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(json_format), 1)

        

