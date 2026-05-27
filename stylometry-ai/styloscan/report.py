"""Génération de rapports (JSON + HTML autonome, sans dépendance front)."""

from __future__ import annotations

import html
import json

from .features import FEATURE_CATEGORIES, FEATURE_GLOSSARY, FeatureResult
from .scoring import AIScore

DISCLAIMER = (
    "Cet indice est une aide à l'analyse, PAS une preuve. Les détecteurs "
    "stylométriques produisent des faux positifs, notamment sur la prose "
    "académique très formelle, les textes de locuteurs non natifs et les "
    "textes courts. Un score élevé doit être recoupé (historique de "
    "versions, entretien, métadonnées) et ne saurait fonder à lui seul une "
    "accusation. Calibrez les seuils sur votre propre corpus (voir model.py)."
)


def to_dict(fr: FeatureResult, sc: AIScore) -> dict:
    return {
        "language": fr.language,
        "n_words": fr.n_words,
        "n_sentences": fr.n_sentences,
        "ai_index": sc.score,
        "band": sc.band,
        "band_label": sc.band_label,
        "reliability": sc.reliability,
        "category_scores": sc.category_scores,
        "tool_guess": sc.tool_guess,
        "tool_confidence": sc.tool_confidence,
        "evidence_pro_ai": [
            {"signal": s, "value": v, "contribution": c} for s, v, c in sc.pro_ai_evidence],
        "evidence_pro_human": [
            {"signal": s, "value": v} for s, v in sc.pro_human_evidence],
        "features": {k: round(v, 4) for k, v in fr.features.items()},
        "disclaimer": DISCLAIMER,
    }


def to_json(fr: FeatureResult, sc: AIScore, indent: int = 2) -> str:
    return json.dumps(to_dict(fr, sc), ensure_ascii=False, indent=indent)


def _bar(pct: float, color: str) -> str:
    pct = max(0.0, min(100.0, pct))
    return (f'<div class="bar"><div class="fill" style="width:{pct:.0f}%;'
            f'background:{color}">{pct:.0f}</div></div>')


def _color(score: float) -> str:
    if score < 25:
        return "#2e7d32"
    if score < 50:
        return "#f9a825"
    if score < 75:
        return "#ef6c00"
    return "#c62828"


def to_html(fr: FeatureResult, sc: AIScore, title: str = "Rapport StyloScan") -> str:
    d = to_dict(fr, sc)
    esc = html.escape
    col = _color(sc.score)

    cat_rows = "".join(
        f"<tr><td>{esc(c)}</td><td>{_bar(v, _color(v))}</td></tr>"
        for c, v in sc.category_scores.items())

    ai_rows = "".join(
        f"<li><b>{esc(s)}</b> — valeur {v} (contribution {c})</li>"
        for s, v, c in sc.pro_ai_evidence) or "<li>Aucun signal d'IA marqué.</li>"
    hum_rows = "".join(
        f"<li>{esc(s)} — valeur {v}</li>"
        for s, v in sc.pro_human_evidence) or "<li>—</li>"

    feat_rows = ""
    for cat, names in FEATURE_CATEGORIES.items():
        feat_rows += f'<tr class="cat"><td colspan="3">{esc(cat)}</td></tr>'
        for n in names:
            feat_rows += (f"<tr><td>{esc(n)}</td><td>{fr.features.get(n, 0):.4f}</td>"
                          f"<td class='gl'>{esc(FEATURE_GLOSSARY.get(n, ''))}</td></tr>")

    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><style>
body{{font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif;max-width:820px;margin:24px auto;padding:0 16px;color:#1a1a1a}}
h1{{font-size:22px;margin:0 0 4px}} h2{{font-size:17px;margin:24px 0 8px;border-bottom:1px solid #eee;padding-bottom:4px}}
.gauge{{font-size:46px;font-weight:700;color:{col}}} .band{{font-size:15px;color:#555}}
.bar{{background:#eee;border-radius:5px;overflow:hidden;height:20px;min-width:120px}}
.fill{{color:#fff;font-size:12px;text-align:right;padding-right:6px;line-height:20px;border-radius:5px}}
table{{border-collapse:collapse;width:100%}} td{{padding:5px 8px;border-bottom:1px solid #f0f0f0;vertical-align:middle}}
tr.cat td{{background:#fafafa;font-weight:600}} .gl{{color:#777;font-size:12px}}
.meta{{color:#555;font-size:13px}} .warn{{background:#fff8e1;border:1px solid #ffe082;padding:10px 12px;border-radius:8px;font-size:13px;margin-top:16px}}
.tool{{background:#f5f5f5;padding:8px 12px;border-radius:8px;display:inline-block}}
</style></head><body>
<h1>{esc(title)}</h1>
<p class="meta">Langue détectée : <b>{esc(fr.language)}</b> · {fr.n_words} mots · {fr.n_sentences} phrases · fiabilité : {esc(sc.reliability)}</p>
<h2>Indice d'usage d'IA</h2>
<div class="gauge">{sc.score:.0f}/100</div>
<div class="band">Niveau <b>{esc(sc.band)}</b> — {esc(sc.band_label)}</div>
<p class="tool">Type d'outil estimé : <b>{esc(sc.tool_guess)}</b> (confiance : {esc(sc.tool_confidence)})</p>
<h2>Score par catégorie</h2>
<table>{cat_rows}</table>
<h2>Indices en faveur d'une rédaction par IA</h2><ul>{ai_rows}</ul>
<h2>Indices en faveur d'une rédaction humaine</h2><ul>{hum_rows}</ul>
<h2>Toutes les features</h2>
<table><tr><th>Feature</th><th>Valeur</th><th>Définition</th></tr>{feat_rows}</table>
<div class="warn"><b>Avertissement.</b> {esc(d['disclaimer'])}</div>
</body></html>"""
