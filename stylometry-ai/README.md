# StyloScan — stylométrie pour la détection d'usage d'IA dans l'écrit scientifique

Outil de **stylométrie** conçu pour les **productions scientifiques** (articles
de revues, thèses, mémoires, rapports) afin de **détecter, quantifier et
caractériser** l'usage des outils d'IA générative : *degré* d'assistance,
*patterns* mobilisés, et estimation prudente du *type* d'outil. Trois langues :
**français, anglais, néerlandais**.

> ⚠️ **Un indice d'aide à l'analyse, pas une preuve.** Les détecteurs
> stylométriques produisent des faux positifs — surtout sur la prose académique
> très formelle, les textes courts et les locuteurs non natifs. Un score élevé
> doit toujours être recoupé (historique de versions, entretien, métadonnées) et
> ne saurait, à lui seul, fonder une accusation.

## Filiation méthodologique

Transposition directe de la méthode de **Bolt, Bui, Chaudhuri & Dexter,
*« Stylometry for Latin Literary Criticism »*** (in *Evolving Perspectives on
Digital Classics*, Routledge, 2026) — le texte de référence fourni. On reprend
sa chaîne, en remplaçant l'attribution de *genre latin* par la tâche *humain vs
IA* :

| Chapitre (latin) | StyloScan (IA) |
|---|---|
| 26 features interprétables (mots-outils, syntaxe, longueurs de phrase…) | features interprétables FR/EN/NL (burstiness, connecteurs, tics LLM, variété n-gramme, redondance…) |
| chaque texte → vecteur n-dimensionnel | idem |
| classifieur **Random Forest** | idem |
| **validation croisée** 5 plis | idem |
| métriques **accuracy + F1** | idem |
| **importance de Gini** (interprétabilité > performance brute) | idem |
| **PCA** + violin plots (case studies 3-4) | idem |

Le principe directeur du chapitre est respecté : **des features simples,
comptables à la main, et interprétables**, plutôt qu'une boîte noire.

## Le paramétrage (recherche en ligne)

Le jeu de features et les seuils heuristiques s'appuient sur la littérature
2023-2025 de détection de texte généré, notamment :

- **StyloAI** (Opara, 2024, arXiv:2405.10129) — 31 features stylométriques +
  Random Forest, organisées en catégories (diversité lexicale, complexité
  syntaxique, lisibilité, marqueurs, unicité/variété), qui structurent ici
  `FEATURE_CATEGORIES`.
- **Perplexité & burstiness** (GPTZero, DetectGPT) — les sorties LLM ont une
  *burstiness* basse (phrases régulières) et une perplexité basse. On en mesure
  des *proxys* sans réseau (variance des longueurs, variété n-gramme,
  compression).
- **Tics lexicaux LLM** — sur-emploi de connecteurs formels (*moreover, de plus,
  bovendien*), de mots-signatures (*delve, intricate, paysage, souligner*), de
  tirets cadratins, de listes ; faible variété de formulations.

Voir `styloscan/languages.py` (listes par langue) et `styloscan/scoring.py`
(règles + seuils, tous documentés et recalibrables).

## Installation

```bash
cd stylometry-ai
pip install -r requirements.txt        # numpy, scikit-learn, matplotlib, flask, joblib
# ou : pip install -e .                 # installe la commande `styloscan`
```

## Utilisation

### 1) Ligne de commande / bibliothèque (score heuristique, sans entraînement)

```bash
PYTHONPATH=. python3 -m styloscan.cli analyze mon_article.txt --html rapport.html
PYTHONPATH=. python3 -m styloscan.cli features mon_article.txt        # vecteur brut
```

```python
from styloscan import analyze
fr, sc = analyze(open("these_chap3.txt").read())
print(sc.score, sc.band, sc.tool_guess)      # ex. 62.0 'élevé' 'famille GPT…'
print(sc.category_scores, sc.pro_ai_evidence)
```

