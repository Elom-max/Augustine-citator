"""Ressources linguistiques pour FR / EN / NL.

Listes de mots-outils, connecteurs, subordonnants et marqueurs lexicaux
fréquemment sur-représentés dans le texte généré par LLM. Tout est en
clair (curable à la main), dans l'esprit du chapitre de référence
(Bolt et al., « Stylometry for Latin Literary Criticism », 2026) : des
features interprétables, pas de boîte noire.

Les listes ne prétendent pas être exhaustives : ce sont des points de
départ, à enrichir. Aucune dépendance réseau / aucun modèle à télécharger.
"""

from __future__ import annotations

SUPPORTED = ("fr", "en", "nl")

# --- Mots-outils (function words) : noyau servant d'empreinte stylistique.
# Volontairement courts mais discriminants ; ils dominent les analyses
# d'attribution (cf. chapitre §"Background: Features").
FUNCTION_WORDS = {
    "fr": [
        "le", "la", "les", "un", "une", "des", "de", "du", "au", "aux", "à",
        "et", "ou", "mais", "donc", "or", "ni", "car", "que", "qui", "quoi",
        "dont", "où", "ce", "cet", "cette", "ces", "il", "elle", "ils",
        "elles", "je", "tu", "nous", "vous", "on", "se", "son", "sa", "ses",
        "leur", "leurs", "dans", "sur", "sous", "pour", "par", "avec", "sans",
        "entre", "vers", "chez", "ne", "pas", "plus", "très", "comme", "si",
        "lorsque", "puisque", "afin", "ainsi", "alors", "cependant", "néanmoins",
    ],
    "en": [
        "the", "a", "an", "of", "to", "in", "on", "at", "by", "for", "with",
        "from", "into", "about", "and", "or", "but", "so", "yet", "nor",
        "because", "although", "though", "while", "whereas", "that", "which",
        "who", "whom", "whose", "this", "these", "those", "it", "its", "he",
        "she", "they", "we", "you", "i", "his", "her", "their", "our", "your",
        "not", "no", "very", "as", "if", "then", "thus", "however", "moreover",
        "furthermore", "therefore", "hence",
    ],
    "nl": [
        "de", "het", "een", "van", "te", "in", "op", "aan", "bij", "voor",
        "met", "uit", "over", "en", "of", "maar", "dus", "want", "noch",
        "omdat", "hoewel", "terwijl", "dat", "die", "welke", "wie", "wiens",
        "dit", "deze", "het", "hij", "zij", "ze", "wij", "we", "jij", "je",
        "ik", "zijn", "haar", "hun", "ons", "jouw", "niet", "geen", "zeer",
        "als", "dan", "dus", "echter", "bovendien", "daarnaast", "derhalve",
    ],
}

# --- Connecteurs de transition « formels » sur-employés par les LLM.
# Densité élevée = signal pro-IA (registre uniformément soutenu).
AI_TRANSITION_WORDS = {
    "fr": [
        "de plus", "par ailleurs", "en outre", "en effet", "ainsi", "de surcroît",
        "néanmoins", "cependant", "toutefois", "notamment", "globalement",
        "en conclusion", "en somme", "il convient de", "il est important de",
        "il est essentiel de", "force est de constater", "dans ce contexte",
        "à cet égard", "en définitive", "par conséquent",
    ],
    "en": [
        "moreover", "furthermore", "additionally", "in addition", "however",
        "nevertheless", "nonetheless", "consequently", "therefore", "thus",
        "notably", "importantly", "overall", "in conclusion", "to summarize",
        "it is important to", "it is worth noting", "in today's world",
        "in the realm of", "when it comes to", "first and foremost",
    ],
    "nl": [
        "bovendien", "daarnaast", "voorts", "echter", "niettemin",
        "desalniettemin", "bijgevolg", "derhalve", "aldus", "met name",
        "het is belangrijk om", "het is vermeldenswaard", "in conclusie",
        "samenvattend", "over het algemeen", "in dit verband", "kortom",
    ],
}

