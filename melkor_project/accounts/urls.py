# accounts/urls.py
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("placeholder/", views.placeholder_view_accounts, name="placeholder_accounts"),
    # Adicionar URLs para login, logout, registro, etc.
    # Ex: path("login/", views.login_view, name="login"),
]

