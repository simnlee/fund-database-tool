import os 
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate, SystemMessage
from langchain_core.output_parsers.json import JsonOutputParser 
from langchain_experimental.graph_transformers.llm import UnstructuredRelation
from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship
from data_processing import *
# from langchain.graphs import Neo4jGraph
from neo4j import GraphDatabase, Query
from neo4j.exceptions import CypherSyntaxError
from constants import EXAMPLES, GRAPH_BUILDER_HUMAN_PROMPT, GRAPH_BUILDER_SYSTEM_PROMPT, NODE_IMPORT_QUERY, REL_IMPORT_QUERY
from langchain_cohere import ChatCohere
import json_repair
import uuid
from typing import Any, Dict, List, Optional

config = load_config()
# graph = Neo4jGraph(url = config["Neo4j"]["uri"], username = config["Neo4j"]["username"], password = config["Neo4j"]["password"])
# driver = GraphDatabase.driver(config["Neo4j"]["uri"], auth=(config["Neo4j"]["username"], config["Neo4j"]["password"]))
os.environ['COHERE_API_KEY'] = config["Cohere"]["api_key"]
os.environ['LANGCHAIN_TRACING_V2'] = config['Langchain']['tracing']
os.environ['LANGCHAIN_ENDPOINT'] = config['Langchain']['endpoint']
os.environ['LANGCHAIN_API_KEY'] = config['Langchain']['api_key']
os.environ['LANGCHAIN_PROJECT'] = config['Langchain']['project_name']

def create_prompt(fund_name: str, year: int, month: int):
    system_message = SystemMessage(content = GRAPH_BUILDER_SYSTEM_PROMPT)
    parser = JsonOutputParser(pydantic_object = UnstructuredRelation)
    human_prompt = PromptTemplate(template = GRAPH_BUILDER_HUMAN_PROMPT, 
                                  input_variables = ['input'], 
                                  partial_variables = {'format_instructions': parser.get_format_instructions(),
                                                       'examples': EXAMPLES,
                                                       'month': month,
                                                       'year': year,
                                                       'fund_name': fund_name})
    human_message = HumanMessagePromptTemplate(prompt = human_prompt)
    return ChatPromptTemplate.from_messages([system_message, human_message])

def create_graph_transformer(prompt: ChatPromptTemplate, llm):
    chain = prompt | llm
    return chain


def documents_to_graph_doc(documents: list, fund_name: str, year: int, month: int) -> GraphDocument: 
    prompt = create_prompt(fund_name, year, month)
    llm = ChatCohere(model=config["Cohere"]["model"])
    chain = create_graph_transformer(prompt, llm)
    source_doc_id = str(uuid.uuid3(uuid.NAMESPACE_OID, documents[0].metadata['source']))
    #source_doc_id = documents[0].metadata['fund_name'] + "_" + str(documents[0].metadata['year']) + "_" + str(documents[0].metadata['month'])
    print("TYPEE:", type(documents[0].metadata['source']))
    source_doc = Document(id = source_doc_id, page_content=str(documents[0].metadata['source']), metadata=documents[0].metadata)

    nodes_set = set()
    relationships = []

    for i in range(len(documents)):
        print(f'Processing document {i+1}/{len(documents)}...')
        doc = documents[i]
        raw_response = chain.invoke({'input': doc.page_content})
        response = json_repair.loads(raw_response.content)

        for rel in response:
            try:
                rel['head_type'] = rel['head_type'] if rel['head_type'] else 'Unknown'
                rel["tail_type"] = rel["tail_type"] if rel["tail_type"] else "Unknown"
                rel['head'] = rel['head'] if rel['head'] else 'Unknown'
                rel['tail'] = rel['tail'] if rel['tail'] else 'Unknown'
                rel['relation'] = rel['relation'] if rel['relation'] else 'Unknown'
                nodes_set.add((rel["head"], rel["head_type"]))
                nodes_set.add((rel["tail"], rel["tail_type"]))
                source_node = Node(
                    id=rel["head"],
                    type=rel["head_type"]
                )
                target_node = Node(
                    id=rel["tail"],
                    type=rel["tail_type"]
                )
                relationships.append(
                    Relationship(
                        source=source_node,
                        target=target_node,
                        type=rel["relation"]
                    )
                )
            except:
                print(f"Error processing relation: {rel}")

    nodes = [Node(id = n[0], type = n[1]) for n in list(nodes_set)]
    return GraphDocument(nodes = nodes, relationships = relationships, source = source_doc)

"""
def query(query: str, params: dict = {}) -> List[Dict[str, Any]]:
    #graph.add_graph_documents([doc], include_source = True, baseEntityLabel = True)
    with GraphDatabase.driver(config["Neo4j"]["uri"], auth=(config["Neo4j"]["username"], config["Neo4j"]["password"])) as driver:
        with driver.session() as session:
            try:
                data = session.run(Query(text = query, timeout = None), params)
                json_data = [r.data() for r in data]
                return json_data
            except CypherSyntaxError as e:
                raise ValueError(f"Generated Cypher Statement is not valid\n{e}")

def upload_graph_doc(graph_doc: GraphDocument):
    # Upload nodes
    query(
        NODE_IMPORT_QUERY,
        {'data': [n.__dict__ for n in graph_doc.nodes],
        'document': graph_doc.source.__dict__
        }
    )

    # Upload relationships
    query(
        REL_IMPORT_QUERY,
        {
            "data": [
                {
                    "source": n.source.id,
                    "source_label": n.source.type,
                    "target": n.target.id,
                    "target_label": n.target.type,
                    "type": n.type.replace(" ", "_").upper(),
                    "properties": n.properties
                }
                for n in graph_doc.relationships
            ]
        }
    )
"""

def add_doc_to_neo4j(doc: GraphDocument):
    graph = neo4j_graph.Neo4jGraph(url = config["Neo4j"]["uri"], username = config["Neo4j"]["username"], password = config["Neo4j"]["password"])
    graph.add_graph_documents([doc], include_source = True, baseEntityLabel = True)



