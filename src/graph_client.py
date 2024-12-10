import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
from typing import Any
from document_client import Document, DocumentNote
from pydantic import BaseModel
from typing import List

class Annotation(BaseModel):
    type: str
    text: str
    mtime: str

def get_ordinal_suffix(day: int) -> str:
    if 11 <= day <= 13:
        return 'th'
    else:
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

class GraphClient:
    def __init__(self, data_path: str, graph_path: str, template_path: str):
        self.data_path = data_path
        self.graph_path = graph_path
        self.env = Environment(loader=FileSystemLoader(template_path))

    def sanitize(self, text: str) -> str:
        return text.replace('/', '_').replace(':', '_')

    def get_document_annotations(self, document: Document) -> List[Annotation]:
        annotations = sorted(document.notes + document.annotations, key=lambda x: x.mtime)
        for i, annotation in enumerate(annotations):
            dt = datetime.strptime(annotation.mtime, '%Y-%m-%dT%H:%M:%SZ')
            day = dt.day
            ordinal_suffix = get_ordinal_suffix(day)
            annotations[i].mtime = dt.strftime(f'%b {day}{ordinal_suffix}, %Y')
            if type(annotation) == DocumentNote:
                annotations[i] = Annotation(type='note', text=annotation.text, mtime=annotation.mtime)
            else:
                annotations[i] = Annotation(type='highlight', text=annotation.text, mtime=annotation.mtime)
        return annotations

    def write_document_page(self, key: str):
        with open(f"{self.data_path}/{key}.json") as file:
            document = Document.parse_obj(json.load(file))
        template = self.env.get_template('document_page_template.md')
        annotations = self.get_document_annotations(document)
        page_content = template.render(document=document, annotations=annotations)

        if len(annotations) > 0:           
            filename = f"{self.graph_path}/pages/{self.sanitize(document.title)}.md"
            with open(filename, 'w') as file:
                file.write(page_content)
        
    def delete_document_page(self, key: str):
        with open(f"{self.data_path}/{key}.json") as file:
            document = Document.parse_obj(json.load(file))
        
        filename = f"{self.graph_path}/pages/{self.sanitize(document.title)}.md"
        os.remove(filename)

    def write_journal_page(self, date: datetime):
        dt = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
        day = dt.day
        ordinal_suffix = get_ordinal_suffix(day)
        format_dt = dt.strftime(f'%b {day}{ordinal_suffix}, %Y')
        fn_dt = dt.strftime(f'%Y_%m_%d')
        content = f"{{{{query (and (property mtime <% {format_dt} %>))}}}}"
        if not os.path.exists(f"{self.graph_path}/journals/{fn_dt}.md"):
            with open(f"{self.graph_path}/journals/{fn_dt}.md", 'w') as file:
                file.write(content)
    
    def sync_graph(self):
        for file in os.listdir(self.data_path):
            if file.endswith('.json'):
                key = file.replace('.json', '')
                self.write_document_page(key)

    def backfill_journal_pages(self, n_days=90):
        date_now = datetime.now()
        past_3_months = [date_now - timedelta(days=x) for x in range(n_days)]
        past_3_months = [date.strftime('%Y-%m-%dT%H:%M:%SZ') for date in past_3_months]
        for date in past_3_months:
            self.write_journal_page(date)

if __name__ == "__main__":
    # Backfill journal pages for the past 3 months with a query for notes and highlights
    load_dotenv()
    gc = GraphClient(os.getenv('DATA_PATH'), os.getenv('GRAPH_PATH'), os.getenv('TEMPLATE_PATH'))
    gc.sync_graph()
    gc.backfill_journal_pages()