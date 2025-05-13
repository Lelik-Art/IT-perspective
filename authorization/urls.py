from django.urls import path
from .views import register_view, confirm_view, home_view, user_login, user_logout, forgive_password, restore_password_view

urlpatterns = [
    path('register', register_view, name='register'),
    path('registration', confirm_view, name='confirm'),
    path('login', user_login, name='login'),
    # path('', home_view, name='home'),
    path("logout", user_logout, name="logout"),
    path("restore", restore_password_view, name="restore_password"),
    path('forgive-password', forgive_password, name='forgive_password'),
]
