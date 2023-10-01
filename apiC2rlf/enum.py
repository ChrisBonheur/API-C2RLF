from enum import Enum

class RequestMethod(Enum):
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'

class ArticleState(Enum):
    INITIALISATION = 1
    PARRUTION = 2
    PUBLICATION = 3