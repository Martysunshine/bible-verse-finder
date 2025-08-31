"""
Build embeddings from a Bible CSV once. Columns: book,chapter,verse,text
"""
import csv
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CSV_PATH = os.getenv('BIBLE_CSV', os.path.join(DATA_DIR, 'bible_full.csv'))
EMB_PATH = os.path.join(DATA_DIR, 'verses.npy')
META_PATH = os.path.join(DATA_DIR, 'meta.json')
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'


if not os.path.exists(CSV_PATH):
	raise FileNotFoundError(f"CSV not found: {CSV_PATH}")


# Read CSV without pandas
meta: list[dict] = []
texts: list[str] = []
with open(CSV_PATH, 'r', encoding='utf-8') as f:
	reader = csv.DictReader(f)
	required = {'book', 'chapter', 'verse', 'text'}
	if not required.issubset(reader.fieldnames or []):
		raise ValueError(f"CSV must contain columns: {required}")
	for row in reader:
		book = str(row['book']).strip()
		chapter = int(row['chapter']) if str(row['chapter']).strip() else 0
		verse = int(row['verse']) if str(row['verse']).strip() else 0
		text = str(row['text']).strip()
		texts.append(text)
		meta.append({
			'book': book,
			'chapter': chapter,
			'verse': verse,
			'text': text,
		})

model = SentenceTransformer(MODEL_NAME)
print('Encoding verses (this runs once)…')
embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
np.save(EMB_PATH, embeddings)

with open(META_PATH, 'w', encoding='utf-8') as f:
	json.dump(meta, f, ensure_ascii=False)

print('Saved embeddings to', EMB_PATH)
print('Saved meta to', META_PATH)