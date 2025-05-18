# agente.py

"""
Configuração dos agentes CrewAI para o sistema Melkor.
Inclui:
- Analista de Acusação: Identifica pontos fracos na denúncia.
- Formulador de Perguntas: Gera perguntas estratégicas para testemunhas.
- Redator de Teses: Transforma jurisprudência em argumentos para o plenário.
"""

from crewai import Agent, Task, Crew, Process
from crewai_tools import BaseTool # Se formos criar tools customizadas para CrewAI

# Importar as ferramentas desenvolvidas e a persona
from melkor.persona import PersonaMelkor
from melkor.tool_analise_denuncia import AnaliseDenunciaTool
from melkor.jurisprudencia_tool import JurisprudenciaTool
from melkor.parser_pdf import ParserPDF

# Inicializar a Persona Melkor para fornecer o contexto e o tom aos agentes
persona_melkor = PersonaMelkor()

# Inicializar as ferramentas que os agentes poderão usar
# (A ferramenta de jurisprudência é assíncrona, sua integração com CrewAI síncrono pode exigir um wrapper)
# Por enquanto, vamos focar na estrutura dos agentes.

# Definição das Ferramentas (Wrappers para CrewAI se necessário)
# Exemplo de como uma ferramenta poderia ser definida para CrewAI:
# class MinhaFerramentaCrewAI(BaseTool):
#     name: str = "Nome da Ferramenta"
#     description: str = "Descrição do que a ferramenta faz."
#     def _run(self, argumento: str) -> str:
#         # Lógica da ferramenta
#         return "Resultado da ferramenta"

# 1. Agente: Analista de Acusação
analista_acusacao = Agent(
    role="Analista de Acusação Estratégico",
    goal=f"Analisar minuciosamente o texto de denúncias criminais para identificar pontos fracos, contradições, omissões e possíveis nulidades na acusação, seguindo a abordagem estratégica e os princípios da persona {persona_melkor.nome}.",
    backstory=f"Você é um especialista em análise processual penal, treinado para dissecar acusações com um olhar crítico e detalhista. Sua atuação é pautada pela busca incansável por falhas que possam beneficiar a defesa, sempre com a perspicácia e o rigor técnico de {persona_melkor.nome}.",
    verbose=True,
    allow_delegation=False,
    # tools=[AnaliseDenunciaTool()], # Adicionar a ferramenta de análise de denúncia quando integrada
    llm=None, # Definir o LLM a ser usado (ex: OpenAI, Ollama, etc.)
    max_iter=5,
    # prompt_persona=persona_melkor.get_prompt_base() # Alguns LLMs/frameworks podem aceitar um prompt de persona
)

# 2. Agente: Formulador de Perguntas Estratégicas
formulador_perguntas = Agent(
    role="Formulador de Perguntas Incisivas para Testemunhas",
    goal=f"Elaborar perguntas estratégicas, perspicazes e, quando necessário, desestabilizadoras para testemunhas de acusação e defesa, com o objetivo de extrair informações cruciais, expor contradições ou fortalecer a narrativa da defesa, alinhado com a inteligência e táticas de {persona_melkor.nome}.",
    backstory=f"Você é um mestre na arte do questionamento, capaz de antecipar respostas e conduzir inquirições que revelam a verdade oculta ou a fragilidade dos depoimentos. Sua inspiração vem da capacidade de {persona_melkor.nome} de dominar o tribunal através da palavra.",
    verbose=True,
    allow_delegation=False,
    # tools=[], # Adicionar ferramentas relevantes, ex: acesso a detalhes do caso, perfil de testemunhas
    llm=None, # Definir o LLM
    max_iter=5
)

# 3. Agente: Redator de Teses Jurídicas para Plenário
redator_teses = Agent(
    role="Redator de Teses Jurídicas Persuasivas para o Plenário do Júri",
    goal=f"Transformar informações complexas, incluindo jurisprudência relevante e os pontos fracos da acusação, em argumentos de defesa claros, concisos, persuasivos e emocionalmente impactantes, prontos para serem utilizados no plenário do Tribunal do Júri, refletindo a eloquência e a solidez argumentativa de {persona_melkor.nome}.",
    backstory=f"Você é um artífice da argumentação jurídica, especializado em construir narrativas de defesa que convencem e comovem. Sua habilidade reside em traduzir o jargão legal e os fatos brutos em uma história coesa e convincente, digna da reputação de {persona_melkor.nome}.",
    verbose=True,
    allow_delegation=False,
    # tools=[jurisprudencia_tool_wrapper], # Adicionar a ferramenta de jurisprudência (wrapper)
    llm=None, # Definir o LLM
    max_iter=5
)

# Definição de Tarefas (Tasks) para os agentes
# Exemplo de como uma tarefa poderia ser definida:
# task_analise_denuncia = Task(
#     description="Analisar o seguinte texto de denúncia: {texto_denuncia} e identificar todos os pontos fracos.",
#     agent=analista_acusacao,
#     expected_output="Um relatório detalhado listando os pontos fracos, contradições e omissões encontradas na denúncia, com justificativas baseadas na análise técnica e estratégica."
# )

# Configuração do Crew
# melkor_crew = Crew(
#     agents=[analista_acusacao, formulador_perguntas, redator_teses],
#     tasks=[task_analise_denuncia, ...], # Adicionar outras tarefas
#     process=Process.sequential, # Ou Process.hierarchical
#     verbose=2
# )

# Ponto de entrada para executar o crew (exemplo)
# def run_melkor_analysis(texto_denuncia: str, outros_dados_caso: dict):
#     # Aqui você passaria os dados para as tasks
#     # resultado = melkor_crew.kickoff(inputs={
#     #     'texto_denuncia': texto_denuncia,
#     #     'dados_caso': outros_dados_caso
#     # })
#     # return resultado
#     print("Estrutura dos agentes e crew definida. Implementação da execução pendente.")
#     return "Execução de análise pendente."

if __name__ == "__main__":
    print("Arquivo de agentes (agente.py) carregado.")
    print(f"Persona base para os agentes: {persona_melkor.get_prompt_base()}\n")
    print(f"Agente Analista de Acusação: {analista_acusacao.role}")
    print(f"Agente Formulador de Perguntas: {formulador_perguntas.role}")
    print(f"Agente Redator de Teses: {redator_teses.role}")
    # Exemplo de como iniciar uma análise (requer LLM configurado e tasks definidas)
    # resultado_analise = run_melkor_analysis("Texto da denúncia aqui...", {})
    # print(resultado_analise)

