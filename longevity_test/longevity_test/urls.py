from django.urls import path
from longevity.views import RegistrationView, LoginView, LogoutView, ChangePasswordView, DeleteUserView, UpdateProfileView, FetchProfileView
from rest_framework_simplejwt import views as jwt_views



urlpatterns = [
    path('accounts/register/', RegistrationView.as_view(), name='register'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('accounts/delete/', DeleteUserView.as_view(), name='delete'),
    path('accounts/token-refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/update/', UpdateProfileView.as_view(), name='update'),
    path('accounts/fetch/', FetchProfileView.as_view(), name='fetch')
]
