from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from django.urls import reverse_lazy
from ouvrage.models import Category, Ouvrage
from author.base64_for_test import base64_file

class TestCategory(APITestCase):
    uri = reverse_lazy('category-ouvrage-list')

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='bonheur', email='bonheur@gmail.com', password='1234')
        self.superuser = User.objects.create_superuser(username='chris', email='chris@gmail.com', password='1234')
        self.category = Category.objects.create(**{'name': 'jeunesse'})

    def test_create_raise_error_if_no_admin(self):
        self.client.force_authenticate(self.user)
        #raise error if no superuser
        response = self.client.post(self.uri, data={'name': 'romans'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_by_superuser(self):
        self.client.force_authenticate(self.superuser)
        #create if superuser
        response = self.client.post(self.uri, data={'name': 'romans'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_raiser_error_if_no_superuser(self):
        self.client.force_authenticate(self.user)
        #create if superuser
        response = self.client.put(f'{self.uri}{self.category.id}/', data={'name': 'romans-two'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_by_superuser(self):
        self.client.force_authenticate(self.superuser)
        #create if superuser
        response = self.client.put(f'{self.uri}{self.category.id}/', data={'name': 'romans-two'})
        self.assertEqual(response.status_code, status.HTTP_200_OK) 


    def test_delete_raise_error_if_no_admin(self):
        self.client.force_authenticate(self.user)
        #raise error if no superuser
        response = self.client.delete(f"{self.uri}{self.category.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_if_admin(self):
        self.client.force_authenticate(self.superuser)
        #raise error if no superuser
        response = self.client.delete(f"{self.uri}{self.category.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_raise_error_if_conflict(self):
        self.client.force_authenticate(self.superuser)
        category = self.category
        Category.objects.create(**{'name': 'jeunesse'})
        response = self.client.post(self.uri, data={'name': 'jeunesse'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OuvrageTest(APITestCase):
    uri = reverse_lazy('ouvrage-list')

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='bonheur', email='bonheur@gmail.com', password='1234')
        self.superuser = User.objects.create_superuser(username='chris', email='chris@gmail.com', password='1234')
        self.category = Category.objects.create(**{'name': 'jeunesse'})
        self.ouvrage_data = {
            'title': 'La demeure des gouvernantes',
            'year_parution': '2024',
            'category': self.category,
            'presentation': 'Nouvel ouvrage',
            'pdf_file': base64_file,
            'version': '3',
            'edition': 'Maison ref',
        }
        self.ouvrage = Ouvrage.objects.create(**self.ouvrage_data)
        self.authors = [
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



    def test_create_raise_error_if_no_admin(self):
        self.client.force_authenticate(self.user)
        #raise error if no superuser
        response = self.client.post(self.uri, data=self.ouvrage_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_by_superuser(self):
        self.client.force_authenticate(self.superuser)
        #create if superuser
        self.ouvrage_data['category'] = self.category.id
        self.ouvrage_data['author'] = self.authors
        response = self.client.post(self.uri, data=self.ouvrage_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_raiser_error_if_no_superuser(self):
        self.client.force_authenticate(self.user)
        #create if superuser
        self.ouvrage_data['category'] = self.category.id
        response = self.client.put(f'{self.uri}{self.ouvrage.id}/', data=self.ouvrage_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_by_superuser(self):
        self.client.force_authenticate(self.superuser)
        #create if superuser
        self.ouvrage_data['category'] = self.category.id
        self.ouvrage_data['author'] = self.authors
        response = self.client.put(f'{self.uri}{self.ouvrage.id}/', data=self.ouvrage_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK) 


    def test_delete_raise_error_if_no_admin(self):
        self.client.force_authenticate(self.user)
        #raise error if no superuser
        response = self.client.delete(f"{self.uri}{self.ouvrage.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_if_admin(self):
        self.client.force_authenticate(self.superuser)
        #raise error if no superuser
        response = self.client.delete(f"{self.uri}{self.ouvrage.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_one_ouvrage(self):
        response = self.client.get(f"{self.uri}{self.ouvrage.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)