import requests
from datetime import datetime
import zipfile
import pydantic
from bs4 import BeautifulSoup
from io import BytesIO

class ZoteroDocumentData(pydantic.BaseModel):
    title: str
    abstractNote: str
    collections: list[str]
    dateModified: str

class ZoteroDocument(pydantic.BaseModel):
    key: str
    version: int
    data: ZoteroDocumentData

class ZoteroAttachmentData(pydantic.BaseModel):
    filename: str

class ZoteroAttachment(pydantic.BaseModel):
    key: str
    data: ZoteroAttachmentData

class ZoteroAttachmentHighlightData(pydantic.BaseModel):
    annotationText: str
    dateModified: str

class ZoteroAttachmentHighlight(pydantic.BaseModel):
    key: str
    data: ZoteroAttachmentHighlightData

class ZoteroAttachmentNoteData(pydantic.BaseModel):
    annotationComment: str
    dateModified: str

class ZoteroAttachmentNote(pydantic.BaseModel):
    key: str
    data: ZoteroAttachmentNoteData

class ZoteroNoteData(pydantic.BaseModel):
    note: str
    dateModified: str

class ZoteroNote(pydantic.BaseModel):
    key: str
    data: ZoteroNoteData

class ZoteroClient:
    def __init__(self, zotero_user_id: str, zotero_api_key: str):
        self.zotero_user_id = zotero_user_id
        self.zotero_api_key = zotero_api_key
    
    def get_item_versions(self):
        url = f"https://api.zotero.org/users/{self.zotero_user_id}/items/top?format=versions"
        with requests.get(url, headers={"Authorization": f"Bearer {self.zotero_api_key}",
                                                  "Accept": "application/json"}) as response:
            response.raise_for_status()
            return response.json()

    def get_item(self, key: str): 
        url = f"https://api.zotero.org/users/{self.zotero_user_id}/items/{key}"
        with requests.get(url, headers={"Authorization": f"Bearer {self.zotero_api_key}",
                                                  "Accept": "application/json"}) as response:
            response.raise_for_status()
            return response.json()
    
    def get_document(self, key: str):
        document_json = self.get_item(key)
        document = ZoteroDocument(**document_json)
        return document
    
    def get_document_child_notes(self, parent_key: str):
        url = f"https://api.zotero.org/users/{self.zotero_user_id}/items/{parent_key}/children?itemType=note"
        with requests.get(url, headers={"Authorization": f"Bearer {self.zotero_api_key}",
                                                    "Accept": "application/json"}) as response:
            response.raise_for_status()
            return [ZoteroNote(**note) for note in response.json()]
                
    def get_attachment_items(self, parent_key: str):
        url = f"https://api.zotero.org/users/{self.zotero_user_id}/items/{parent_key}/children?itemType=attachment"
        with requests.get(url, headers={"Authorization": f"Bearer {self.zotero_api_key}",
                                                    "Accept": "application/json"}) as response:
            response.raise_for_status()
            return [ZoteroAttachment(**attachment) for attachment in response.json()]
    
    def get_file(self, item_key: str):
        url = f"https://api.zotero.org/users/{self.zotero_user_id}/items/{item_key}/file"
        with self.session.get(url, headers={"Authorization": f"Bearer {self.zotero_api_key}",
                                                    "Accept": "application/json"}) as response:
            response.raise_for_status()
            if 'application/zip' in response.headers.get('Content-Type', ''):
                return self._process_zip_file(response.read())
            else:
                raise ValueError("Expected HTML file, received: {}".format(response.headers['Content-Type']))
    
    def _process_zip_file(self, zip_content):
        zip_file = BytesIO(zip_content)
        with zipfile.ZipFile(zip_file, 'r') as z:
            for filename in z.namelist():
                if filename.endswith('.html'):
                    with z.open(filename) as html_file:
                        html_content = html_file.read().decode('utf-8')
                        return html_content
            raise ValueError("No HTML file found in the ZIP archive")
    

    def get_attachment_highlights_pdf(self, key: str):
        url = f"https://api.zotero.org/users/{self.zotero_user_id}/items/{key}/children"
        with requests.get(url, headers={"Authorization": f"Bearer {self.zotero_api_key}",
                                                    "Accept": "application/json"}) as response:
            response.raise_for_status()

            highlights = []
            for highlight in response.json():
                if highlight.get('data', {}).get('annotationType') == 'highlight':
                    highlights.append(ZoteroAttachmentHighlight(**highlight))
            return highlights

    def get_attachment_notes_pdf(self, key: str):
        url = f"https://api.zotero.org/users/{self.zotero_user_id}/items/{key}/children"
        with requests.get(url, headers={"Authorization": f"Bearer {self.zotero_api_key}",
                                                    "Accept": "application/json"}) as response: 

            response.raise_for_status()
            notes = []
            for note in response.json():
                if note.get('data', {}).get('annotationType') == 'note':
                    notes.append(ZoteroAttachmentNote(**note))
            return notes
    
    def get_attachment_annotations_kindle(self, parent_key, notebook):
        soup = BeautifulSoup(notebook, 'html.parser')
        text_elements = soup.find_all('div', class_='noteText')
        highlights = []
        for i, highlight in enumerate(text_elements):
            highlights.append(
                ZoteroAttachmentHighlight(
                    key=f"{parent_key}-highlight-{i}",
                    data=ZoteroAttachmentHighlightData(
                        annotationText=highlight.get_text(),
                        dateModified=datetime.now().isoformat()
                    )
                )
            )
        return highlights
    
    def get_attachment_annotations(self, parent_key: str):
        attachments = self.get_attachment_items(parent_key)

        notes = []
        annotations = []
        
        for attachment in attachments:
            if attachment.data.filename.endswith(".pdf"):
                annotations.append(self.get_attachment_highlights_pdf(attachment.key))
                notes.append(self.get_attachment_notes_pdf(attachment.key))
            elif attachment.data.filename.endswith("Notebook.html"):
                notebook = self.get_file(attachment.key)
                annotations.append(self.get_attachment_annotations_kindle(attachment.key, notebook))
        
        return annotations, notes

