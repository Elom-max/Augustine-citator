"""Extraction de features stylométriques interprétables.

Chaque texte est transformé en un vecteur de features nommées, regroupées
en catégories (à la StyloAI : diversité lexicale, complexité syntaxique,
lisibilité, marqueurs, unicité/variété). C'est l'analogue, pour la
détection d'usage d'IA dans l'écrit scientifique, du jeu de 26 features
latines du chapitre de référence : des grandeurs simples, comptables à la
main, et donc *interprétables*.

Toutes les features sont calculées à partir du texte brut : segmentation
en phrases et tokenisation par expressions régulières, sans modèle NLP à
télécharger. Les choix (ex. définition de la « burstiness ») sont
documentés ligne à ligne.
"""

from __future__ import annotations

import math
import re
import zlib
from collections import Counter
from dataclasses import dataclass, field

from . import languages as L

_WORD_RE = re.compile(r"[^\W\d_]+(?:['’\-][^\W\d_]+)*", re.UNICODE)
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?…])[\"'”’\)\]]?\s+(?=[A-ZÀ-ÖØ-Þ0-9«\"'])")


def split_sentences(text: str):
    text = text.strip()
    if not text:
        return []
    parts = _SENT_SPLIT_RE.split(text)
    return [p.strip() for p in parts if p.strip()]


def tokenize(text: str):
    return _WORD_RE.findall(text)


def _count_phrases(text_lower: str, phrases) -> int:
    n = 0
    for p in phrases:
        if " " in p:
            n += text_lower.count(p)
        else:
            n += len(re.findall(r"\b" + re.escape(p) + r"\b", text_lower))
    return n


def _safe_div(a, b):
    return a / b if b else 0.0


@dataclass
class FeatureResult:
    language: str
    n_words: int
    n_sentences: int
    n_paragraphs: int = 1
    features: dict = field(default_factory=dict)

    def vector(self, names):
        return [self.features.get(n, 0.0) for n in names]


# Ordre canonique des features (sert de schéma de vecteur, comme le
# Tableau 6.1 du chapitre). Regroupées par catégorie.
FEATURE_CATEGORIES = {
    "Diversité lexicale": [
        "ttr", "mattr_50", "hapax_ratio", "yule_k", "mean_word_len",
    ],
    "Complexité syntaxique": [
        "mean_sent_len", "sd_sent_len", "cv_sent_len", "burstiness",
        "commas_per_sent", "subordination_ratio", "interrogative_ratio",
    ],
    "Lisibilité": [
        "syllables_per_word", "long_word_ratio", "readability_proxy",
    ],
    "Mots-outils & connecteurs": [
        "function_word_ratio", "transition_density",
    ],
    "Marqueurs d'IA": [
        "ai_marker_density", "hedge_density", "emdash_per_1k",
        "curly_quote_ratio", "contraction_ratio", "list_marker_ratio",
    ],
    "Unicité & variété": [
        "distinct_bigram_ratio", "distinct_trigram_ratio",
        "bigram_repetition", "compression_ratio",
        "sent_initial_repetition", "paragraph_len_cv",
    ],
}

FEATURE_NAMES = [n for names in FEATURE_CATEGORIES.values() for n in names]

