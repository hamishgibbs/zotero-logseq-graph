import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from zotero_client import (
    ZoteroClient,
    ZoteroDocument,
    ZoteroAttachmentHighlight,
    ZoteroNote,
    ZoteroNoteData
)
from pydantic import BaseModel
from typing import List, Optional

class DocumentHighlight(BaseModel):
    text: str
    mtime: str

class DocumentNote(BaseModel):
    text: str
    mtime: str

class Document(BaseModel):
    key: str
    version: int
    title: str
    abstract: Optional[str]
    collections: list[str]
    annotations: list[DocumentHighlight]
    notes: list[DocumentNote]

class DocumentClient:
    def __init__(self, zotero_client: ZoteroClient, data_path: str, graph_path: str):
        self.zotero_client = zotero_client
        self.data_path = data_path
        self.graph_path = graph_path
        
    def split_note_content(self, note: ZoteroNote):
        soup = BeautifulSoup(note.data.text, 'html.parser')
        text = soup.get_text()
        lines = text.split('\n')
        return [ZoteroNote(
            key=note.key,
            data=ZoteroNoteData(
                note=line,
                dateModified=note.data.mtime
            )
        ) for line in lines if len(line) > 0]

    def document_from_zotero(
        self,
        zotero_doc: ZoteroDocument,
        zotero_highlights: List[ZoteroAttachmentHighlight],
        zotero_notes: List[ZoteroNote]) -> Document:
        
        highlights = [
            DocumentHighlight(**highlight.data.dict())
            for highlight in zotero_highlights
        ]

        notes = [
            DocumentNote(**note.data.dict())
            for note in zotero_notes
        ]

        return Document(
            key=zotero_doc.key,
            version=zotero_doc.version,
            title=zotero_doc.data.title,
            abstract=zotero_doc.data.abstract,
            collections=zotero_doc.data.collections,
            annotations=highlights,
            notes=notes
        )

    def add_document(self, key: str):
        zotero_doc = self.zotero_client.get_document(key)
        
        if zotero_doc is None: # DEV: This won't currently support top-level notes
            return
        
        zotero_highlights, zotero_notes = self.zotero_client.get_attachment_annotations(key)
        
        child_notes = [self.split_note_content(x) for x in self.zotero_client.get_document_child_notes(key)]
        child_notes = [item for sublist in child_notes for item in sublist]
        
        zotero_notes.extend(child_notes)
        document = self.document_from_zotero(zotero_doc, zotero_highlights, zotero_notes)

        with open(f"{self.data_path}/{key}.json", "w") as f:
            f.write(document.json())
        
    def delete_document(self, key: str):
        os.remove(f"{self.data_path}/{key}.json")        

    def update_document(self, key: str):
        print(f"Updating document {key}")
        self.delete_document(key)
        self.add_document(key)
    
    def sync_documents(self):
        versions = self.zotero_client.get_item_versions()
        n_keys = len(versions)
        i = 0
        for key, version in versions.items():
            try:
                with open(f"{self.data_path}/{key}.json") as f:
                    document = Document.parse_raw(f.read())
                    if document.version != version:
                        self.update_document(key)
            except FileNotFoundError:
                self.add_document(key)
            #print(f"Synced {i} of {n_keys} documents ({i/n_keys*100:.2f}%)")
            i += 1
        
    def write_document_page(self, document: ZoteroDocument):
        pass

if __name__ == "__main__":
    load_dotenv()
    zotero_client = ZoteroClient(os.getenv('ZOTERO_USER_ID'), os.getenv('ZOTERO_API_KEY'))
    document_client = DocumentClient(zotero_client, os.getenv('DATA_PATH'), os.getenv('GRAPH_PATH'))
    document_client.sync_documents()