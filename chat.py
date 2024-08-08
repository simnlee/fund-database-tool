from langchain.chains import GraphCypherQAChain
import neo4j_graph
import os 
from data_processing import *

config = load_config()
os.environ['COHERE_API_KEY'] = config["Cohere"]["api_key"]
os.environ['LANGCHAIN_TRACING_V2'] = config['Langchain']['tracing']
os.environ['LANGCHAIN_ENDPOINT'] = config['Langchain']['endpoint']
os.environ['LANGCHAIN_API_KEY'] = config['Langchain']['api_key']
os.environ['LANGCHAIN_PROJECT'] = config['Langchain']['project_name']


def create_qa_chain():
    if config['LLM'] is 'Cohere':
        from langchain_cohere import ChatCohere
        model = ChatCohere(model=config["Cohere"]["model"], temperature = config['LLM']['temperature'], max_tokens = config['LLM']['max_tokens'])
    elif config['LLM'] is 'OpenAI':
        from langchain_openai import ChatOpenAI
        model = ChatOpenAI(model = config['OpenAI']['model'], temperature = config['LLM']['temperature'], max_tokens = config['LLM']['max_tokens'])
    graph = neo4j_graph.Neo4jGraph(url = config["Neo4j"]["uri"], username = config["Neo4j"]["username"], password = config["Neo4j"]["password"])
    chain = GraphCypherQAChain.from_llm(model, graph, verbose = True)
    return chain

def query_graph_chain(chain, query: str):
    chain.invoke({'input': query})


