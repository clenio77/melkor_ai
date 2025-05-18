# parser_pdf.py

"""
Parser de denúncia PDF com OCR para extrair informações da denúncia.
Este módulo é responsável por processar arquivos PDF de denúncias,
extrair seu conteúdo textual e preparar os dados para análise.
"""

import os
import re
import PyPDF2
from typing import Dict, List, Optional, Tuple, Union

class ParserPDF:
    def __init__(self, use_ocr: bool = True):
        """
        Inicializa o parser de PDF.
        
        Args:
            use_ocr: Se True, utiliza OCR para extrair texto de imagens no PDF.
                     Se False, utiliza apenas extração direta de texto.
        """
        self.use_ocr = use_ocr
        # Verificar se as dependências estão instaladas
        try:
            import pytesseract
            from pdf2image import convert_from_path
            self.pytesseract = pytesseract
            self.convert_from_path = convert_from_path
            self.ocr_available = True
        except ImportError:
            if use_ocr:
                print("AVISO: Dependências de OCR não encontradas. Instalando...")
                print("Execute: pip install pytesseract pdf2image")
                print("E instale o Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
            self.ocr_available = False

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrai texto de um arquivo PDF.
        
        Args:
            pdf_path: Caminho para o arquivo PDF.
            
        Returns:
            Texto extraído do PDF.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Arquivo PDF não encontrado: {pdf_path}")
        
        # Primeiro, tenta extração direta de texto
        text = self._extract_text_direct(pdf_path)
        
        # Se OCR estiver habilitado e o texto extraído for muito curto ou vazio,
        # tenta OCR
        if self.use_ocr and self.ocr_available and (len(text) < 100 or not text.strip()):
            print("Texto extraído diretamente é insuficiente. Tentando OCR...")
            text = self._extract_text_ocr(pdf_path)
        
        # Limpa o texto extraído
        return self._clean_text(text)
    
    def _extract_text_direct(self, pdf_path: str) -> str:
        """
        Extrai texto diretamente do PDF usando PyPDF2.
        
        Args:
            pdf_path: Caminho para o arquivo PDF.
            
        Returns:
            Texto extraído diretamente do PDF.
        """
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
        except Exception as e:
            print(f"Erro ao extrair texto diretamente: {e}")
        
        return text
    
    def _extract_text_ocr(self, pdf_path: str) -> str:
        """
        Extrai texto do PDF usando OCR.
        
        Args:
            pdf_path: Caminho para o arquivo PDF.
            
        Returns:
            Texto extraído via OCR.
        """
        if not self.ocr_available:
            return ""
        
        text = ""
        try:
            # Converte PDF para imagens
            images = self.convert_from_path(pdf_path)
            
            # Extrai texto de cada imagem
            for i, image in enumerate(images):
                print(f"Processando página {i+1}/{len(images)} com OCR...")
                page_text = self.pytesseract.image_to_string(image, lang='por')
                text += page_text + "\n\n"
        except Exception as e:
            print(f"Erro ao extrair texto via OCR: {e}")
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """
        Limpa o texto extraído, removendo cabeçalhos, rodapés e formatação desnecessária.
        
        Args:
            text: Texto a ser limpo.
            
        Returns:
            Texto limpo.
        """
        if not text:
            return ""
        
        # Remove múltiplos espaços em branco
        text = re.sub(r'\s+', ' ', text)
        
        # Remove cabeçalhos e rodapés comuns em documentos jurídicos
        # Estes padrões podem precisar ser ajustados com base nos documentos reais
        headers_footers = [
            r'MINISTÉRIO PÚBLICO DO ESTADO DE.*\n',
            r'PROMOTORIA DE JUSTIÇA.*\n',
            r'Página \d+ de \d+',
            r'Documento assinado digitalmente.*',
            r'www\..*\.jus\.br',
        ]
        
        for pattern in headers_footers:
            text = re.sub(pattern, '', text)
        
        # Remove números de página isolados
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        # Normaliza quebras de linha
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def extract_structured_info(self, text: str) -> Dict[str, Union[str, List[str]]]:
        """
        Extrai informações estruturadas do texto da denúncia.
        
        Args:
            text: Texto extraído da denúncia.
            
        Returns:
            Dicionário com informações estruturadas como:
            - réu(s)
            - vítima(s)
            - crime(s)
            - data_fato
            - local_fato
            - testemunhas
        """
        info = {
            'reus': [],
            'vitimas': [],
            'crimes': [],
            'data_fato': '',
            'local_fato': '',
            'testemunhas': []
        }
        
        # Extração de réus
        reu_patterns = [
            r'denunciado[s]?:?\s*([^,;\n\.]+)',
            r'acusado[s]?:?\s*([^,;\n\.]+)',
            r'réu[s]?:?\s*([^,;\n\.]+)'
        ]
        for pattern in reu_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.group(1).strip() and match.group(1).strip() not in info['reus']:
                    info['reus'].append(match.group(1).strip())
        
        # Extração de vítimas
        vitima_patterns = [
            r'vítima[s]?:?\s*([^,;\n\.]+)',
            r'ofendido[s]?:?\s*([^,;\n\.]+)'
        ]
        for pattern in vitima_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.group(1).strip() and match.group(1).strip() not in info['vitimas']:
                    info['vitimas'].append(match.group(1).strip())
        
        # Extração de crimes
        crime_patterns = [
            r'crime[s]? (?:de|do|da)?\s*([^,;\n\.]+)',
            r'delito[s]? (?:de|do|da)?\s*([^,;\n\.]+)',
            r'(?:art|artigo)[\.:]?\s*(\d+)[^\d]+(?:do|da)\s*(?:CP|Código Penal)',
        ]
        for pattern in crime_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.group(1).strip() and match.group(1).strip() not in info['crimes']:
                    info['crimes'].append(match.group(1).strip())
        
        # Extração de data do fato
        data_patterns = [
            r'(?:em|no dia|na data de|datado de)\s*(\d{1,2}\/\d{1,2}\/\d{2,4})',
            r'(?:em|no dia|na data de|datado de)\s*(\d{1,2}\s+de\s+(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+\d{2,4})'
        ]
        for pattern in data_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['data_fato'] = match.group(1).strip()
                break
        
        # Extração de local do fato
        local_patterns = [
            r'(?:ocorrido|ocorrida|ocorreram|aconteceu|sucedeu|deu-se)[^,;\.]*(?:em|no|na|nos|nas)\s*([^,;\n\.]{5,100})',
            r'(?:local|lugar|endereço)[^,;\.]*(?:em|no|na|nos|nas)\s*([^,;\n\.]{5,100})'
        ]
        for pattern in local_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['local_fato'] = match.group(1).strip()
                break
        
        # Extração de testemunhas
        testemunha_patterns = [
            r'testemunha[s]?:?\s*([^,;\n\.]+)',
            r'(?:ouvir|ouvido|depoimento de)\s*([^,;\n\.]+)'
        ]
        for pattern in testemunha_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.group(1).strip() and match.group(1).strip() not in info['testemunhas']:
                    info['testemunhas'].append(match.group(1).strip())
        
        return info

# Exemplo de uso:
if __name__ == "__main__":
    parser = ParserPDF(use_ocr=True)
    
    # Exemplo com um arquivo fictício
    # pdf_path = "/caminho/para/denuncia.pdf"
    # if os.path.exists(pdf_path):
    #     texto = parser.extract_text_from_pdf(pdf_path)
    #     print(f"Texto extraído ({len(texto)} caracteres):")
    #     print(texto[:500] + "..." if len(texto) > 500 else texto)
    #     
    #     info = parser.extract_structured_info(texto)
    #     print("\nInformações estruturadas:")
    #     for key, value in info.items():
    #         print(f"{key}: {value}")
    # else:
    #     print(f"Arquivo de exemplo não encontrado: {pdf_path}")
    
    # Exemplo com texto fictício para teste
    texto_exemplo = """
    MINISTÉRIO PÚBLICO DO ESTADO DE MINAS GERAIS
    PROMOTORIA DE JUSTIÇA DA COMARCA DE BELO HORIZONTE
    
    DENÚNCIA
    
    O MINISTÉRIO PÚBLICO DO ESTADO DE MINAS GERAIS, por seu Promotor de Justiça, no uso de suas atribuições legais, vem oferecer DENÚNCIA em face de:
    
    JOÃO DA SILVA, brasileiro, solteiro, nascido em 15/03/1985, portador do RG nº 12.345.678, inscrito no CPF sob o nº 123.456.789-00, residente na Rua das Flores, nº 123, Bairro Centro, Belo Horizonte/MG.
    
    Pela prática do seguinte fato delituoso:
    
    No dia 10 de janeiro de 2023, por volta das 22h, na Avenida Afonso Pena, nº 1500, Bairro Centro, Belo Horizonte/MG, o denunciado, com consciência e vontade, subtraiu para si, mediante grave ameaça exercida com emprego de arma de fogo, o veículo modelo Gol, placa ABC-1234, pertencente à vítima MARIA OLIVEIRA.
    
    Segundo apurado, a vítima estava estacionando seu veículo quando foi abordada pelo denunciado, que, empunhando uma arma de fogo, anunciou o assalto e exigiu a entrega das chaves do automóvel.
    
    O crime foi presenciado pelas testemunhas PEDRO SANTOS e ANA PEREIRA, que acionaram a Polícia Militar.
    
    Diante do exposto, o denunciado JOÃO DA SILVA está incurso nas penas do artigo 157, §2º, inciso I, do Código Penal.
    
    Requer-se o recebimento e processamento da presente denúncia, com a citação do denunciado para responder à acusação por escrito, prosseguindo-se nos demais termos processuais até final condenação.
    
    Belo Horizonte, 15 de fevereiro de 2023.
    
    Promotor de Justiça
    
    Página 1 de 1
    """
    
    info = parser.extract_structured_info(texto_exemplo)
    print("Informações estruturadas do exemplo:")
    for key, value in info.items():
        print(f"{key}: {value}")
