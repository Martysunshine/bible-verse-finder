from __future__ import annotations

import json
from urllib.request import urlopen, Request

BASE = 'http://127.0.0.1:8000'


def get(path: str):
    with urlopen(BASE + path) as r:
        return json.loads(r.read().decode('utf-8'))


def post(path: str, body: dict):
    data = json.dumps(body).encode('utf-8')
    req = Request(BASE + path, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    with urlopen(req) as r:
        return json.loads(r.read().decode('utf-8'))


if __name__ == '__main__':
    print('GET /health =>')
    print(get('/health'))
    print()
    print('POST /recommend =>')
    sample = {
        'text': "Yesterday I had a dream about sunshine and a ship full of animals like Noah's ark, feeling hope for a better tomorrow.",
        'k': 3,
    }
    rec = post('/recommend', sample)
    print({'query': rec.get('query'), 'n': len(rec.get('results', []))})
    for i, r in enumerate(rec.get('results', []), 1):
        print(f"{i}. {r['book']} {r['chapter']}:{r['verse']} | {r['score']:.3f} | {r['why']}")
        print(r['text'])
        print()
