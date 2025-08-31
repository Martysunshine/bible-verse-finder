"""
Quick smoke test: import recommend() and run a sample query, printing top results.
Run with the project venv:

  C:\Users\marti\Documents\GitHub\bible-verse-finder\.venv\Scripts\python.exe backend\smoke_test.py
"""
from __future__ import annotations

from app import recommend, RecommendReq


SAMPLE = (
    "Yesterday I had a dream about sunshine and a ship full of animals like Noah's ark, "
    "feeling hope for a better tomorrow."
)


def main():
    req = RecommendReq(text=SAMPLE, k=3)
    res = recommend(req)
    print(f"OK results: {len(res.results)}\n")
    for r in res.results:
        print(f"{r.book} {r.chapter}:{r.verse} | {r.score:.3f} | {r.why}")
        print(r.text)
        print()


if __name__ == "__main__":
    main()
