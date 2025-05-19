# accounts/urls.py
from django.urls import path, include
from . import views

app_name = "accounts"

urlpatterns = [
    path("placeholder/", views.placeholder_view_accounts, name="placeholder_accounts"),
    # URLs de autenticação padrão do Django
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    # URLs de redefinição de senha (opcional)
    path("password_reset/", views.password_reset_view, name="password_reset"),
    path("password_reset/done/", views.password_reset_done_view, name="password_reset_done"),
    path("reset/<uidb64>/<token>/", views.password_reset_confirm_view, name="password_reset_confirm"),
    path("reset/done/", views.password_reset_complete_view, name="password_reset_complete"),
]

