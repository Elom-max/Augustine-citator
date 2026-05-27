"""Tests de fumée : extraction de features, scoring, détection de langue, rapports."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from styloscan import analyze, extract_features, FEATURE_NAMES
from styloscan.languages import detect_language
from styloscan import report as rpt

AI_EN = ("In today's evolving landscape, it is important to delve into the "
         "intricate realm of writing. Moreover, researchers must navigate a "
         "complex tapestry. Furthermore, robust methods underscore credibility. "
         "Additionally, scholars leverage holistic frameworks. In conclusion, "
         "the seamless integration remains pivotal and crucial.")

HUMAN_FR = ("Je ne m'attendais pas à ça. On a refait la manip trois fois. La "
            "première a raté — contamination, sans doute. Mais les deux autres ? "
            "Nickel. Bizarrement stable, ce qui m'a intrigué. Pourquoi personne "
            "n'avait creusé avant ? Mystère.")

NL = ("Het is belangrijk om dieper in te gaan op de complexe dynamiek. "
      "Bovendien moeten onderzoekers een ingewikkeld landschap navigeren. "
      "Daarnaast onderstrepen robuuste methoden de geloofwaardigheid.")

LA = ("Deus creator omnium est, et per ipsum facta sunt omnia quae in caelo "
      "et in terra sunt. Ratio igitur ordinem rerum quaerit, cum anima ad "
      "veritatem contendit atque per gradus disciplinarum ascendit. Nam quod "
      "verum est non potest non esse verum, sicut quod bonum est bonum manet.")


def test_feature_vector_complete():
    fr = extract_features(AI_EN, language="en")
    assert fr.n_words > 0 and fr.n_sentences > 0
    for n in FEATURE_NAMES:
        assert n in fr.features, f"feature manquante: {n}"
        assert isinstance(fr.features[n], float)


def test_language_detection():
    assert detect_language(AI_EN) == "en"
    assert detect_language(HUMAN_FR) == "fr"
    assert detect_language(NL) == "nl"
    assert detect_language(LA) == "la"


def test_latin_feature_vector_complete():
    fr = extract_features(LA, language="la")
    assert fr.language == "la" and fr.n_words > 0
    for n in FEATURE_NAMES:
        assert n in fr.features and isinstance(fr.features[n], float)


def test_ai_scores_higher_than_human():
    _, ai = analyze(AI_EN)
    _, hu = analyze(HUMAN_FR)
    assert 0 <= ai.score <= 100 and 0 <= hu.score <= 100
    assert ai.score > hu.score, (ai.score, hu.score)


def test_reports_render():
    fr, sc = analyze(AI_EN)
    j = rpt.to_json(fr, sc)
    h = rpt.to_html(fr, sc)
    assert '"ai_index"' in j
    assert "<html" in h and "Indice d'usage d'IA" in h


if __name__ == "__main__":
    test_feature_vector_complete()
    test_language_detection()
    test_ai_scores_higher_than_human()
    test_reports_render()
    print("OK — tous les tests de fumée passent.")
