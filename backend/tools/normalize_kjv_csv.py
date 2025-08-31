"""Normalize raw KJV CSV into a standard format without pandas."""

import csv
import os

IN = os.path.join(os.path.dirname(__file__), "..", "data", "kjv.json.csv")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "bible_full.csv")

book_names = [
    "Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth",
    "1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra","Nehemiah",
    "Esther","Job","Psalms","Proverbs","Ecclesiastes","Song of Solomon","Isaiah","Jeremiah",
    "Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah","Jonah","Micah","Nahum",
    "Habakkuk","Zephaniah","Haggai","Zechariah","Malachi","Matthew","Mark","Luke","John",
    "Acts","Romans","1 Corinthians","2 Corinthians","Galatians","Ephesians","Philippians",
    "Colossians","1 Thessalonians","2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon",
    "Hebrews","James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation"
]


def pick(cols, *cands):
    for c in cands:
        if c in cols:
            return c
    return None


def main():
    if not os.path.exists(IN):
        raise SystemExit(f"Input CSV not found: {IN}")

    with open(IN, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        book_c = pick(cols, "book","book_name","Book","bookName","BookName","osis","book_id","bookId")
        chap_c = pick(cols, "chapter","chapterNumber","chapter_nr","Chapter","chapter_num","ch")
        vers_c = pick(cols, "verse","verseNumber","verse_nr","Verse","verse_num","v")
        text_c = pick(cols, "text","verse_text","content","value","t","body","Text")

        if book_c is None or chap_c is None or vers_c is None or text_c is None:
            raise SystemExit(f"Could not detect columns. Found: {list(cols)}")

        rows: list[dict[str, object]] = []
        for row in reader:
            book_raw = row.get(book_c, "")
            try:
                num = int(float(book_raw))
                if 1 <= num <= 66:
                    book = book_names[num-1]
                else:
                    book = f"Book{num}"
            except (TypeError, ValueError):
                book = str(book_raw).strip()

            def parse_int(val: object) -> int:
                try:
                    return int(float(val))
                except (TypeError, ValueError):
                    return 0

            chapter = parse_int(row.get(chap_c))
            verse = parse_int(row.get(vers_c))
            text = str(row.get(text_c, "")).strip()

            rows.append({
                "book": book,
                "chapter": chapter,
                "verse": verse,
                "text": text,
            })

    with open(OUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["book", "chapter", "verse", "text"])
        writer.writeheader()
        writer.writerows(rows)

    print("Wrote", OUT, "rows:", len(rows))


if __name__ == "__main__":
    main()