### 2) Voie supervisée (dès que vous avez un corpus étiqueté)

Organisez le corpus en sous-dossiers de classes, puis :

```
corpus/
  human/  *.txt
  ai/     *.txt          # ou gpt/, claude/, gemini/… pour du multi-classe (type d'outil)
```

```bash
PYTHONPATH=. python3 -m styloscan.cli train corpus --lang fr \
    --out modele.joblib --gini-plot gini.png
PYTHONPATH=. python3 -m styloscan.cli predict nouveau.txt --model modele.joblib
```

La sortie donne **accuracy** et **F1** en validation croisée 5 plis, le **F1 par
classe**, et le classement des features par **importance de Gini**.

### 3) Interface web

```bash
PYTHONPATH=. python3 web/app.py     # http://127.0.0.1:5000
```

Collez un texte, choisissez la langue (ou *auto*), obtenez le rapport. Une API
JSON est aussi exposée : `POST /api/analyze` `{"text": "...", "lang": "fr"}`.

### 4) Notebook reproductible

`notebooks/stylometry_ai_tutorial.ipynb` : walk-through complet façon chapitre
(features → RF + CV + F1 + Gini → PCA → violin plots), auto-exécutable sur un
mini-corpus jouet.

## Ce que produit l'analyse

- **Indice d'usage d'IA** 0-100 + bande qualitative (faible / modéré / élevé /
  très élevé) — le *degré*.
- **Score par catégorie** (diversité lexicale, complexité syntaxique, lisibilité,
  connecteurs, marqueurs d'IA, unicité) — les *patterns*.
- **Faisceau d'indices** explicite (quels signaux ont pesé, et combien).
- **Estimation du type d'outil** (famille GPT vs sortie « naturelle » type
  Claude vs générique) — *confiance volontairement basse*.
- **Indicateur de fiabilité** selon la longueur du texte.

## Features (résumé)

| Catégorie | Exemples |
|---|---|
| Diversité lexicale | TTR, MATTR-50, hapax, Yule's K, longueur de mot |
| Complexité syntaxique | longueur de phrase (μ, σ, CV), **burstiness**, subordination, virgules/phrase, interrogatives |
| Lisibilité | syllabes/mot, mots longs, indice Flesch (ajusté langue) |
| Mots-outils & connecteurs | ratio de mots-outils, densité de connecteurs formels |
| Marqueurs d'IA | tics lexicaux LLM, hedges, tirets cadratins, guillemets typographiques, contractions, listes |
| Unicité & variété | distinct-2/3, répétition de bigrammes, compression, anaphores, régularité des paragraphes |

Glossaire complet dans `styloscan/features.py` (`FEATURE_GLOSSARY`).

## Limites (à lire)

- **Pas de perplexité réelle** par défaut (aucun modèle téléchargé) : on emploie
  des proxys. Brancher un LM local améliorerait la détection.
- **Score heuristique non calibré** tant qu'aucun corpus n'a servi à
  l'entraînement : à considérer comme indicatif. La voie supervisée est la
  référence.
- **Faux positifs** structurels sur l'écrit académique formel. Le seuil et le
  jeu de features doivent être adaptés à votre discipline et votre langue.

## Structure

```
stylometry-ai/
├── styloscan/           # bibliothèque
│   ├── languages.py     # ressources FR/EN/NL + détection de langue
│   ├── features.py      # extraction des features (catégories interprétables)
│   ├── scoring.py       # score heuristique 0-100 + indices + type d'outil
│   ├── model.py         # RF + validation croisée + F1 + Gini + PCA
│   ├── report.py        # rapports JSON + HTML autonome
│   ├── viz.py           # Gini, PCA, violin plots
│   └── cli.py           # CLI (analyze / features / train / predict)
├── web/                 # mini-app Flask + API JSON
├── notebooks/           # tutoriel reproductible
├── examples/            # textes d'exemple
└── tests/               # tests de fumée
```

## Licence

Outil libre pour usage académique.
