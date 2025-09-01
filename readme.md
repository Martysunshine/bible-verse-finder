BibleVerse Finder
=================

Given a 10+ word description, this app suggests 3–5 relevant Bible passages using local Sentence-Transformers embeddings and an optional Cross-Encoder reranker. No paid APIs.

Quickstart (Windows PowerShell)
-------------------------------

```pwsh
# From the repo root
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt

# Build embeddings once (first run downloads models and can take a few minutes)
python backend\prepare_bible.py

# Start the API
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000

# In a new terminal: start the UI
cd frontend
$env:VITE_API_BASE='http://127.0.0.1:8000'
npm install
npm run dev
```

Open http://localhost:5173, enter 10+ words, then click “Suggest Passages”.

Project structure
-----------------

```
bible-verse-finder/
├─ backend/
│  ├─ app.py                 # FastAPI app (GET /, /health, POST /recommend)
│  ├─ prepare_bible.py       # Build embeddings from CSV (runs once)
│  ├─ requirements.txt
│  ├─ smoke_test.py          # Quick local test for recommend()
│  ├─ test_api.py            # Tiny HTTP test for running server
│  └─ data/
│     ├─ bible_sample.csv    # small CSV to start
│     ├─ bible_full.csv      # full KJV CSV (book,chapter,verse,text)
│     ├─ verses.npy          # auto-generated embeddings
│     ├─ meta.json           # verse metadata (book/chapter/verse/text)
│     └─ kjv.json.csv        # raw/alternate CSV source (optional)
└─ frontend/
	 ├─ index.html
	 ├─ vite.config.js
	 ├─ package.json
	 └─ src/
			├─ main.jsx
			└─ App.jsx
```

Prerequisites
-------------

- Windows PowerShell
- Python 3.10+ (3.11/3.12/3.13 OK)
- Node 18+

Backend (FastAPI)
-----------------

```pwsh
# From the repo root
. .\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt

# Build embeddings once (first run will download models and take a few minutes)
python backend\prepare_bible.py

# Start API (use --reload during development if preferred)
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
# or with reload:
# python -m uvicorn backend.app:app --reload --port 8000
```

Sanity checks (new terminal):

- Health
```pwsh
Invoke-RestMethod -UseBasicParsing http://localhost:8000/health | ConvertTo-Json -Depth 5
```

- Recommend (POST /recommend)
```pwsh
$body = @{ text = "Yesterday I had a dream about sunshine and a ship full of animals like Noah's ark, feeling hope for a better tomorrow."; k = 3 } | ConvertTo-Json -Compress
Invoke-RestMethod -UseBasicParsing http://localhost:8000/recommend -Method Post -ContentType 'application/json' -Body $body | ConvertTo-Json -Depth 5
```

Frontend (React + Vite)
-----------------------

```pwsh
cd frontend
npm i

# Point UI at backend API (adjust if needed)
"VITE_API_BASE=http://localhost:8000" | Out-File -FilePath .env.local -Encoding ascii

npm run dev
```

Open http://localhost:5173, enter 10+ words, then click “Suggest Passages”.

Swap in the full Bible
----------------------

1) Replace `backend/data/bible_sample.csv` with a full CSV (columns: `book,chapter,verse,text`).

2) Rebuild embeddings:
```pwsh
cd backend
. .venv\Scripts\Activate.ps1
python prepare_bible.py
```

3) Restart Uvicorn.

API reference (brief)
---------------------

- GET `/` → basic info
- GET `/health` → `{ ok: boolean, verses: number, reranker: boolean }`
- POST `/recommend`
	- Request JSON: `{ text: string, k?: number (default 3), candidates?: number (default 40) }`
	- Response JSON: `{ query: string, results: { book, chapter, verse, text, score, why }[] }`

Deployment (quick)
------------------

Backend (Render)
- Root: `backend/`
- Build: `pip install -r requirements.txt && python prepare_bible.py`
- Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`

Backend (Vercel)
- Root: `backend/`
- Build: `pip install -r requirements.txt && python prepare_bible.py`
- Env: `AUTO_BUILD_EMBEDS=0`
- Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`

Frontend (Vercel)
- Root: `frontend/`
- Env: `VITE_API_BASE=https://YOUR-BACKEND.onrender.com`
- Build: `npm run build`, Output: `dist`

Troubleshooting
---------------

- “Failed to fetch” in the UI
	- Ensure backend is running on http://localhost:8000
	- Ensure `frontend/.env.local` points `VITE_API_BASE` to the backend
	- Restart `npm run dev` after editing `.env.local`

- 400 error “Please enter at least 10 words”
	- Provide more context in your description; the model uses richer input.

- Slow first run
	- Models download on first use; embeddings build can take a few minutes.

- Python 3.13 + pandas
	- No action required. The backend does not depend on pandas for runtime; `prepare_bible.py` reads CSV with the stdlib `csv` module.

Notes
-----

- Works offline after first model download and embedding build.
- Optional reranker (Cross-Encoder) loads automatically if available; if loading fails due to memory or dependencies, the API falls back to semantic-only ranking.
- To index paragraphs instead of verses, preprocess the CSV to paragraph rows and re-run `prepare_bible.py`.