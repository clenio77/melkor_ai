# accounts/admin.py
from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "nome_completo",
        "empresa",
        "token_acesso",
        "data_validade_token",
    )
    search_fields = ("user__username", "nome_completo", "empresa")
    list_filter = ("empresa", "data_validade_token")
    raw_id_fields = ("user",) # Para melhor performance com muitos usuários

# Se o modelo APIToken for ativado, registrar aqui também.
# from .models import APIToken
# @admin.register(APIToken)
# class APITokenAdmin(admin.ModelAdmin):
#     list_display = ('key', 'user', 'created', 'expires')
#     search_fields = ('user__username', 'key')
#     list_filter = ('created', 'expires')

