import os
import zipfile

# Estrutura do projeto com conteúdo dos arquivos
project_structure = {
    "agents/search_agent.py": """from crewai import Agent
from tools.web_search_tool import WebSearchTool

def create_search_agent():
    return Agent(
        role="Especialista em Busca de Provas",
        goal="Encontrar provas anteriores para o cargo, concurso, banca e cidade especificados.",
        backstory="Especialista em busca na web e recuperação de dados, com conhecimento profundo de repositórios de provas de concursos públicos.",
        tools=[WebSearchTool()],
        verbose=True
    )
""",
    "agents/study_plan_agent.py": """from crewai import Agent
from tools.study_plan_tool import StudyPlanTool

def create_study_plan_agent():
    return Agent(
        role="Criador de Plano de Estudos",
        goal="Criar um plano de estudos personalizado com base em provas anteriores e padrões da banca.",
        backstory="Educador experiente especializado em criar cronogramas de estudo estruturados para candidatos a concursos.",
        tools=[StudyPlanTool()],
        verbose=True
    )
""",
    "agents/mock_exam_agent.py": """from crewai import Agent
from tools.mock_exam_tool import MockExamTool

def create_mock_exam_agent():
    return Agent(
        role="Gerador de Simulados",
        goal="Gerar simulados com base no estilo de questões e padrões de provas anteriores da banca.",
        backstory="Especialista em design de provas, familiarizado com os formatos e níveis de dificuldade das bancas.",
        tools=[MockExamTool()],
        verbose=True
    )
""",
    "agents/__init__.py": "",
    "tools/web_search_tool.py": """from crewai_tools import Tool
from duckduckgo_search import DDG
import os
import requests
from bs4 import BeautifulSoup
import PyPDF2

class WebSearchTool(Tool):
    name = "WebSearchTool"
    description = "Pesquisa na web por provas anteriores e extrai dados relevantes."

    def _run(self, query: str) -> str:
        results = DDG().text(query, max_results=10)
        exam_data = []
        for result in results:
            try:
                response = requests.get(result['href'], timeout=5)
                if response.headers.get('content-type') == 'application/pdf':
                    with open(f"data/previous_exams/{result['title']}.pdf", 'wb') as f:
                        f.write(response.content)
                    exam_data.append(f"PDF salvo: {result['title']}")
                else:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = soup.get_text()
                    exam_data.append(f"Texto extraído de {result['href']}: {text[:500]}...")
            except Exception as e:
                exam_data.append(f"Erro ao processar {result['href']}: {str(e)}")
        return "\n".join(exam_data)
""",
    "tools/study_plan_tool.py": """from crewai_tools import Tool
import datetime
import json

class StudyPlanTool(Tool):
    name = "StudyPlanTool"
    description = "Gera um plano de estudos personalizado com base em dados de provas."

    def _run(self, exam_data: str, study_hours: int, months: int) -> str:
        topics = ["Matemática", "Português", "Direito", "Informática", "Conhecimentos Específicos"]
        daily_hours = study_hours / 5  # Assume 5 dias/semana
        plan = {}
        start_date = datetime.datetime.now()
        for i, topic in enumerate(topics):
            plan[f"Semana {i+1}"] = {
                "Tópico": topic,
                "Horas": daily_hours,
                "DataInício": (start_date + datetime.timedelta(days=i*7)).strftime("%Y-%m-%d")
            }
        with open(f"data/study_plans/plano_{start_date.strftime('%Y%m%d')}.json", 'w') as f:
            json.dump(plan, f, indent=2)
        return json.dumps(plan)
""",
    "tools/mock_exam_tool.py": """from crewai_tools import Tool
import random

class MockExamTool(Tool):
    name = "MockExamTool"
    description = "Gera um simulado com base nos padrões da banca."

    def _run(self, exam_data: str) -> str:
        questions = [
            {
                "question": "Qual é a capital do Brasil?",
                "options": ["Rio de Janeiro", "São Paulo", "Brasília", "Salvador"],
                "answer": "Brasília"
            },
            {
                "question": "Resolva: 2x + 3 = 7",
                "options": ["x=1", "x=2", "x=3", "x=4"],
                "answer": "x=2"
            }
        ]
        random.shuffle(questions)
        exam_content = ["Simulado\n"]
        for i, q in enumerate(questions, 1):
            exam_content.append(f"{i}. {q['question']}")
            for j, opt in enumerate(q['options'], 1):
                exam_content.append(f"   {j}) {opt}")
            exam_content.append(f"Resposta: {q['answer']}\n")
        return "\n".join(exam_content)
""",
    "tools/__init__.py": "",
    "app/main.py": """import streamlit as st
from app.crew import run_crew

st.title("Assistente de Preparação para Concursos Públicos")

# Entrada do usuário
cargo = st.text_input("Cargo")
concurso = st.text_input("Concurso")
banca = st.text_input("Banca")
cidade = st.text_input("Cidade")
study_hours = st.number_input("Horas de Estudo Semanais", min_value=1, max_value=40, value=10)
study_months = st.number_input("Duração do Estudo (Meses)", min_value=1, max_value=12, value=6)

if st.button("Gerar Plano de Estudos e Simulado"):
    if cargo and concurso and banca and cidade:
        with st.spinner("Processando..."):
            result = run_crew(cargo, concurso, banca, cidade, study_hours, study_months)
        st.subheader("Plano de Estudos")
        st.json(result['study_plan'])
        st.subheader("Simulado")
        st.text(result['mock_exam'])
    else:
        st.error("Preencha todos os campos.")
""",
    "app/crew.py": """from crewai import Crew, Process
from agents.search_agent import create_search_agent
from agents.study_plan_agent import create_study_plan_agent
from agents.mock_exam_agent import create_mock_exam_agent
from crewai import Task

def run_crew(cargo, concurso, banca, cidade, study_hours, study_months):
    # Inicializa agentes
    search_agent = create_search_agent()
    study_plan_agent = create_study_plan_agent()
    mock_exam_agent = create_mock_exam_agent()

    # Define tarefas
    search_task = Task(
        description=f"Buscar provas anteriores para o cargo '{cargo}' no concurso '{concurso}', organizado pela banca '{banca}' na cidade '{cidade}'.",
        agent=search_agent,
        expected_output="Lista de provas encontradas e dados extraídos."
    )

    study_plan_task = Task(
        description=f"Criar um plano de estudos para {study_hours} horas/semana durante {study_months} meses com base nas provas encontradas.",
        agent=study_plan_agent,
        expected_output="Plano de estudos no formato JSON."
    )

    mock_exam_task = Task(
        description=f"Gerar um simulado com base nos padrões da banca '{banca}' e nas provas encontradas.",
        agent=mock_exam_agent,
        expected_output="Simulado no formato de texto com questões e respostas."
    )

    # Cria crew
    crew = Crew(
        agents=[search_agent, study_plan_agent, mock_exam_agent],
        tasks=[search_task, study_plan_task, mock_exam_task],
        process=Process.sequential
    )

    # Executa crew
    result = crew.kickoff()
    
    return {
        "exam_data": result.tasks_output[0].raw,
        "study_plan": result.tasks_output[1].raw,
        "mock_exam": result.tasks_output[2].raw
    }
""",
    "app/__init__.py": "",
    "requirements.txt": """crewai==0.30.11
crewai-tools==0.2.6
streamlit==1.36.0
duckduckgo-search==6.2.15
requests==2.32.3
beautifulsoup4==4.12.3
PyPDF2==3.0.1
python-dotenv==1.0.1
""",
    ".env": """# Adicione chaves de API, se necessário (ex.: para APIs de busca premium)
# SEARCH_API_KEY=sua_chave_aqui
""",
    "README.md": """# Assistente de Preparação para Concursos

Sistema baseado em CrewAI para auxiliar candidatos a concursos públicos, gerando planos de estudo e simulados com base em provas anteriores.

## Configuração

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-repo/exam-prep-crewai.git
   cd exam-prep-crewai
    """
}