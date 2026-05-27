"""Scoring heuristique « zéro-entraînement » de l'indice d'usage d'IA.

Faute de corpus étiqueté, on ne peut pas (encore) entraîner le Random
Forest du chapitre. On fournit donc un score interprétable fondé sur des
règles documentées, tirées de la littérature 2023-2025 sur la détection
de texte généré (burstiness/perplexité, sur-emploi de connecteurs,
« tics » lexicaux, faible variété n-gramme, redondance).

Chaque règle transforme une feature en une contribution ∈ [0, 1]
(1 = très « IA »), via une rampe linéaire entre deux seuils explicites.
Les contributions sont pondérées et agrégées par catégorie, puis en un
score global 0-100. RIEN ICI N'EST UNE PREUVE : voir les avertissements
du rapport. Les seuils sont des points de départ, à recalibrer dès qu'un
corpus est disponible (cf. model.py pour la voie supervisée).
"""

from __future__ import annotations

from dataclasses import dataclass

from .features import FeatureResult


def _ramp(x: float, lo: float, hi: float) -> float:
    """Rampe linéaire. Si lo<hi : x<=lo→0, x>=hi→1. Si lo>hi : inversée."""
    if lo == hi:
        return 0.0
    if lo < hi:
        return max(0.0, min(1.0, (x - lo) / (hi - lo)))
    return max(0.0, min(1.0, (lo - x) / (lo - hi)))


# (feature, fonction->[0,1] où 1=IA, poids, libellé indice, sens)
# `direction` documente ce qui pousse vers "IA".
_RULES = [
    # Complexité syntaxique / rythme
    ("burstiness", lambda v: _ramp(v, 0.30, -0.10), 2.0,
     "Rythme de phrase très uniforme (burstiness basse)"),
    ("cv_sent_len", lambda v: _ramp(v, 0.70, 0.30), 1.5,
     "Faible variation des longueurs de phrase"),
    ("paragraph_len_cv", lambda v: _ramp(v, 0.60, 0.15), 1.0,
     "Paragraphes de longueur très régulière"),
    # Connecteurs & marqueurs
    ("transition_density", lambda v: _ramp(v, 3.0, 13.0), 2.0,
     "Sur-emploi de connecteurs formels (de plus, moreover…)"),
    ("ai_marker_density", lambda v: _ramp(v, 1.0, 8.0), 2.0,
     "Tics lexicaux typiques de LLM (delve, paysage, souligner…)"),
    ("emdash_per_1k", lambda v: _ramp(v, 1.0, 6.0), 1.5,
     "Densité élevée de tirets cadratins (—)"),
    ("hedge_density", lambda v: _ramp(v, 3.0, 16.0), 0.8,
     "Atténuateurs épistémiques lisses et nombreux"),
    ("list_marker_ratio", lambda v: _ramp(v, 0.03, 0.25), 0.8,
     "Recours fréquent aux listes à puces / numérotées"),
    # Unicité & variété
    ("distinct_trigram_ratio", lambda v: _ramp(v, 0.97, 0.85), 1.2,
     "Faible variété des trigrammes (formulations répétées)"),
    ("compression_ratio", lambda v: _ramp(v, 2.0, 2.8), 1.0,
     "Texte très compressible (redondant)"),
    ("sent_initial_repetition", lambda v: _ramp(v, 0.05, 0.35), 0.8,
     "Répétition des débuts de phrase (parallélisme)"),
    # Diversité lexicale
    ("mattr_50", lambda v: _ramp(v, 0.78, 0.62), 1.0,
     "Diversité lexicale locale plus faible que la normale"),
]

# Indices qui poussent vers "HUMAIN" quand ils sont forts (pour l'affichage).
_HUMAN_HINTS = [
    ("burstiness", lambda v: v > 0.30, "Rythme de phrase irrégulier (humain typique)"),
    ("transition_density", lambda v: v < 3.0, "Peu de connecteurs formels"),
    ("ai_marker_density", lambda v: v < 1.0, "Absence de tics lexicaux LLM"),
    ("distinct_trigram_ratio", lambda v: v > 0.97, "Forte variété des formulations"),
]

BANDS = [
    (0, 25, "faible", "Signaux d'IA peu présents — vraisemblablement humain ou très retravaillé."),
    (25, 50, "modéré", "Quelques signaux d'IA — possible assistance ponctuelle (relecture, reformulation)."),
    (50, 75, "élevé", "Signaux d'IA marqués — rédaction probablement assistée par IA pour une partie substantielle."),
    (75, 101, "très élevé", "Signaux d'IA convergents — rédaction très probablement générée par IA."),
]


