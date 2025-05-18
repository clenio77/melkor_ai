# jurisprudencia_tool.py

"""
Ferramenta para buscar jurisprudência em sites jurídicos como JusBrasil, STF, STJ e outros tribunais.
Utiliza Playwright para interagir com as páginas web e extrair informações relevantes.
"""

import asyncio
from playwright.async_api import async_playwright, Playwright, Browser, Page
from typing import List, Dict, Optional
import time

class JurisprudenciaTool:
    def __init__(self, timeout: int = 30000, headless: bool = True):
        """
        Inicializa a ferramenta de busca de jurisprudência.

        Args:
            timeout: Tempo máximo de espera para operações do Playwright (em milissegundos).
            headless: Se True, executa o navegador em modo headless (sem interface gráfica).
        """
        self.timeout = timeout
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.playwright: Optional[Playwright] = None

    async def _get_browser(self) -> Browser:
        """Retorna uma instância do navegador, inicializando se necessário."""
        if self.playwright is None:
            self.playwright = await async_playwright().start()
        if self.browser is None or not self.browser.is_connected():
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
        return self.browser

    async def close_browser(self):
        """Fecha o navegador e o Playwright se estiverem abertos."""
        if self.browser and self.browser.is_connected():
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def buscar_jurisprudencia(self, termo_busca: str, sites: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """
        Busca jurisprudência sobre um termo específico nos sites fornecidos ou em um conjunto padrão.

        Args:
            termo_busca: O termo a ser pesquisado.
            sites: Lista opcional de sites para buscar. Sites suportados no momento:
                   ["jusbrasil", "stf", "stj", "tjmg"].
                   Se None, busca em todos os sites suportados.

        Returns:
            Uma lista de dicionários, onde cada dicionário representa um resultado de jurisprudência
            contendo chaves como "titulo", "link", "resumo", "fonte", "data_publicacao".
        """
        if sites is None:
            sites = ["jusbrasil", "stf", "stj", "tjmg"] # Sites padrão conforme especificado

        resultados_finais: List[Dict[str, str]] = []
        browser = await self._get_browser()
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            java_script_enabled=True,
            accept_downloads=False,
            bypass_csp=True
        )
        # Adicionar cookies se necessário para evitar pop-ups de consentimento, etc.
        # await context.add_cookies([...])

        for site in sites:
            page = await context.new_page()
            try:
                if site == "jusbrasil":
                    resultados_site = await self._buscar_jusbrasil(page, termo_busca)
                elif site == "stf":
                    resultados_site = await self._buscar_stf(page, termo_busca)
                elif site == "stj":
                    resultados_site = await self._buscar_stj(page, termo_busca)
                elif site == "tjmg":
                    resultados_site = await self._buscar_tjmg(page, termo_busca)
                else:
                    print(f"Site não suportado: {site}")
                    resultados_site = []
                
                resultados_finais.extend(resultados_site)
            except Exception as e:
                print(f"Erro ao buscar em {site}: {e}")
            finally:
                await page.close()
        
        await context.close()
        # Não fechar o browser aqui se for reutilizar em chamadas subsequentes
        # await self.close_browser() # Descomente se quiser fechar após cada busca completa
        return resultados_finais

    async def _buscar_jusbrasil(self, page: Page, termo_busca: str) -> List[Dict[str, str]]:
        """Busca jurisprudência no JusBrasil."""
        print(f"Buscando '{termo_busca}' no JusBrasil...")
        resultados: List[Dict[str, str]] = []
        url = f"https://www.jusbrasil.com.br/jurisprudencia/busca?q={termo_busca.replace(' ', '+')}"
        await page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000) # Espera adicional para carregamento dinâmico

        # Tenta fechar pop-ups de consentimento/login se aparecerem
        try:
            if await page.locator("button[aria-label='close']").is_visible(timeout=2000):
                 await page.locator("button[aria-label='close']").click()
            elif await page.locator("*[data-testid='modal-close-button']").is_visible(timeout=2000):
                 await page.locator("*[data-testid='modal-close-button']").click()
        except Exception:
            pass # Ignora se o pop-up não estiver presente

        # Extrai os resultados
        # A estrutura do JusBrasil pode mudar, então os seletores podem precisar de ajuste.
        items = await page.locator("div.search-results_SearchCard__1wsPd").all()
        if not items:
             items = await page.locator("div[data-testid='search-result-card']").all()

        for i, item in enumerate(items[:5]): # Limita a 5 resultados por site por enquanto
            try:
                titulo_element = item.locator("h2 a, a h2, a[data-testid='search-result-card-title']")
                titulo = await titulo_element.inner_text()
                link = await titulo_element.get_attribute("href")
                if link and not link.startswith("http"):
                    link = f"https://www.jusbrasil.com.br{link}"
                
                resumo_element = item.locator("div.DocumentSnippet, p[data-testid='search-result-card-snippet']")
                resumo = await resumo_element.inner_text() if await resumo_element.count() > 0 else "Resumo não disponível"
                
                # Data e fonte podem ser mais complexos de extrair de forma consistente
                data_publicacao = "Não informado"
                try:
                    data_element = item.locator("span.BaseSnippetWrapper-publish-date, time")
                    if await data_element.count() > 0:
                        data_publicacao = await data_element.first.inner_text()
                except Exception:
                    pass

                resultados.append({
                    "titulo": titulo.strip(),
                    "link": link.strip() if link else "",
                    "resumo": resumo.strip(),
                    "fonte": "JusBrasil",
                    "data_publicacao": data_publicacao.strip()
                })
            except Exception as e:
                print(f"Erro ao processar item do JusBrasil: {e}")
        print(f"Encontrados {len(resultados)} resultados no JusBrasil.")
        return resultados

    async def _buscar_stf(self, page: Page, termo_busca: str) -> List[Dict[str, str]]:
        """Busca jurisprudência no STF."""
        print(f"Buscando '{termo_busca}' no STF...")
        resultados: List[Dict[str, str]] = []
        # URL e seletores específicos para o STF
        # Exemplo: https://jurisprudencia.stf.jus.br/pages/search?base=acordaos&sinonimo=true&plural=true&page=1&pageSize=10&queryString={termo_busca}
        # Esta parte precisará de implementação detalhada dos seletores corretos para o STF.
        await page.goto(f"https://portal.stf.jus.br/jurisprudencia/pesquisarJurisprudencia.asp", timeout=self.timeout)
        await page.fill("input[name='pesquisa']", termo_busca)
        await page.press("input[name='pesquisa']", "Enter")
        await page.wait_for_timeout(3000)
        # ... lógica de extração para STF
        print(f"Busca no STF ainda não implementada em detalhes.")
        return resultados

    async def _buscar_stj(self, page: Page, termo_busca: str) -> List[Dict[str, str]]:
        """Busca jurisprudência no STJ."""
        print(f"Buscando '{termo_busca}' no STJ...")
        resultados: List[Dict[str, str]] = []
        # URL e seletores específicos para o STJ
        # Exemplo: https://scon.stj.jus.br/SCON/pesquisar.jsp?NOME_USUARIO=&ACAO=PESQUISAR&novaConsulta=true&i=1&OPERADOR_E_OU=AND&tipoPesquisa=&chkOrgao=&DATA_JULGAMENTO_INI=&DATA_JULGAMENTO_FIM=&obj_TEXTO=&ementa=&hide=&p={termo_busca}
        # Esta parte precisará de implementação detalhada dos seletores corretos para o STJ.
        await page.goto(f"https://scon.stj.jus.br/SCON/", timeout=self.timeout)
        await page.fill("textarea[name='pesquisaLivre']", termo_busca)
        await page.click("input[name='imgBotao']") # Botão de pesquisa
        await page.wait_for_timeout(3000)
        # ... lógica de extração para STJ
        print(f"Busca no STJ ainda não implementada em detalhes.")
        return resultados

    async def _buscar_tjmg(self, page: Page, termo_busca: str) -> List[Dict[str, str]]:
        """Busca jurisprudência no TJMG."""
        print(f"Buscando '{termo_busca}' no TJMG...")
        resultados: List[Dict[str, str]] = []
        # URL e seletores específicos para o TJMG
        # Exemplo: https://jurisprudencia.tjmg.jus.br/jurisprudencia/pesquisaPalavrasGerarInteiro Teor.do?numeroRegistro=1&paginaNumero=1&linhasPorPagina=10&palavras={termo_busca}
        # Esta parte precisará de implementação detalhada dos seletores corretos para o TJMG.
        await page.goto(f"https://www5.tjmg.jus.br/jurisprudencia/pesquisaJurisprudenciaPrimeiraInstancia.do", timeout=self.timeout)
        # O TJMG pode ter um formulário mais complexo
        await page.fill("input[name='palavras']", termo_busca)
        await page.click("input[name='pesquisar']")
        await page.wait_for_timeout(3000)
        # ... lógica de extração para TJMG
        print(f"Busca no TJMG ainda não implementada em detalhes.")
        return resultados

async def main_test():
    tool = JurisprudenciaTool(headless=True) # Mude para False para ver o navegador
    termo = "homicídio qualificado tribunal do júri nulidade"
    
    print(f"Iniciando busca por: {termo}")
    resultados_gerais = await tool.buscar_jurisprudencia(termo, sites=["jusbrasil"]) # Testando apenas JusBrasil por enquanto
    
    if resultados_gerais:
        print("\n--- Resultados Encontrados ---")
        for res in resultados_gerais:
            print(f"\nTítulo: {res['titulo']}")
            print(f"Link: {res['link']}")
            print(f"Fonte: {res['fonte']}")
            print(f"Data: {res['data_publicacao']}")
            print(f"Resumo: {res['resumo'][:200]}...")
    else:
        print("Nenhum resultado encontrado.")
    
    await tool.close_browser()

if __name__ == "__main__":
    # Para executar o teste:
    # 1. Certifique-se de ter o Playwright instalado e os navegadores baixados:
    #    pip install playwright
    #    python -m playwright install
    # 2. Execute este script.
    asyncio.run(main_test())

