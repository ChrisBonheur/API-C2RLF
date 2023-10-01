from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from author.base64_for_test import base64_file
from rest_framework import status
from django.urls import reverse_lazy
import json

from . models import PageContent

class TestPageContent(APITestCase):
    uri =  reverse_lazy('page-list')

    def setUp(self):
        self.user = User.objects.create_superuser(username='bonheur', email='bonheur@gmail.com', password='1234')
        self.page_data = {
            "title": "liens institutitionel",
            "content": "comntenuybjks ",
            "pdf_file": base64_file
        }
        self.page = PageContent.objects.create(**self.page_data)
    
    def test_create(self):
        self.page_data['title'] = "liens "
        page_count_before = PageContent.objects.count()
        self.client.force_authenticate(self.user)
        response = self.client.post(self.uri, self.page_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PageContent.objects.count(), page_count_before + 1)

    def test_update(self):
        self.page_data = {
            "title": "liens institutitioneldd",
            "content": "comntenuybjks dd",
            "pdf_file": base64_file
        }
        self.client.force_authenticate(self.user)
        response = self.client.put(f'{self.uri}{self.page.id}/', self.page_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res_json = json.loads(response.content.decode('utf-8'))
        [self.assertEqual(self.page_data[key], self.page_data[key]) for key in self.page_data.keys() if key != "page_title"]

    def test_delete(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(f'{self.uri}{self.page.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)  

    def test_get(self):
        response = self.client.get(reverse_lazy('pages_list-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
