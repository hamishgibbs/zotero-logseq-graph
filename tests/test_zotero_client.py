import pytest
import os
from dotenv import load_dotenv
from src.zotero_client import (
    ZoteroClient,
    ZoteroAttachment
)

load_dotenv()


def test_get_item_versions():
    zotero_client = ZoteroClient(os.getenv('ZOTERO_USER_ID'), os.getenv('ZOTERO_API_KEY'))
    item_versions = zotero_client.get_item_versions()
    assert type(item_versions) == dict


def test_get_item():
    zotero_client = ZoteroClient(os.getenv('ZOTERO_USER_ID'), os.getenv('ZOTERO_API_KEY'))
    item_key = 'LPCXM5FY'
    item = zotero_client.get_item(item_key)
    assert type(item) == dict


def test_get_document():
    zotero_client = ZoteroClient(os.getenv('ZOTERO_USER_ID'), os.getenv('ZOTERO_API_KEY'))
    item_key = 'LPCXM5FY'
    document = zotero_client.get_document(item_key)
    assert document.data.title == "Association between mobility, non-pharmaceutical interventions, and COVID-19 transmission in Ghana: A modelling study using mobile phone data"


def test_get_document_child_notes():
    zotero_client = ZoteroClient(os.getenv('ZOTERO_USER_ID'), os.getenv('ZOTERO_API_KEY'))
    item_key = 'LPCXM5FY'
    notes = zotero_client.get_document_child_notes(item_key)
    assert notes is not None

def test_get_attachment_items():
    zotero_client = ZoteroClient(os.getenv('ZOTERO_USER_ID'), os.getenv('ZOTERO_API_KEY'))
    parent_key = 'LPCXM5FY'
    attachments = zotero_client.get_attachment_items(parent_key)
    assert type(attachments) == list
    assert all(isinstance(attachment, ZoteroAttachment) for attachment in attachments)

def test_get_attachment_annotations_pdf():
    zotero_client = ZoteroClient(os.getenv('ZOTERO_USER_ID'), os.getenv('ZOTERO_API_KEY'))
    parent_key = 'LPCXM5FY'
    annotations, notes = zotero_client.get_attachment_annotations(parent_key)
    assert type(annotations) == list
    assert type(notes) == list
    
    