# Glossaire FR court pour les rapports.
FEATURE_GLOSSARY = {
    "ttr": "Type-Token Ratio : vocabulaire distinct / total.",
    "mattr_50": "TTR moyen mobile (fenêtre 50 mots), robuste à la longueur.",
    "hapax_ratio": "Proportion de mots n'apparaissant qu'une fois.",
    "yule_k": "Yule's K : richesse lexicale (haut = répétitif).",
    "mean_word_len": "Longueur moyenne des mots (caractères).",
    "mean_sent_len": "Longueur moyenne de phrase (mots).",
    "sd_sent_len": "Écart-type de la longueur de phrase.",
    "cv_sent_len": "Coefficient de variation des longueurs de phrase.",
    "burstiness": "(σ−μ)/(σ+μ) des longueurs de phrase ; bas = uniforme = pro-IA.",
    "commas_per_sent": "Virgules par phrase (densité de propositions).",
    "subordination_ratio": "Phrases contenant ≥1 subordonnant.",
    "interrogative_ratio": "Proportion de phrases interrogatives.",
    "syllables_per_word": "Syllabes (approx. voyelles) par mot.",
    "long_word_ratio": "Proportion de mots ≥ 7 lettres.",
    "readability_proxy": "Indice de lisibilité (style Flesch, ajusté langue).",
    "function_word_ratio": "Part des mots-outils dans le texte.",
    "transition_density": "Connecteurs de transition « formels » / 1000 mots.",
    "ai_marker_density": "Tics lexicaux LLM / 1000 mots (delve, paysage…).",
    "hedge_density": "Atténuateurs épistémiques / 1000 mots.",
    "emdash_per_1k": "Tirets cadratins (—) / 1000 mots.",
    "curly_quote_ratio": "Part de guillemets typographiques (« ' ' » vs droits).",
    "contraction_ratio": "Contractions / 1000 mots (EN : don't, it's…).",
    "list_marker_ratio": "Densité de puces / listes numérotées.",
    "distinct_bigram_ratio": "Bigrammes distincts / total (distinct-2).",
    "distinct_trigram_ratio": "Trigrammes distincts / total (distinct-3).",
    "bigram_repetition": "Taux de bigrammes répétés (1 − distinct-2).",
    "compression_ratio": "Ratio de compression zlib (haut = redondant).",
    "sent_initial_repetition": "Répétition du 1er mot entre phrases (anaphore).",
    "paragraph_len_cv": "Coefficient de variation des longueurs de paragraphe.",
}


def _syllables(word: str, vowels: str) -> int:
    w = word.lower()
    groups = re.findall("[" + re.escape(vowels) + "]+", w)
    return max(1, len(groups))


