"""StyloScan — stylométrie pour la détection d'usage d'IA dans l'écrit scientifique.

Transposition de la méthodologie de Bolt, Bui, Chaudhuri & Dexter,
« Stylometry for Latin Literary Criticism » (Routledge, 2026) : un jeu de
features linguistiques *interprétables* → vecteurs → Random Forest +
validation croisée + importance de Gini, complété par une PCA pour la
visualisation. Adapté ici aux articles, thèses et rapports scientifiques
(FR / EN / NL) pour détecter, quantifier et caractériser l'usage des
outils d'IA générative.
"""

from .features import (FEATURE_CATEGORIES, FEATURE_NAMES, extract_features,
                       FeatureResult)
from .scoring import AIScore, score_text
from . import report

__all__ = [
    "extract_features", "FeatureResult", "FEATURE_NAMES", "FEATURE_CATEGORIES",
    "score_text", "AIScore", "report", "analyze",
]

__version__ = "0.1.0"


def analyze(text: str, language: str | None = None):
    """Raccourci : (FeatureResult, AIScore) pour un texte."""
    fr = extract_features(text, language=language)
    return fr, score_text(fr, lang=fr.language)
