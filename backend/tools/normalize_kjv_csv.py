import os
import pandas as pd

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

    df = pd.read_csv(IN, sep=None, engine="python")

    cols = df.columns
    book_c = pick(cols, "book","book_name","Book","bookName","BookName","osis","book_id","bookId")
    chap_c = pick(cols, "chapter","chapterNumber","chapter_nr","Chapter","chapter_num","ch")
    vers_c = pick(cols, "verse","verseNumber","verse_nr","Verse","verse_num","v")
    text_c = pick(cols, "text","verse_text","content","value","t","body","Text")

    if book_c is None or chap_c is None or vers_c is None or text_c is None:
        raise SystemExit(f"Could not detect columns. Found: {list(cols)}")

    # Map book names if numeric or OSIS codes
    book_series = df[book_c]
    if pd.api.types.is_integer_dtype(book_series) or pd.api.types.is_float_dtype(book_series):
        # 1..66 → names
        df["book"] = book_series.astype(int).apply(lambda n: book_names[n-1] if 1 <= n <= 66 else f"Book{n}")
    else:
        # keep as string
        df["book"] = book_series.astype(str)

    norm = pd.DataFrame({
        "book": df["book"].astype(str),
        "chapter": df[chap_c].astype(int),
        "verse": df[vers_c].astype(int),
        "text": df[text_c].astype(str).str.strip(),
    })

    norm.to_csv(OUT, index=False, encoding="utf-8")
    print("Wrote", OUT, "rows:", len(norm))


if __name__ == "__main__":
    main()
