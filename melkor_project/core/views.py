# core/views.py
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import HistoricoPesquisa

def placeholder_view_core(request):
    return HttpResponse("Placeholder para views do app Core. (Ex: dashboard, histórico de pesquisas, etc.)")

@login_required
def dashboard(request):
    """
    Dashboard principal para usuários autenticados.
    Mostra histórico recente, opções de pesquisa, etc.
    """
    return render(request, 'core/dashboard.html', {
        'title': 'Dashboard - Melkor',
    })

@login_required
def historico_pesquisas(request):
    """
    Exibe o histórico de pesquisas do usuário atual.
    Permite filtrar por vara e outros critérios.
    """
    historico = HistoricoPesquisa.objects.filter(usuario=request.user).order_by('-timestamp')
    vara = request.GET.get('vara')
    if vara:
        historico = historico.filter(vara=vara)
    
    return render(request, 'core/historico.html', {
        'title': 'Histórico de Pesquisas - Melkor',
        'historico': historico,
    })

@login_required
def api_historico(request):
    """
    API para obter histórico de pesquisas em formato JSON.
    Útil para atualizações dinâmicas na interface.
    """
    historico = HistoricoPesquisa.objects.filter(usuario=request.user).order_by('-timestamp')
    vara = request.GET.get('vara')
    if vara:
        historico = historico.filter(vara=vara)
    historico = historico[:50]
    data = [{
        'id': h.id,
        'timestamp': h.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'termo': h.termo_pesquisado,
        'vara': h.vara or 'N/A',
        'resumo': h.resultado_resumido or 'Sem resumo disponível',
    } for h in historico]
    return JsonResponse({'historico': data})

@login_required
def api_documentation(request):
    """Exibe a página de documentação da API."""
    return render(request, 'core/documentation/api_docs.html', {
        'title': 'Documentação da API - Melkor',
    })

@login_required
def chatgpt_integration_guide(request):
    """Exibe o guia de integração com ChatGPT."""
    return render(request, 'core/integration/chatgpt_guide.html', {
        'title': 'Guia de Integração ChatGPT - Melkor',
    })

