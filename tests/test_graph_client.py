import os
from dotenv import load_dotenv
from src.graph_client import GraphClient

load_dotenv()

def test_write_document_page():
    graph_client = GraphClient(os.getenv('DATA_PATH'), os.getenv('GRAPH_PATH'), os.getenv('TEMPLATE_PATH'))
    document = graph_client.write_document_page('LPCXM5FY')
    assert os.path.exists(f"{os.getenv('GRAPH_PATH')}/pages/Association between mobility, non-pharmaceutical interventions, and COVID-19 transmission in Ghana: A modelling study using mobile phone data.md")
