from pymongo import MongoClient
import re
from collections import defaultdict
import nltk
from nltk.tokenize import word_tokenize

client = MongoClient('localhost', 27017)
db = client['ASRSDB']
collection = db.asrs

# Placeholder dictionary (expand later with more data or via NLP methods)
abbrev_dict = {
    "AC": "aircraft",
    "ATC": "air traffic control",
    "RWY": "runway"
}

def expand_abbreviations(text, abbrev_dict):
    pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in abbrev_dict.keys()) + r')\b')
    return pattern.sub(lambda x: abbrev_dict[x.group()], text)

def flatten_document(doc, parent_key='', sep='.'):
    items = []
    for k, v in doc.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_document(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                items.extend(flatten_document({f"{k}_{i}": item}, new_key, sep=sep).items())
        else:
            items.append((new_key, str(v)))
    return dict(items)