# --- « Tics » lexicaux caractéristiques de l'écriture LLM (surtout GPT).
AI_MARKER_WORDS = {
    "fr": [
        "plonger", "approfondir", "incontournable", "riche", "paysage",
        "tapisserie", "souligner", "exploiter", "robuste", "holistique",
        "synergie", "fluide", "transformateur", "primordial", "crucial",
        "pivot", "naviguer", "domaine", "à l'ère", "véritable mine",
    ],
    "en": [
        "delve", "delving", "intricate", "intricacies", "realm", "tapestry",
        "underscore", "underscores", "leverage", "robust", "holistic",
        "synergy", "seamless", "seamlessly", "transformative", "pivotal",
        "navigate", "navigating", "landscape", "testament", "showcase",
        "foster", "fostering", "harness", "vibrant", "myriad", "crucial",
    ],
    "nl": [
        "duiken", "verdiepen", "complexe", "complexiteit", "landschap",
        "onderstrepen", "benutten", "robuust", "holistisch", "synergie",
        "naadloos", "transformatief", "cruciaal", "navigeren", "domein",
        "schatkamer", "veelzijdig", "talloze",
    ],
}

# --- Subordonnants (proxy de complexité syntaxique : densité de subordination).
SUBORDINATORS = {
    "fr": ["que", "qui", "dont", "où", "lorsque", "puisque", "quoique",
           "bien que", "afin que", "parce que", "tandis que", "alors que",
           "si", "comme", "quand"],
    "en": ["that", "which", "who", "whom", "whose", "because", "although",
           "though", "while", "whereas", "since", "unless", "if", "when",
           "before", "after", "until", "as"],
    "nl": ["dat", "die", "welke", "wie", "omdat", "hoewel", "terwijl",
           "zodat", "indien", "als", "wanneer", "voordat", "nadat", "totdat",
           "aangezien"],
}

# --- Booster/hedge (registre épistémique). Forte présence de hedges
# atténués + boosters lisses est typique du texte poli par LLM.
HEDGES = {
    "fr": ["peut-être", "probablement", "semble", "pourrait", "en quelque sorte",
           "relativement", "dans une certaine mesure", "généralement", "souvent"],
    "en": ["perhaps", "probably", "seems", "might", "could", "somewhat",
           "relatively", "to some extent", "generally", "often", "arguably"],
    "nl": ["misschien", "waarschijnlijk", "lijkt", "zou kunnen", "enigszins",
           "relatief", "in zekere mate", "doorgaans", "vaak"],
}

# Approximations de comptage de syllabes (voyelles) par langue, pour la
# lisibilité. Simplifié et documenté comme proxy.
VOWELS = {
    "fr": "aàâeéèêëiîïoôuùûüy",
    "en": "aeiouy",
    "nl": "aeiouyé",
}


def _tokens_lower(text: str):
    import re
    return re.findall(r"[^\W\d_]+", text.lower(), flags=re.UNICODE)


def detect_language(text: str) -> str:
    """Détection de langue par recouvrement de mots-outils (sans réseau).

    Renvoie 'fr', 'en' ou 'nl'. Robuste pour des textes de quelques phrases.
    Départage par fréquence relative des mots-outils de chaque langue.
    """
    toks = _tokens_lower(text)
    if not toks:
        return "en"
    counts = {}
    for lang in SUPPORTED:
        fw = set(FUNCTION_WORDS[lang])
        counts[lang] = sum(1 for t in toks if t in fw)
    # Quelques marqueurs très discriminants pour départager fr/nl/en.
    disc = {
        "fr": {"le", "la", "les", "des", "une", "est", "dans", "pour", "que"},
        "nl": {"het", "een", "van", "en", "de", "dat", "niet", "zijn", "voor"},
        "en": {"the", "of", "and", "to", "is", "in", "that", "for", "with"},
    }
    for lang in SUPPORTED:
        counts[lang] += 1.5 * sum(1 for t in toks if t in disc[lang])
    best = max(counts, key=counts.get)
    return best