@dataclass
class AIScore:
    score: float                 # 0-100
    band: str
    band_label: str
    category_scores: dict        # catégorie -> 0-100
    pro_ai_evidence: list        # [(libellé, valeur, contribution)]
    pro_human_evidence: list
    tool_guess: str
    tool_confidence: str
    reliability: str             # fiabilité de la mesure selon la longueur


def _category_of(feature: str) -> str:
    from .features import FEATURE_CATEGORIES
    for cat, names in FEATURE_CATEGORIES.items():
        if feature in names:
            return cat
    return "Autre"


def score_text(fr: FeatureResult, lang: str | None = None) -> AIScore:
    lang = lang or fr.language
    f = fr.features

    # Contraction (EN seulement) : registre formel sans contraction → +IA.
    rules = list(_RULES)
    # Le signal « régularité des paragraphes » n'a de sens qu'avec ≥2 paragraphes.
    if fr.n_paragraphs < 2:
        rules = [r for r in rules if r[0] != "paragraph_len_cv"]
    if lang == "en":
        rules.append(("contraction_ratio", lambda v: _ramp(v, 5.0, 0.5), 1.0,
                       "Registre formel sans contractions (don't, it's…)"))

    total_w = sum(w for _, _, w, _ in rules)
    weighted = 0.0
    pro_ai = []
    cat_num: dict[str, float] = {}
    cat_den: dict[str, float] = {}
    for feat, fn, w, label in rules:
        val = f.get(feat, 0.0)
        c = fn(val)
        weighted += w * c
        cat = _category_of(feat)
        cat_num[cat] = cat_num.get(cat, 0.0) + w * c
        cat_den[cat] = cat_den.get(cat, 0.0) + w
        if c >= 0.5:
            pro_ai.append((label, round(val, 3), round(c, 2)))

    score = 100.0 * weighted / total_w if total_w else 0.0
    pro_ai.sort(key=lambda x: -x[2])

    pro_human = []
    for feat, cond, label in _HUMAN_HINTS:
        v = f.get(feat, 0.0)
        if cond(v):
            pro_human.append((label, round(v, 3)))

    band, band_label = "faible", BANDS[0][3]
    for lo, hi, name, desc in BANDS:
        if lo <= score < hi:
            band, band_label = name, desc
            break

    cat_scores = {c: round(100.0 * cat_num[c] / cat_den[c], 1) for c in cat_num}

    tool, conf = _guess_tool(f, score)

    # Fiabilité selon la longueur (les stats sont instables en deçà de ~300 mots).
    if fr.n_words < 150:
        reliability = "faible (texte court : < 150 mots — résultat indicatif seulement)"
    elif fr.n_words < 400:
        reliability = "moyenne (150-400 mots)"
    else:
        reliability = "bonne (≥ 400 mots)"

    return AIScore(
        score=round(score, 1), band=band, band_label=band_label,
        category_scores=cat_scores, pro_ai_evidence=pro_ai,
        pro_human_evidence=pro_human, tool_guess=tool,
        tool_confidence=conf, reliability=reliability,
    )


def _guess_tool(f: dict, score: float) -> tuple[str, str]:
    """Estimation TRÈS prudente de la famille d'outil. Faible fiabilité.

    Repose sur des tendances rapportées (non garanties) : la famille GPT
    tend à un fort sur-emploi de tirets cadratins + connecteurs + tics
    lexicaux ; les sorties type Claude sont souvent plus « naturelles »
    (variété lexicale plus haute, moins de connecteurs mécaniques).
    """
    if score < 35:
        return "indéterminé (signaux d'IA trop faibles)", "n/a"
    emdash = f.get("emdash_per_1k", 0)
    trans = f.get("transition_density", 0)
    markers = f.get("ai_marker_density", 0)
    diversity = f.get("distinct_trigram_ratio", 1)
    gpt_like = (emdash >= 4) + (trans >= 9) + (markers >= 5)
    if gpt_like >= 2:
        return "famille GPT (OpenAI) — profil « connecteurs + tirets + tics »", "faible"
    if diversity >= 0.95 and trans < 6 and markers < 3:
        return "famille type Claude / sortie peu mécanique", "très faible"
    return "LLM générique (famille indéterminée)", "très faible"
