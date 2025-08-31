from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, json, re
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
EMB_PATH = os.path.join(DATA_DIR, 'verses.npy')
META_PATH = os.path.join(DATA_DIR, 'meta.json')

# Optionally auto-build artifacts
AUTO_BUILD = os.getenv('AUTO_BUILD_EMBEDS', '1') != '0'
if AUTO_BUILD and not (os.path.exists(EMB_PATH) and os.path.exists(META_PATH)):
        import subprocess, sys
        subprocess.check_call([sys.executable, os.path.join(os.path.dirname(__file__), 'prepare_bible.py')])

# Load data
emb = np.load(EMB_PATH)
with open(META_PATH, 'r', encoding='utf-8') as f:
	meta = json.load(f)

# Normalize embeddings (safety) for cosine similarity
def l2_normalize(x: np.ndarray) -> np.ndarray:
	denom = np.linalg.norm(x, axis=1, keepdims=True) + 1e-12
	return x / denom

emb = l2_normalize(emb.astype(np.float32))

# Encoder for queries
from sentence_transformers import SentenceTransformer
EMB_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
encoder = SentenceTransformer(EMB_MODEL)

# Optional reranker
RERANKER = None
try:
	from sentence_transformers import CrossEncoder
	RERANKER = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
except Exception:
	RERANKER = None

# Minimal stopwords for quick keyword overlap
STOP = set('''a an and are as at be but by for from has have i in is it its nor not of on or so that the their there these this to was were will with your you're you'''.split())
TOKEN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")

def tokenize(s: str):
	return [w.lower() for w in TOKEN.findall(s)]

def keywords(s: str, topk=6):
	toks = [t for t in tokenize(s) if t not in STOP]
	if not toks:
		return []
	from collections import Counter
	return [w for w,_ in Counter(toks).most_common(topk)]

class RecommendReq(BaseModel):
	text: str
	k: int = 3
	candidates: int = 40

class Passage(BaseModel):
	book: str
	chapter: int
	verse: int
	text: str
	score: float
	why: str

class RecommendRes(BaseModel):
	query: str
	results: list[Passage]

app = FastAPI(title='BibleVerse Finder — AI Copilot')
app.add_middleware(
	CORSMiddleware,
	allow_origins=['*'],
	# Credentials not needed; keep wildcard origins valid to avoid CORS errors in browsers
	allow_credentials=False,
	allow_methods=['*'],
	allow_headers=['*'],
)

@app.get('/')
def root():
	return {
		'title': 'BibleVerse Finder — API',
		'health': '/health',
		'recommend': '/recommend',
		'models': {
			'encoder': EMB_MODEL,
			'reranker': bool(RERANKER)
		}
	}

@app.get('/health')
def health():
	return {'ok': True, 'verses': len(meta), 'reranker': bool(RERANKER)}

@app.post('/recommend', response_model=RecommendRes)
def recommend(req: RecommendReq):
	# 1) Basic validation (10+ words)
	words = [w for w in tokenize(req.text)]
	if len(words) < 10:
		raise HTTPException(status_code=400, detail='Please enter at least 10 words for better context.')

	k_final = max(3, min(10, req.k))
	n_cand = max(k_final, min(100, req.candidates))

	# 2) Encode query and retrieve top-N by cosine
	q_vec = encoder.encode([req.text], normalize_embeddings=True).astype(np.float32)
	q = q_vec[0]
	sims = (emb @ q)  # since both are normalized, dot == cosine
	# get top n_cand indices
	n = min(n_cand, sims.shape[0])
	top_idx = np.argpartition(-sims, kth=n-1)[:n]
	# sort selected by similarity desc
	top_sorted = top_idx[np.argsort(-sims[top_idx])]
	candidates = [(float(sims[i]), int(i)) for i in top_sorted]

	# 3) Optional rerank with cross-encoder
	if RERANKER is not None:
		pairs = [(req.text, meta[i]['text']) for _,i in candidates]
		rerank_scores = RERANKER.predict(pairs)
		enriched = list(zip(rerank_scores.tolist(), candidates))
		enriched.sort(key=lambda x: x[0], reverse=True)
		ranked = [(float(cs), i) for (cs, (_sim, i)) in enriched]
		from math import tanh
		ranked = [((tanh(s/5)+1)/2, i) for s,i in ranked]
		top = ranked[:k_final]
		selected = [(score, i) for score, i in top]
	else:
		selected = candidates[:k_final]

	q_keys = keywords(req.text, topk=6)
	results = []
	for score, i in selected:
		v = meta[i]
		v_keys = keywords(v['text'], topk=6)
		overlap = [kw for kw in q_keys if kw in set(v_keys)]
		why_bits = []
		if overlap:
			why_bits.append('matches themes: ' + ', '.join(overlap))
		why = '; '.join(why_bits) if why_bits else 'strong semantic match to your description'
		results.append(Passage(
			book=str(v['book']),
			chapter=int(v['chapter']),
			verse=int(v['verse']),
			text=str(v['text']),
			score=float(score),
			why=why
		))

	return RecommendRes(query=req.text, results=results)

# For local dev: uvicorn app:app --reload --port 8000