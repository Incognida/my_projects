from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView, TokenVerifyView,
)
from .views import (
    UserView, CreateUserView, upload_avatar, sign_in
)

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('login/', sign_in, name='login'),
    path('sign_up/', CreateUserView.as_view(), name='sign_up'),
    path('profile/', UserView.as_view(), name='profile'),
    path('upload_avatar/', upload_avatar, name='upload_avatar')
]