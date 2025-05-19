# accounts/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

def placeholder_view_accounts(request):
    return HttpResponse("Placeholder para views do app Accounts. (Ex: login, cadastro de cliente, etc.)")

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("core:dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("accounts:login")

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounts:login")
    else:
        form = UserCreationForm()
    return render(request, "accounts/register.html", {"form": form})

def password_reset_view(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            return redirect("accounts:password_reset_done")
    else:
        form = PasswordResetForm()
    return render(request, "accounts/password_reset.html", {"form": form})

def password_reset_done_view(request):
    return render(request, "accounts/password_reset_done.html")

def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect("accounts:password_reset_complete")
        else:
            form = SetPasswordForm(user)
        return render(request, "accounts/password_reset_confirm.html", {"form": form})
    else:
        return HttpResponse("Link inválido ou expirado.", status=400)

def password_reset_complete_view(request):
    return render(request, "accounts/password_reset_complete.html")

