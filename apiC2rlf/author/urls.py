from django.urls import path

from . views import UserAPIView, AuthorAPIView

urlpatterns = [
    path('', UserAPIView.as_view()),
    path('author', AuthorAPIView.as_view()),
    path('author/<int:id_user>', AuthorAPIView.as_view()),
]
