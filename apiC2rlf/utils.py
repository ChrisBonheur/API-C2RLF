from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 1  # Nombre d'éléments par page
    page_size_query_param = 'page_size'  # Paramètre pour spécifier le nombre d'éléments par page
    max_page_size = 100  # Nombre maximal d'éléments par page