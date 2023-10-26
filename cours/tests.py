from rest_framework.test import APITestCase
from django.urls import reverse_lazy
from rest_framework import status
from django.contrib.auth.models import User
from apiC2rlf.utils import decode_response_to_json
from .models import Level, Course
from author.base64_for_test import base64_file

class LevelTest(APITestCase):
    url = reverse_lazy('level-list')

    def setUp(self):
        self.user = User.objects.create_user(username='bonheur', email='bonheur@gmail.com', password='1234')
        self.superuser = User.objects.create_superuser(username='chris', email='chris@gmail.com', password='1234')

        self.level_data = {
            'label': 'Licence',
            'code': 'LC',
            'order': 1
        }

    def test_simple_user_cant_create(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, self.level_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_by_admin(self):
        current_count_level = Level.objects.count()
        self.client.force_authenticate(self.superuser)
        response = self.client.post(self.url, self.level_data)
        current_count_level_after = Level.objects.count()
        self.assertEqual(current_count_level + 1, current_count_level_after)
        json_format = decode_response_to_json(response)
        [self.assertEqual(json_format[key], self.level_data[key]) for key in self.level_data.keys()]

    def test_simple_user_cant_update(self):
        self.client.force_authenticate(self.user)
        response = self.client.put(self.url + '1/', self.level_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_by_admin(self):
        level = Level.objects.create(**self.level_data)
        self.client.force_authenticate(self.superuser)
        response = self.client.put(f"{self.url}{level.id}/", self.level_data)
        json_format = decode_response_to_json(response)
        [self.assertEqual(json_format[key], self.level_data[key]) for key in self.level_data.keys()]  

    def test_delete_raise_error_if_simple_user(self):
        level = Level.objects.create(**self.level_data)
        self.client.force_authenticate(self.user)
        response = self.client.delete(f"{self.url}{level.id}/", self.level_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_by_admin(self):
        level = Level.objects.create(**self.level_data)
        current_count_level = Level.objects.count()
        self.client.force_authenticate(self.superuser)
        response = self.client.delete(f"{self.url}{level.id}/", self.level_data)
        current_count_level_after = Level.objects.count()
        self.assertEqual(current_count_level - 1, current_count_level_after)

    def test_get_public(self):
        level = Level.objects.create(**self.level_data)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_raise_error_if_conflict_of_code(self):
        level_data = {
            'label': 'Licence',
            'code': 'LC',
            'order': 1
        }
        level = Level.objects.create(**level_data)
        self.client.force_authenticate(self.superuser)
        response = self.client.post(self.url, level_data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)


class CourseTestCase(APITestCase):
    url = reverse_lazy('course-list')

    def setUp(self):
        self.user = User.objects.create_user(username='bonheur', email='bonheur@gmail.com', password='1234')
        self.superuser = User.objects.create_superuser(username='chris', email='chris@gmail.com', password='1234')
        self.level_data = {
            'label': 'Licence',
            'code': 'LC',
            'order': 1
        }
        self.level = Level.objects.create(**self.level_data)
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
        self.course_data = {
            "title": 'Histoire de Grant',
            "presentation": 'Grant fut le pere...', 
            "pdf_file": base64_file, 
            "is_public": False,    
        }
        self.course = Course.objects.create(**self.course_data)
        self.course_data['authors'] = self.authors
        self.course_data['level'] = [self.level.id]

    def test_create_raise_error_if_no_super_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, self.course_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_by_admin(self):
        count_before = Course.objects.count()
        self.client.force_authenticate(self.superuser)
        response = self.client.post(self.url, self.course_data, format='json')
        count_after = Course.objects.count()
        self.assertEqual(count_before + 1, count_after)

    def test_raise_update_if_no_admin(self):
        self.client.force_authenticate(self.user)
        response = self.client.put(f"{self.url}{self.course.id}/", self.course_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_by_admin(self):
        self.client.force_authenticate(self.superuser)
        response = self.client.put(f"{self.url}{self.course.id}/", data=self.course_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_raise_error_if_no_admin(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(f"{self.url}{self.course.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_delete_by_admin(self):
        course = self.course
        count_before = Course.objects.count()
        self.client.force_authenticate(self.superuser)
        response = self.client.delete(f"{self.url}{course.id}/")
        count_after = Course.objects.count()
        self.assertEqual(count_before - 1, count_after)