import os
from dotenv import load_dotenv
from src.zotero_client import ZoteroClient
from src.document_client import DocumentClient

load_dotenv()

def test_add_document():
    zotero_client = ZoteroClient(os.getenv('ZOTERO_USER_ID'), os.getenv('ZOTERO_API_KEY'))
    graph_client = DocumentClient(zotero_client, os.getenv('DATA_PATH'), os.getenv('GRAPH_PATH'))
    key = 'LPCXM5FY'

    if os.path.exists('data/LPCXM5FY.json'):
        os.remove('data/LPCXM5FY.json')
    
    graph_client.add_document(key)
    
    assert os.path.exists(f'data/{key}.json')

def test_delete_document():
    zotero_client = ZoteroClient(os.getenv('ZOTERO_USER_ID'), os.getenv('ZOTERO_API_KEY'))
    graph_client = DocumentClient(zotero_client, os.getenv('DATA_PATH'), os.getenv('GRAPH_PATH'))
    key = 'LPCXM5FY'

    if not os.path.exists('data/LPCXM5FY.json'):
        graph_client.add_document(key)
    
    graph_client.delete_document(key)
    
    assert not os.path.exists(f'data/{key}.json')

def test_sync_documents():
    zotero_client = ZoteroClient(os.getenv('ZOTERO_USER_ID'), os.getenv('ZOTERO_API_KEY'))
    graph_client = DocumentClient(zotero_client, os.getenv('DATA_PATH'), os.getenv('GRAPH_PATH'))
    
    graph_client.sync_documents()
    
    assert os.path.exists('data/LPCXM5FY.json')