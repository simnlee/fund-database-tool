import os 
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate, SystemMessage
from langchain_core.output_parsers.json import JsonOutputParser 
from data_processing import *
from langchain_cohere import ChatCohere, CohereEmbeddings
from typing import Any, Dict, List, Optional
from langchain_community.vectorstores import Chroma
from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator
import pandas as pd

config = load_config()
os.environ['COHERE_API_KEY'] = config["Cohere"]["api_key"]
os.environ['LANGCHAIN_TRACING_V2'] = config['Langchain']['tracing']
os.environ['LANGCHAIN_ENDPOINT'] = config['Langchain']['endpoint']
os.environ['LANGCHAIN_API_KEY'] = config['Langchain']['api_key']
os.environ['LANGCHAIN_PROJECT'] = config['Langchain']['project_name']

return_prompt = """
What is the return of the fund in {month} {year}? Do not provide any explanation or context. Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, or if the context is not relevant, output 'n/a'. If the return is surrounded in parentheses (e.g. (2.03%)) then this represents a negative return, so just output '-2.03%'.
The term 'MTD' refers to the month-to-date return, and is the return of the month in that month. Output should be lowercase. 

Context: {context}

Format instructions: {format_instructions}
"""

PROMPT_TEMPLATE = PromptTemplate(template=return_prompt, partial_variables={"month": "month", "year": "year", "format_instructions": "format_instructions"}, input_variables=["context"])

def tables_to_vector(tables: List[Document]):
    vectorstore = Chroma.from_documents(
        documents = tables,
        embedding = CohereEmbeddings(model = "embed-english-v3.0")
    )
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 7})
    return vectorstore, retriever

def get_month_and_year_from_path(filepath: str):
    parent_dir = os.path.dirname(filepath)
    month = str(os.path.basename(parent_dir))
    parent_parent_dir = os.path.dirname(parent_dir)
    year = str(os.path.basename(parent_parent_dir))
    return month, year

def create_prompt(month, year):
    parser = PydanticOutputParser(pydantic_object = MonthlyReturn)
    print("FORMAT INSTRUCTIONS:" + parser.get_format_instructions())

    prompt = PROMPT_TEMPLATE.partial(month=month, year=year, format_instructions=parser.get_format_instructions())
    return prompt

class MonthlyReturn(BaseModel):
    performance: str = Field(description="a percentage, ends in a percentage sign, e.g. '1.43%'. Or is 'n/a' if the return is not available.")
    

def create_chain(prompt):
    llm = ChatCohere(model="command-r-plus", temperature = 0)
    #structured_llm = llm.with_structured_output(MonthlyReturn)
    parser = PydanticOutputParser(pydantic_object = MonthlyReturn)
    chain = prompt | llm | parser
    return chain

def get_return_from_pdf(filePath: str):
    paragraphs, tables = pdf_to_lc_docs(filePath)
    docs = paragraphs + tables
    vectorstore, retriever = tables_to_vector(docs)
    month, year = get_month_and_year_from_path(filePath)
    question = f"What is the return of the fund in {month} {year}? Provide only the percentage value, including the percentage sign."
    context = retriever.invoke(question)
    prompt = create_prompt(month, year)
    chain = create_chain(prompt)
    return chain.invoke({'context': context})

def get_return_from_json(filePath: str):
    paragraphs, tables = json_to_lc_docs(filePath)
    docs = paragraphs + tables
    vectorstore, retriever = tables_to_vector(docs)
    month, year = get_month_and_year_from_path(filePath)
    question = f"What is the return of the fund in {month} {year}? Provide only the percentage value, including the percentage sign."
    context = retriever.invoke(question)
    print("NUMBER OF DOCS: ", len(context))
    prompt = create_prompt(month, year)
    chain = create_chain(prompt)
    return chain.invoke({'context': context})

def process_folder(folderPath: str):
    month = str(os.path.basename(folderPath))
    parent_dir = os.path.dirname(folderPath)
    year = str(os.path.basename(parent_dir))
    existing_file_list = []
    # check if csv already exists 
    if os.path.exists(folderPath + "/" + str(year) + "_" + str(month) + ".csv"):
        old_df = pd.read_csv(folderPath + "/" + str(year) + "_" + str(month) + ".csv")
        existing_file_list = old_df['Filename'].tolist()
    files = os.listdir(folderPath)
    lis = []
    for file in files:
        if file.endswith(".pdf"):
            if os.path.basename(file) not in existing_file_list:
                filePath = os.path.join(folderPath, file)
                file_return = get_return_from_pdf(filePath)
                # initialize list of lists
                entry = [os.path.basename(filePath), file_return.performance]
                lis.append(entry)

    df = pd.DataFrame(lis, columns=['Filename', 'Monthly Return'])
    csv_path = folderPath + "/" + str(year) + "_" + str(month) + ".csv"
    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_path, index=False)

def process_folder_json(folderPath: str):
    month = str(os.path.basename(folderPath))
    parent_dir = os.path.dirname(folderPath)
    year = str(os.path.basename(parent_dir))
    existing_file_list = []
    # check if csv already exists 
    if os.path.exists(folderPath + "/" + str(year) + "_" + str(month) + ".csv"):
        old_df = pd.read_csv(folderPath + "/" + str(year) + "_" + str(month) + ".csv")
        existing_file_list = old_df['Filename'].tolist()
    files = os.listdir(folderPath)
    lis = []
    for file in files:
        if file.endswith(".json"):
            if os.path.basename(file) not in existing_file_list:
                filePath = os.path.join(folderPath, file)
                file_return = get_return_from_json(filePath)
                # initialize list of lists
                entry = [os.path.basename(filePath), file_return.performance]
                lis.append(entry)

    df = pd.DataFrame(lis, columns=['Filename', 'Monthly Return'])
    csv_path = folderPath + "/" + str(year) + "_" + str(month) + ".csv"
    df.to_csv(csv_path, index=False)

