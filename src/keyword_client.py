import os
import re
import spacy
from dotenv import load_dotenv
import json
from collections import Counter
from itertools import chain
from document_client import Document

class KeywordClient:

    def __init__(self, data_path: str, keywords: list = []):
        self.data_path = data_path

        if keywords:
            self.keywords = keywords
        else:
            self.keywords = self.detect_keywords()
    
    def extract_named_entities(self, corpus):
        nlp = spacy.load("en_core_web_sm")
        all_entities = []
        for doc_text in corpus:
            doc = nlp(doc_text)
            for ent in doc.ents:
                all_entities.append(ent.text.strip())
        
        return Counter(all_entities)

    def document_to_corpus(self, key):
        with open(f"{self.data_path}/{key}.json") as file:
            document = Document.model_validate(json.load(file))
        
        corpus = []
        
        for note in document.notes:
            corpus.append(note.text)
        
        for highlight in document.annotations:
            corpus.append(highlight.text)
        
        return corpus

    def detect_keywords(self):
        '''
        Extract named entities from the corpus of documents
        '''
        corpus = []
        for file in os.listdir(self.data_path):
            key = file.replace('.json', '')
            corpus.extend(self.document_to_corpus(key))
        
        named_entity_counts = self.extract_named_entities(corpus)
        # Drop any entities that contain numbers
        named_entity_counts = {k: v for k, v in named_entity_counts.items() if not any(char.isdigit() for char in k)}
        # Remove starting string "the " from entities
        named_entity_counts = {k[4:] if k.startswith("the ") else k: v for k, v in named_entity_counts.items()}
        # Select entities mentioned more than once
        named_entity_counts = {k: v for k, v in named_entity_counts.items() if v > 1}

        return set(named_entity_counts.keys())
    
    def highlight_keywords(self, text):
        try:
            escaped_keywords = [re.escape(k) for k in self.keywords]
            
            pattern = re.compile(r'\b(' + '|'.join(escaped_keywords) + r')\b', flags=re.IGNORECASE)
            
            def replace_func(match):
                return f'[[{match.group(1)}]]'
        
            return pattern.sub(replace_func, text)
        except TypeError:
            return text
    
    def write_keyword_pages(self):
        pass

if __name__ == "__main__":
    # Output detected keywords to a file
    load_dotenv()
    keyword_client = KeywordClient(data_path=os.getenv('DATA_PATH'))
    keywords = keyword_client.detect_keywords()
    with open(f"{os.getenv('KEYWORD_PATH')}/ner_results.txt", 'w') as file:
        for k in keywords:
            file.write(f"{k}\n")


