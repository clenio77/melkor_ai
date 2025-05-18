# core/models.py
from django.db import models
from django.contrib.auth.models import User
# from accounts.models import Cliente # Se necessário vincular diretamente ao Cliente

class HistoricoPesquisa(models.Model):
    """Armazena o histórico de pesquisas realizadas pelo agente Melkor."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, help_text="Usuário que realizou a pesquisa")
    # cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True, help_text="Cliente associado à pesquisa, se aplicável")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Data e hora da pesquisa")
    termo_pesquisado = models.TextField(help_text="Termo ou descrição da pesquisa realizada")
    resultado_resumido = models.TextField(blank=True, null=True, help_text="Resumo do resultado da pesquisa")
    # O campo 'vara' é mencionado como filtro, pode ser um CharField ou ForeignKey para uma tabela de Varas, se houver.
    vara = models.CharField(max_length=255, blank=True, null=True, help_text="Vara relacionada à pesquisa, para filtragem")
    # Adicionar campos para armazenar os resultados completos ou referências a eles, se necessário.
    # Ex: json_resultado_completo = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Pesquisa de {self.usuario.username} em {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Histórico de Pesquisa"
        verbose_name_plural = "Históricos de Pesquisas"

# Outros modelos para o app core podem ser adicionados aqui, como:
# - Modelo para armazenar os prompts e suas versões (para centralização e fácil atualização)
# - Modelo para logs de segurança específicos da aplicação (além dos logs gerais do sistema)

# class Prompt(models.Model):
#     nome = models.CharField(max_length=255, unique=True)
#     conteudo = models.TextField()
#     versao = models.PositiveIntegerField(default=1)
#     ativo = models.BooleanField(default=True)
#     data_criacao = models.DateTimeField(auto_now_add=True)
#     data_atualizacao = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.nome} (v{self.versao})"

