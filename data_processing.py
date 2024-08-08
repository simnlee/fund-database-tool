import os 
import json 
from pathlib import Path 
from configparser import ConfigParser
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from langchain.docstore.document import Document

def load_config():
    config = ConfigParser()
    config_path = Path(__file__).parent / "config.ini"
    config.read(config_path)
    return config

config = load_config()

# Calls Azure Document Intelligence API on PDF file and returns list of paragraphs and list of tables separately in Markdown format
def analyze_pdf_with_azure(pdf_path: str):
    endpoint = config['azure']['endpoint']
    key = config['azure']['key']
    min_para_words = int(config['azure']['min_para_words'])
    
    document_intelligence_client = DocumentIntelligenceClient(endpoint = endpoint, credential = AzureKeyCredential(key))

    with open(pdf_path, "rb") as f:
        poller = document_intelligence_client.begin_analyze_document("prebuilt-layout", f)
        result = poller.result()

    # Extract paragraphs and tables
    paragraphs = []
    tables = []
    for paragraph in result.paragraphs:
        text = paragraph.content
        if len(text.split()) > min_para_words:
            paragraphs.append(text)
    
    for table in result.tables:
        tables.append(table.content)

    return paragraphs, tables

def extract_paragraphs_and_tables_from_json(file_path: str):
    min_para_words = int(config['Azure']['min_para_words'])
    with open(file_path, "r") as file:
        data = json.load(file)
    
    paragraphs = []
    tables = []

    i = 0
    # Extract paragraphs
    for paragraph in data['analyzeResult']['paragraphs']:
        text = paragraph['content']
        # count word count of text
        if len(text.split()) > min_para_words:
            paragraphs.append(text)
            i += 1
        
        if i == 2:
            break
            
    # Extract tables
    #for table in data['analyzeResult']['tables']:
        #tables.append(table)

    return paragraphs, tables

def list_to_lc_docs(lis: list, metadata: dict):
    return [Document(page_content=str(text), metadata=metadata) for text in lis]

# Analyzes Azure response and returns list of paragraphs and list of tables as Langchain documents 
def pdf_to_lc_docs(pdf_path: str, fund_name: str, year: int, month: int):
    paragraphs, tables = analyze_pdf_with_azure(pdf_path)
    metadata = {"fund": fund_name, "year": year, "month": month, 'source': pdf_path}
    paragraph_docs = list_to_lc_docs(paragraphs, metadata)
    table_docs = list_to_lc_docs(tables, metadata)
    return paragraph_docs, table_docs

# Analyzes Azure response and returns list of paragraphs and list of tables as Langchain documents 
def json_to_lc_docs(file_path: str, fund_name: str, year: int, month: int):
    paragraphs, tables = extract_paragraphs_and_tables_from_json(file_path)
    metadata = {"fund": fund_name, "year": year, "month": month, 'source': file_path}
    paragraph_docs = list_to_lc_docs(paragraphs, metadata)
    table_docs = list_to_lc_docs(tables, metadata)
    return paragraph_docs, table_docs