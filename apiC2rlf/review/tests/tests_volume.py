from rest_framework.test import APITestCase
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from rest_framework import status
import json
from  review.models import Volume
from apiC2rlf.settings import BASE_URI_API_FOR_TEST

class TestVolume(APITestCase):
    URI = reverse_lazy('volume-list')

    def setUp(self) -> None:
        self.superuser = User.objects.create_superuser("bonheur@gmail.com", "bonheur@gmail.com", "1234")
        self.user = User.objects.create_user("chris@gmail.com", "chris@gmail.com", "1234")
        self.volume = {
            "number": 1,
            "pages_number": 10,
            "volume_year": 2023,
        }
    
    def test_raise_err_create_if_no_super_user(self):
        response = self.client.post(self.URI, data=self.volume)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_create(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(self.URI, data=self.volume)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_list_volume(self):
        Volume.objects.create(**self.volume)
        all_volume = Volume.objects.all()
        response = self.client.get(self.URI, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jsonFormat = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(jsonFormat['results']), len(all_volume))

    def test_update(self):
        volume = Volume.objects.create(**self.volume)
        self.volume['pages_number'] = 20
        self.volume['number'] = 2
        self.volume['volume_year'] = 2023
        self.client.force_authenticate(user=self.superuser)
        response = self.client.put(f'{BASE_URI_API_FOR_TEST}api/volume/{volume.id}/', data=self.volume)
        jsonFormat = json.loads(response.content.decode('utf-8'))
        self.assertEqual(jsonFormat['pages_number'], self.volume['pages_number'])
        self.assertEqual(jsonFormat['number'], self.volume['number'])
        self.assertEqual(jsonFormat['volume_year'], self.volume['volume_year'])

    def test_raise_err_if_no_admin(self):
        volume = {
            "number": 2,
            "pages_number": 23,
            "volume_year": 2025,
        }
        volume = Volume.objects.create(**volume)
        self.client.force_authenticate(self.user)
        response = self.client.put(f'{BASE_URI_API_FOR_TEST}api/volume/{volume.id}/', data=self.volume)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(self.superuser)

    def test_delete(self):
        volume = {
            "number": 6,
            "pages_number": 23,
            "volume_year": 2026,
        }
        count_before = Volume.objects.count()
        volume = Volume.objects.create(**volume)
        count_after = Volume.objects.count()
        self.client.force_authenticate(self.superuser)

        response = self.client.delete(f'{BASE_URI_API_FOR_TEST}api/volume/{volume.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(count_before, count_after - 1)
        