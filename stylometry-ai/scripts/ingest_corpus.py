"""Ingestion de textes bruts vers un corpus StyloScan.

Extrait le texte de fichiers .pdf / .docx / .md / .txt, le nettoie, le
découpe en échantillons de taille homogène, détecte la langue et range le
tout dans  <corpus>/<label>/<lang>/  (le latin, non supporté par les
features FR/EN/NL, est isolé dans  _latin_unsupported/  et exclu de
l'entraînement).

Usage :
    PYTHONPATH=. python3 scripts/ingest_corpus.py \
        --out corpus --label human --target-words 450 --min-words 200 \
        fichier1.pdf fichier2.md ...
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from styloscan.languages import detect_language, FUNCTION_WORDS
from styloscan.features import tokenize

# Mots-outils latins pour reconnaître (et écarter) le latin, non supporté.
_LATIN_FW = {"et", "in", "est", "non", "ad", "ut", "cum", "qui", "quae",
             "quod", "sed", "si", "ex", "de", "per", "atque", "enim", "autem",
             "nam", "esse", "sunt", "hoc", "haec", "nec", "ne", "ita", "quam"}


def extract_pdf(path: str) -> str:
    import fitz
    doc = fitz.open(path)
    parts = [page.get_text("text") for page in doc]
    doc.close()
    return "\n".join(parts)


def extract_docx(path: str) -> str:
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
    # Les paragraphes sont des <w:p> ; le texte est dans les <w:t>.
    paras = re.split(r"</w:p>", xml)
    out = []
    for p in paras:
        texts = re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, flags=re.DOTALL)
        line = "".join(texts)
        line = re.sub(r"<[^>]+>", "", line)
        if line.strip():
            out.append(line.strip())
    return "\n\n".join(out)


def clean_markdown(text: str) -> str:
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith(("> ", ">", "#")):      # citations Zotero, callouts, titres
            s = re.sub(r"^[>#\s]+", "", s)
        if re.match(r"^\[\^\w+\]:", s):          # définitions de notes de bas de page
            continue
        if re.match(r"^\^[\w]+$", s):            # ancres Zotero (^GI3C4N3...)
            continue
        if s in ("---", "[!note]") or s.startswith("[!"):
            continue
        # On PRÉSERVE les lignes vides : ce sont les séparateurs de paragraphe.
        lines.append(ln)
    text = "\n".join(lines)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)   # commentaires HTML
    text = re.sub(r"={2,}", "", text)                          # surlignage ==..==
    text = re.sub(r"\[\^\w+\]", "", text)                      # appels de note [^1]
    text = re.sub(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", r"\1", text)  # [[wikilinks]]
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)       # [texte](url)
    text = re.sub(r"https?://\S+", "", text)                   # URLs nues
    text = re.sub(r"\(\s*\d+\s*\)", "", text)                  # numéros de page (485)
    return text


def normalize(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"-\n(?=[a-zà-ö])", "", text)   # césures de fin de ligne
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        raw = extract_pdf(path)
    elif ext == ".docx":
        raw = extract_docx(path)
    elif ext in (".md", ".markdown"):
        raw = clean_markdown(_read(path))
    else:
        raw = _read(path)
    return normalize(raw)


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def detect_lang_ext(text: str) -> str:
    """Comme detect_language mais reconnaît aussi le latin ('la')."""
    toks = [t.lower() for t in tokenize(text)]
    if not toks:
        return "en"
    lat = sum(1 for t in toks if t in _LATIN_FW)
    best_mod = detect_language(text)
    mod_hits = sum(1 for t in toks if t in set(FUNCTION_WORDS[best_mod]))
    # Le latin l'emporte s'il domine nettement les mots-outils modernes.
    if lat > mod_hits * 1.1 and lat >= 5:
        return "la"
    return best_mod


def chunk(text: str, target_words: int, min_words: int):
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, buf, n = [], [], 0
    for p in paras:
        w = len(tokenize(p))
        buf.append(p)
        n += w
        if n >= target_words:
            chunks.append("\n\n".join(buf))
            buf, n = [], 0
    if n >= min_words and buf:
        chunks.append("\n\n".join(buf))
    elif buf and chunks:                  # rattacher le reliquat trop court
        chunks[-1] += "\n\n" + "\n\n".join(buf)
    return chunks


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", default="corpus")
    ap.add_argument("--label", default="human")
    ap.add_argument("--target-words", type=int, default=450)
    ap.add_argument("--min-words", type=int, default=200)
    ap.add_argument("--by-language", action="store_true", default=True)
    args = ap.parse_args(argv)

    summary = []
    for path in args.inputs:
        base = re.sub(r"[^A-Za-z0-9]+", "_", os.path.splitext(os.path.basename(path))[0])[:40]
        text = extract(path)
        total_words = len(tokenize(text))
        chunks = chunk(text, args.target_words, args.min_words)
        per_lang = {}
        for i, ch in enumerate(chunks):
            lang = detect_lang_ext(ch)
            per_lang.setdefault(lang, 0)
            per_lang[lang] += 1
            if lang == "la":
                sub = os.path.join(args.out, "_latin_unsupported")
            else:
                sub = os.path.join(args.out, args.label, lang)
            os.makedirs(sub, exist_ok=True)
            with open(os.path.join(sub, f"{base}_{i:03d}.txt"), "w", encoding="utf-8") as fh:
                fh.write(ch)
        summary.append((os.path.basename(path), total_words, len(chunks), per_lang))

    print(f"{'fichier':45s} {'mots':>7s} {'samples':>8s}  langues")
    print("-" * 78)
    for name, words, n, langs in summary:
        lg = ", ".join(f"{k}:{v}" for k, v in sorted(langs.items()))
        print(f"{name[:45]:45s} {words:7d} {n:8d}  {lg or '—'}")


if __name__ == "__main__":
    main()
