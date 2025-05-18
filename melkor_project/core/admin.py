# core/admin.py
from django.contrib import admin
from .models import HistoricoPesquisa # , Prompt # Se o modelo Prompt for ativado

@admin.register(HistoricoPesquisa)
class HistoricoPesquisaAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "timestamp",
        "termo_pesquisado",
        "vara",
        "resultado_resumido",
    )
    search_fields = ("usuario__username", "termo_pesquisado", "vara")
    list_filter = ("timestamp", "vara", "usuario")
    date_hierarchy = "timestamp"
    readonly_fields = ("timestamp",)

# @admin.register(Prompt)
# class PromptAdmin(admin.ModelAdmin):
#     list_display = (
#         "nome",
#         "versao",
#         "ativo",
#         "data_atualizacao",
#     )
#     search_fields = ("nome",)
#     list_filter = ("ativo", "data_atualizacao")
#     readonly_fields = ("data_criacao", "data_atualizacao")