def extract_features(text: str, language: str | None = None) -> FeatureResult:
    lang = language or L.detect_language(text)
    if lang not in L.SUPPORTED:
        lang = "en"
    low = text.lower()

    sents = split_sentences(text)
    words = tokenize(text)
    words_low = [w.lower() for w in words]
    n_words = len(words)
    n_sents = len(sents)

    f: dict[str, float] = {}

    # ---- Diversité lexicale ----
    counts = Counter(words_low)
    n_types = len(counts)
    f["ttr"] = _safe_div(n_types, n_words)
    # MATTR : moyenne des TTR sur fenêtres glissantes de 50.
    win = 50
    if n_words >= win:
        ttrs = []
        for i in range(n_words - win + 1):
            window = words_low[i:i + win]
            ttrs.append(len(set(window)) / win)
        f["mattr_50"] = sum(ttrs) / len(ttrs)
    else:
        f["mattr_50"] = f["ttr"]
    f["hapax_ratio"] = _safe_div(sum(1 for c in counts.values() if c == 1), n_words)
    # Yule's K
    if n_words:
        m1 = n_words
        m2 = sum(c * c for c in counts.values())
        f["yule_k"] = 1e4 * (m2 - m1) / (m1 * m1) if m1 else 0.0
    else:
        f["yule_k"] = 0.0
    f["mean_word_len"] = _safe_div(sum(len(w) for w in words), n_words)

    # ---- Complexité syntaxique ----
    sent_lens = [len(tokenize(s)) for s in sents] or [0]
    mu = _safe_div(sum(sent_lens), len(sent_lens))
    var = _safe_div(sum((x - mu) ** 2 for x in sent_lens), len(sent_lens))
    sd = math.sqrt(var)
    f["mean_sent_len"] = mu
    f["sd_sent_len"] = sd
    f["cv_sent_len"] = _safe_div(sd, mu)
    # Burstiness normalisée (Goh & Barabási) : (σ−μ)/(σ+μ) ∈ [-1, 1].
    f["burstiness"] = _safe_div(sd - mu, sd + mu)
    f["commas_per_sent"] = _safe_div(text.count(","), n_sents or 1)
    subs = set(L.SUBORDINATORS[lang])
    sent_with_sub = sum(1 for s in sents if subs & set(tokenize(s.lower())))
    f["subordination_ratio"] = _safe_div(sent_with_sub, n_sents or 1)
    f["interrogative_ratio"] = _safe_div(sum(1 for s in sents if s.rstrip().endswith("?")), n_sents or 1)

    # ---- Lisibilité ----
    vowels = L.VOWELS[lang]
    syl = sum(_syllables(w, vowels) for w in words)
    spw = _safe_div(syl, n_words)
    f["syllables_per_word"] = spw
    f["long_word_ratio"] = _safe_div(sum(1 for w in words if len(w) >= 7), n_words)
    # Flesch Reading Ease générique (paramètres EN ; proxy pour FR/NL).
    f["readability_proxy"] = 206.835 - 1.015 * mu - 84.6 * spw

    # ---- Mots-outils & connecteurs ----
    fw = set(L.FUNCTION_WORDS[lang])
    f["function_word_ratio"] = _safe_div(sum(1 for w in words_low if w in fw), n_words)
    f["transition_density"] = 1000.0 * _safe_div(
        _count_phrases(low, L.AI_TRANSITION_WORDS[lang]), n_words)

    # ---- Marqueurs d'IA ----
    f["ai_marker_density"] = 1000.0 * _safe_div(
        _count_phrases(low, L.AI_MARKER_WORDS[lang]), n_words)
    f["hedge_density"] = 1000.0 * _safe_div(
        _count_phrases(low, L.HEDGES[lang]), n_words)
    f["emdash_per_1k"] = 1000.0 * _safe_div(text.count("—") + text.count(" – "), n_words)
    straight_q = text.count('"') + text.count("'")
    curly_q = sum(text.count(c) for c in "“”‘’«»")
    f["curly_quote_ratio"] = _safe_div(curly_q, straight_q + curly_q)
    contractions = len(re.findall(r"\b\w+['’](?:s|t|re|ve|ll|d|m)\b", low)) if lang == "en" else \
        len(re.findall(r"\b[cdjlmnst]['’]\w+", low))  # FR élisions: c'est, l'on…
    f["contraction_ratio"] = 1000.0 * _safe_div(contractions, n_words)
    list_markers = len(re.findall(r"(?m)^\s*(?:[-*•·]|\d+[.\)])\s+", text))
    f["list_marker_ratio"] = _safe_div(list_markers, n_sents or 1)

    # ---- Unicité & variété ----
    bigrams = list(zip(words_low, words_low[1:]))
    trigrams = list(zip(words_low, words_low[1:], words_low[2:]))
    f["distinct_bigram_ratio"] = _safe_div(len(set(bigrams)), len(bigrams))
    f["distinct_trigram_ratio"] = _safe_div(len(set(trigrams)), len(trigrams))
    f["bigram_repetition"] = 1.0 - f["distinct_bigram_ratio"] if bigrams else 0.0
    raw = text.encode("utf-8")
    f["compression_ratio"] = _safe_div(len(raw), len(zlib.compress(raw, 9))) if raw else 0.0
    if n_sents > 1:
        firsts = [tokenize(s.lower())[0] for s in sents if tokenize(s)]
        fc = Counter(firsts)
        f["sent_initial_repetition"] = _safe_div(sum(c - 1 for c in fc.values() if c > 1), len(firsts) or 1)
    else:
        f["sent_initial_repetition"] = 0.0
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    plens = [len(tokenize(p)) for p in paras] or [0]
    pmu = _safe_div(sum(plens), len(plens))
    psd = math.sqrt(_safe_div(sum((x - pmu) ** 2 for x in plens), len(plens)))
    f["paragraph_len_cv"] = _safe_div(psd, pmu)

    return FeatureResult(language=lang, n_words=n_words, n_sentences=n_sents,
                         n_paragraphs=len(paras), features=f)
