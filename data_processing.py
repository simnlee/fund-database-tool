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

def has_numbers(input):
    return any(char.isdigit() for char in input)

# Calls Azure Document Intelligence API on PDF file and returns list of paragraphs and list of tables separately in Markdown format
def analyze_pdf_with_azure(pdf_path: str):
    endpoint = config['Azure']['endpoint']
    key = config['Azure']['key']
    
    document_intelligence_client = DocumentIntelligenceClient(endpoint = endpoint, credential = AzureKeyCredential(key))

    with open(pdf_path, "rb") as f:
        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-layout", analyze_request=f, content_type="application/octet-stream"
        )
    result = poller.result()

    # Extract paragraphs and tables
    paragraphs = []
    tables = []
    for paragraph in result.paragraphs:
        text = paragraph.content
        if has_numbers(text):
            paragraphs.append(text)
    
    for table in result.tables:
        tables.append(azure_table_to_markdown(table))

    return paragraphs, tables

def azure_table_to_markdown(table):
    # Get the maximum row and column indices to determine the size of the table
    max_row = table["rowCount"]
    max_col = table['columnCount']

    # Create a 2D list to store the table content
    table_content = [['' for _ in range(max_col)] for _ in range(max_row)]

    # Fill the table content with cell data
    for cell in table['cells']:
        row = cell['rowIndex']
        col = cell['columnIndex']
        span = cell.get('columnSpan', 1)
        content = cell['content']

        # Insert content into the table, handling column span
        table_content[row][col] = content
        for i in range(1, span):
            table_content[row][col + i] = ''

    # Convert the table content to a Markdown string
    markdown = ''
    for row_index, row in enumerate(table_content):
        markdown += '| ' + ' | '.join(row) + ' |\n'
        if row_index == 0:
            # Add the header separator after the first row
            markdown += '| ' + ' | '.join(['---' for _ in row]) + ' |\n'

    return markdown

def extract_paragraphs_and_tables_from_json(file_path: str):
    with open(file_path, "r") as file:
        data = json.load(file)
    
    paragraphs = []
    tables = []

    i = 0
    # Extract paragraphs
    for paragraph in data['analyzeResult']['paragraphs']:
        text = paragraph['content']
        # count word count of text
        if has_numbers(text):
            paragraphs.append(text)
            i += 1
        
        if i == 2:
            break
            
    # Extract tables
    for table in data['analyzeResult']['tables']:
        tables.append(azure_table_to_markdown(table))

    return paragraphs, tables

def list_to_lc_docs(lis: list):
    return [Document(page_content=str(text)) for text in lis]

# Analyzes Azure response and returns list of paragraphs and list of tables as Langchain documents 
def pdf_to_lc_docs(pdf_path: str):
    paragraphs, tables = analyze_pdf_with_azure(pdf_path)
    paragraph_docs = list_to_lc_docs(paragraphs)
    table_docs = list_to_lc_docs(tables)
    return paragraph_docs, table_docs

# Analyzes Azure response and returns list of paragraphs and list of tables as Langchain documents 
def json_to_lc_docs(file_path: str):
    paragraphs, tables = extract_paragraphs_and_tables_from_json(file_path)
    paragraph_docs = list_to_lc_docs(paragraphs)
    table_docs = list_to_lc_docs(tables)
    return paragraph_docs, table_docs