# accounts/models.py
from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente_profile')
    nome_completo = models.CharField(max_length=255)
    empresa = models.CharField(max_length=255, blank=True, null=True)
    # Adicionar outros campos relevantes para o cliente, conforme necessidade
    # Ex: token_acesso, data_validade_token, etc.
    token_acesso = models.CharField(max_length=255, blank=True, null=True, unique=True)
    data_criacao_token = models.DateTimeField(null=True, blank=True)
    data_validade_token = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username

# Potencialmente, um modelo para gerenciar os tokens de forma mais robusta
# class APIToken(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     key = models.CharField(max_length=40, primary_key=True)
#     created = models.DateTimeField(auto_now_add=True)
#     expires = models.DateTimeField(null=True, blank=True)
#     # Outros campos como "vara" para filtrar histórico, se o token for por vara

    # def __str__(self):
    #     return self.key

