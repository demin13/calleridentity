from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import UserRegisterView, UserLoginView

urlpatterns = [
    path('user/register', UserRegisterView.as_view(), name='user_registration'),
    path('user/signin', UserLoginView.as_view(), name='user_login'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify')
]