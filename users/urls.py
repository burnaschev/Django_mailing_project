from django.urls import path

from users.apps import UsersConfig
from users.views import LoginView, LogoutView, RegisterView, UserUpdateView, generate_new_password, verify_email, \
    UserListView, block_user, verify_email_btn

app_name = UsersConfig.name

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserUpdateView.as_view(), name='profile'),
    path('profile/genpassword', generate_new_password, name='generate_new_password'),
    path('verify/<str:token>/', verify_email, name='verify_email'),
    path('user/list', UserListView.as_view(), name='user_list'),
    path('user/list/block/<int:pk>/', block_user, name='block_user'),
    path('user/verify_email_btn/<str:pk>/', verify_email_btn, name='verify_email_btn'),
]