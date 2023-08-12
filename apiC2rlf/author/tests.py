from django.urls import reverse_lazy, reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .views import AuthorAPIView
import json

from author.models import Author

class TestAuthor(APITestCase):
    uri = 'author'
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(email='bonheur@gmail.com', password='1234', username='bonheur')
        self.author_data = {
            "username": "Bonheurs",
            "last_name": "mafoundou",
            "first_name": "bonheur",
            "email": "bonheuar@gmail.com",
            "password": "1234",
            "adress": '102 rue de test',
            "contact": '068314433',
            "institution": 'dev',
            "aboutAuthor": 'me and me'
        }


    def test_create_and_update_author(self):
        author_data = self.author_data
        response = self.client.post(reverse_lazy(viewname='author'), data=author_data, format='json')

        self.assertEqual(response.status_code, 201)

        user = json.loads(response.content.decode('utf-8'))
        self.assertEqual(user['author']['aboutAuthor'], self.author_data['aboutAuthor'])
        self.assertEqual(user['username'], self.author_data['username'])
        #update 
        photo_file = SimpleUploadedFile("../test_photo.jpg", b"file_content", content_type="image/jpeg")
        author_data = {
            "username": "Bonheurs2",
            "last_name": "mafoundou2",
            "first_name": "bonheur2",
            "email": "bonheuar@gmail.com2",
            "password": "1234",
            "adress": '102 rue de test2',
            "contact": '0683144332',
            "institution": 'dev2',
            "aboutAuthor": 'me and me2',
        }
        response = self.client.put(reverse_lazy(viewname='author_one', args=[user['id'],]), data=author_data, format='json')

        self.assertEqual(response.status_code, 201)

        user = json.loads(response.content.decode('utf-8'))
        self.assertEqual(user['author']['aboutAuthor'], author_data['aboutAuthor'])
        self.assertEqual(user['username'], author_data['username'])
        self.assertEqual(user['last_name'], author_data['last_name'])
        self.assertEqual(user['first_name'], author_data['first_name'])
        self.assertEqual(user['email'], author_data['email'])
        self.assertEqual(user['author']['adress'], author_data['adress'])
        self.assertEqual(user['author']['contact'], author_data['contact'])
        self.assertEqual(user['author']['institution'], author_data['institution'])


    def test_login(self):
        data = {
            "username": self.user.username,
            "password": '1234'
        }
        response = self.client.post(reverse_lazy('token_obtain_pair'), data=data)
        self.assertEqual(response.status_code, 200)

    """get data for login user
        """
    def test_get_login_user(self):
        #test with unlogin user
        url = reverse_lazy('author')
        req = self.client.get(url, {'user_id': self.user.id})
        req_to_json = json.loads(req.content.decode('utf-8'))
        #return 401 unthorized if user not login
        self.assertEqual(req.status_code, status.HTTP_401_UNAUTHORIZED)

        #test with login user
        self.client.force_authenticate(user=self.user)
        req = self.client.get(url, {'user_id': self.user.id})
        req_to_json = json.loads(req.content.decode('utf-8'))
        self.assertEqual(self.user.username, req_to_json['username'])
        #test raise error if user not logi
        #self.assertRaises

    def test_get_users_by_super_user(self):
        #raise 401 if no login
        req = self.client.get(reverse_lazy('author'))
        self.assertEqual(req.status_code, status.HTTP_401_UNAUTHORIZED)
        #raise 401 login but not superuser
        self.client.force_authenticate(self.user)
        req = self.client.get(reverse_lazy('author'))
        self.assertEqual(req.status_code, status.HTTP_401_UNAUTHORIZED)

        super_user = User.objects.create_superuser(username='chris', email='chris@gmail.com', password='1234')
        #test get all users by superuser
        self.client.force_authenticate(super_user)
        req = self.client.get(reverse_lazy('author'))
        req_json = json.loads(req.content.decode('utf-8'))
        self.assertEqual(req.status_code, status.HTTP_200_OK)
        self.assertIsInstance(req_json, list)

        #test get one user by superuser
        req = self.client.get(reverse_lazy(viewname='author_one', args=(self.user.id,)))
        req_json = json.loads(req.content.decode('utf-8'))
        self.assertEqual(req_json['username'], self.user.username)
        self.assertNotIsInstance(req_json, list)
