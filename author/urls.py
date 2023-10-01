from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . views import AuthorAPIView

urlpatterns = [
    path('', AuthorAPIView.as_view(), name='author'),
    path('<int:id_user>', AuthorAPIView.as_view(), name='author_one'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
