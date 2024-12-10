
import os
from dotenv import load_dotenv
from zotero_client import ZoteroClient
from document_client import DocumentClient
from graph_client import GraphClient
from keyword_client import KeywordClient

if __name__ == "__main__":
    load_dotenv()
    zotero_client = ZoteroClient(os.getenv('ZOTERO_USER_ID'), os.getenv('ZOTERO_API_KEY'))
    document_client = DocumentClient(zotero_client, os.getenv('DATA_PATH'), os.getenv('GRAPH_PATH'))
    keyword_client = KeywordClient(os.getenv('DATA_PATH'), os.getenv('KEYWORD_PATH'))
    gc = GraphClient(os.getenv('DATA_PATH'), os.getenv('GRAPH_PATH'), os.getenv('TEMPLATE_PATH'), keyword_client)
    document_client.sync_documents()
    gc.sync_graph()
    gc.backfill_journal_pages()