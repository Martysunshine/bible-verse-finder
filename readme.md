BibleVerse Finder
=================

Given a 10+ word description, this app suggests 3–5 relevant Bible passages using local Sentence-Transformers embeddings and an optional Cross-Encoder reranker. No paid APIs.

Quickstart
----------

```bash
npm install
npm run dev
```

That’s it. On first run the setup script will:
1. Create a Python virtual environment (`.venv`)
2. Install pip dependencies (`backend/requirements.txt`)
3. Build verse embeddings (downloads models — may take a few minutes the first time)
4. Install frontend npm packages

Once ready, both servers start concurrently:
- **API** → http://localhost:8000
- **UI**  → http://localhost:5173

Open http://localhost:5173, enter 10+ words, click **Suggest Passages**.

### Manual setup (optional)

```pwsh
# Backend
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python backend\prepare_bible.py
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Prerequisites
-------------

- Python 3.10+ (3.11/3.12/3.13 OK)
- Node 18+

Project structure
-----------------

```
bible-verse-finder/
├─ package.json               # Root: npm run dev starts everything
├─ scripts/
│  ├─ setup.js               # Auto-creates venv, installs deps, builds embeds
│  └─ start-backend.js       # Launches uvicorn from the venv
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
│     └─ meta.json           # verse metadata (book/chapter/verse/text)
└─ frontend/
   ├─ index.html
   ├─ vite.config.js          # Proxies /recommend, /health to backend
   ├─ package.json
   └─ src/
      ├─ main.jsx
      └─ App.jsx
```

API reference
-------------

- GET `/` → basic info
- GET `/health` → `{ ok, verses, reranker }`
- POST `/recommend`
  - Request: `{ text: string, k?: number (default 3), candidates?: number (default 40) }`
  - Response: `{ query, results: [{ book, chapter, verse, text, score, why }] }`

Swap in the full Bible
----------------------

1. Replace `backend/data/bible_sample.csv` with a full CSV (columns: `book,chapter,verse,text`).
2. Delete `backend/data/verses.npy` and `backend/data/meta.json`.
3. Run `npm run dev` again — embeddings rebuild automatically.

Troubleshooting
---------------

- **“Failed to fetch” in the UI** — Ensure backend is running; the Vite proxy forwards `/recommend` to port 8000.
- **400 “Please enter at least 10 words”** — Provide more context in your description.
- **Slow first run** — Models download on first use; embeddings build can take a few minutes.

Notes
-----

- Works offline after first model download and embedding build.
- Optional reranker (Cross-Encoder) loads automatically if available.
- To index paragraphs instead of verses, preprocess the CSV to paragraph rows and re-run `prepare_bible.py`.
