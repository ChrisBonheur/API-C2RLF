from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from rest_framework import status
import json
from apiC2rlf.enum import *

from review.models import Article, Numero, Volume, TypeSource, Reference, Source
from author.base64_for_test import base64_file

class TestArticle(APITestCase):
    URI = reverse_lazy('article-list')
    PUBLIC_URI = reverse_lazy('articles_list-list')

    def setUp(self):
        self.volume = Volume.objects.create(**{
            "number": 1,
            "pages_number": 10,
            "volume_year": 2023,
        })
        self.superuser =  User.objects.create_superuser(username="chris@gmail.com", email="chris@gmail.com", password="1234")
        self.user = User.objects.create(username="bonheur@gmail.com", email="bonheur@gmail.com", password="1234")
        self.user2 = User.objects.create(username="bonheur2@gmail.com", email="bonheur2@gmail.com", password="1234")
        self.type_source = TypeSource.objects.create(type_name="journal")
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

        self.numero_data = {
            "label": 'numero_1',
            "number": 1,
            "volume": self.volume
        }
        self.numero = Numero.objects.create(**self.numero_data)
        self.article_data = {
            "title_fr": "article titre fr",
            "title_ang": "article titre ang",
            "abstract_fr": "abstract_fr titre fr",
            "numero": self.numero,
            "keywords_fr": "keywords_fr titre fr",
            "keywords_ang": "keywords_ang titre fr",
            "page_begin": 1,
            "page_end": 10,
            "doi_link": "doi_link",
            "orcid_link": "orcid_link",
            "user": self.user,
        }
        
        self.source_data = {
            "authors": "Bonheur Mafoundou; George Rodrigues",
            "title": "Le bonheur parfait",
            "city": "Brazzaville",
            "year_publication": "2022",
            "editor": "brazza info du dernier",
            "type_source": self.type_source
        }
        self.source = Source.objects.create(**self.source_data)     
        self.references_data = {
            "volume": "volume 4",
            "publication": "2034",
            "page_begin": 1,
            "page_end": 5,
            "edition_ref": "rett",
            "source": self.source
        }
        
        self.reference = Reference.objects.create(**self.references_data)
        self.article = Article.objects.create(**self.article_data)
        self.article_data['state'] = ArticleState.PARRUTION.value
        self.article2 = Article.objects.create(**self.article_data)
        self.article_data['state'] = ArticleState.PUBLICATION.value
        self.article3 = Article.objects.create(**self.article_data)
        self.article.authors.add(self.user)

    def test_update(self):
        self.client.force_authenticate(self.user2)
        self.references_data['source'] = self.source_data
        self.source_data['type_source'] = self.type_source.id
        article_data = {
            "title_fr": "article titre fr2",
            "title_ang": "article titre ang2",
            "abstract_fr": "abstract_fr titre fr2",
            "numero": self.numero.id,
            "keywords_fr": "keywords_fr titre fr2",
            "keywords_ang": "keywords_ang titre fr2",
            "authors": self.authors,
            "page_begin": 1,
            "page_end": 10,
            "doi_link": "doi_link2",
            "orcid_link": "orcid_link2",
            "user": self.user.id,
            "file_submit": base64_file,
            "references": [
                self.references_data
            ]
        }
        #raise error if no owner user
        response = self.client.put(f"{self.URI}{self.article.id}/", data=article_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        #raise error if owner user and state != 1
        self.article.state = ArticleState.PARRUTION.value
        self.article.save()
        response = self.client.put(f"{self.URI}{self.article.id}/", data=article_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        #valid if state == 1 and owner user 
        self.client.force_authenticate(self.user)
        self.article.state = ArticleState.INITIALISATION.value
        self.article.save()
        self.article_data['numero'] = self.numero.id
        response = self.client.put(f"{self.URI}{self.article.id}/", data=article_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jsonformat = json.loads(response.content.decode('utf-8'))
        [self.assertEqual(article_data[key], jsonformat[key]) for key in article_data.keys() if key != "numero" and key != "authors" and key != 'numero' and key != 'user' and key != 'references' and key != 'file_submit']
        #valid if  admin 
        self.client.force_authenticate(self.superuser)
        response = self.client.put(f"{self.URI}{self.article.id}/", data=article_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        jsonformat = json.loads(response.content.decode('utf-8'))
        [self.assertEqual(article_data[key], jsonformat[key]) for key in article_data.keys() if key != "numero" and key != "authors" and key != 'numero' and key != 'user' and key != 'references' and key != 'file_submit']

    def test_delete(self):
        #raise error if no user
        self.client.force_authenticate(self.user2)
        response = self.client.delete(f"{self.URI}{self.article.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        #raise error if owner user and != 1
        self.article.state = ArticleState.PARRUTION.value
        self.article.save()
        self.client.force_authenticate(self.user)
        response = self.client.delete(f"{self.URI}{self.article.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        #valid if owner user and state == 1
        self.article.state = ArticleState.INITIALISATION.value
        self.article.save()
        self.client.force_authenticate(self.user)
        response = self.client.delete(f"{self.URI}{self.article.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        #valid if admin
        self.client.force_authenticate(self.superuser)
        article = Article.objects.create(**self.article_data)
        response = self.client.delete(f"{self.URI}{article.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_all(self):
        response = self.client.get(self.PUBLIC_URI)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_initialisation(self):
        response = self.client.get(f"{self.PUBLIC_URI}?state={ArticleState.INITIALISATION.value}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_format = json.loads(response.content.decode('utf-8'))
        [self.assertEqual(article['state'], ArticleState.INITIALISATION.value) for article in json_format['results']]

    def test_get_parrution(self):
        response = self.client.get(f"{self.PUBLIC_URI}?state={ArticleState.PARRUTION.value}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_format = json.loads(response.content.decode('utf-8'))
        [self.assertEqual(article['state'], ArticleState.PARRUTION.value) for article in json_format['results']]

    def test_get_publication(self):
        response = self.client.get(f"{self.PUBLIC_URI}?state={ArticleState.PUBLICATION.value}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_format = json.loads(response.content.decode('utf-8'))
        [self.assertEqual(article['state'], ArticleState.PUBLICATION.value) for article in json_format['results']]

    def test_get_one(self):
        response = self.client.get(f"{self.PUBLIC_URI}{self.article.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(json.loads(response.content.decode('utf-8')) , dict)

    #create or initialization of an article
    def test_submit_article(self):
        self.client.force_authenticate(self.user)
        articles_count_before = Article.objects.count()
        article_data = self.article_data
        article_data['id'] = ''
        article_data['authors'] = self.authors
        article_data['user'] = self.user.id
        article_data['numero'] = self.numero.id
        self.source_data['type_source'] = self.type_source.id
        self.references_data['source'] = self.source_data
        article_data['references'] = [self.references_data]
        article_data["file_submit"] = base64_file
        
        response = self.client.post(self.URI + '?retrieve=1', data=article_data, format='json')
        self.assertEqual(articles_count_before + 1, Article.objects.count())

    #valid initialization that will become a parrution article
    def test_valid_article_submitted_to_parrution(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse_lazy('validate-article', args=(self.article.id, )))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        #valid if admin
        self.client.force_authenticate(self.superuser)
        response = self.client.get(reverse_lazy('validate-article', args=(self.article.id, )))
        jsonformat = json.loads(response.content.decode('utf-8'))
        self.assertEqual(jsonformat['state'], ArticleState.PARRUTION.value)

    #publish article come from parrution
    def test_valid_parrution_to_publication(self):
        self.client.force_authenticate(self.user)
        #raise error if no admin
        response = self.client.get(reverse_lazy('publication-article', args=(self.article.id, )))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        #valid if admin
        self.client.force_authenticate(self.superuser)
        response = self.client.get(reverse_lazy('publication-article', args=(self.article.id, )))
        jsonformat = json.loads(response.content.decode('utf-8'))
        self.assertEqual(jsonformat['state'], ArticleState.PUBLICATION.value)

    def test_most_downloader(self):
        response = self.client.get(reverse_lazy('popular-article'))
        jsonformat = json.loads(response.content.decode('utf-8'))
        self.assertLessEqual(len(jsonformat), 5)

    def test_article_filter(self):
        uri = reverse_lazy('filter-article')
        article = self.article
        article_data = {
            "title_fr": "article titre fr",
            "title_ang": "article titre ang",
            "abstract_fr": "abstract_fr titre fr",
            "numero": self.numero.id,
            "keywords_fr": "keywords_fr titre fr",
            "keywords_ang": "keywords_ang titre fr",
            "page_begin": 1,
            "page_end": 10,
            "doi_link": "doi_link",
            "orcid_link": "orcid_link",
            "user": self.user.id,
            "id": article.id
        }
        response = self.client.post(uri, data=article_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_format = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(json_format), 1)