from database import *
from data_processing import *

def main():
    arnott_paras, arnott_tables = json_to_lc_docs(file_path = 'factsheets/json/Factsheet-April-2024-Cayman.pdf.json', fund_name = 'arnott-capital-cayman', year = 2024, month = 4)
    #haidar_paras, haidar_tables = json_to_lc_docs(file_path = 'factsheets/json/Haidar Jupiter April 2024.pdf.json', fund_name = 'haidar-jupiter', year = 2024, month = 4)
    arnott_graph_doc = documents_to_graph_doc(documents = arnott_paras, fund_name = "arnott-capital-cayman", year = 2024, month = 4)
    #haidar_graph_doc = documents_to_graph_doc(documents = haidar_paras, fund_name = "haidar-jupiter", year = 2024, month = 4)
    #upload_graph_doc(arnott_graph_doc)
    add_doc_to_neo4j(arnott_graph_doc)

if __name__ == "__main__":
    main()