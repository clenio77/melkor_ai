# core/urls.py
from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("placeholder/", views.placeholder_view_core, name="placeholder_core"),
    path("", views.dashboard, name="dashboard"), # Definindo dashboard como raiz do app core
    path("dashboard/", views.dashboard, name="dashboard_explicit"), # Rota explícita se necessário
    path("historico/", views.historico_pesquisas, name="historico_pesquisas"),
    path("api/historico/", views.api_historico, name="api_historico"),
    path("documentacao/api/", views.api_documentation, name="api_documentation"),
    path("integracao/chatgpt/", views.chatgpt_integration_guide, name="chatgpt_integration_guide"),
    path('analise-denuncia/', views.analise_denuncia_view, name='analise_denuncia'),
    # Adicionar outras URLs para funcionalidades do core
]

