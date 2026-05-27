# À faire demain — StyloScan

État au 27/05/2026 : outil complet (FR/EN/NL/latin), corpus exploratoire ingéré,
1ʳᵉ expérience FR faite (cf. `docs/RESULTATS_FR.md`). Le corpus est **local**
(gitignoré) : il faudra le **réingérer** demain depuis Drive (conteneur éphémère).

## Priorité 1 — Réhydrater le corpus (5 min, au début de la session)

Le dossier `corpus/` ne survit pas à la fin de session. Demandez-moi simplement :
« réingère le corpus depuis Drive ». Je relancerai le téléchargement
(`Drive > Divers > fichier expert > IA` et `Humain`) + l'ingestion. Rien à faire
de votre côté.

## Priorité 2 — Enrichir la classe humaine française (LE point bloquant)

*Pourquoi :* aujourd'hui seulement 23 échantillons FR issus de **2 sources** → le
modèle risque d'apprendre 2 auteurs, pas « l'humain ». Objectif : **30-50 textes
FR variés**, registre académique **moderne** (comparable aux sorties IA).

*Comment :*
1. Piochez dans `docs/SOURCES_LIBRES.md` (Wikisource Raulx, Gallica, CCEL…) **et**
   dans votre Zotero/bibliothèque : articles récents, chapitres, vos propres écrits.
2. Déposez les fichiers (.txt/.pdf/.docx) dans `Drive > … > fichier expert > Humain`.
3. Dites-moi « ré-ingère et ré-entraîne ».

*Idéal (étalon-or) :* faire rédiger par un humain **le même prompt** que celui
soumis aux IA → supprime la confusion genre/sujet.

## Priorité 3 — Neutraliser l'artefact typographique (15 min, côté code)

*Pourquoi :* `curly_quote_ratio` (guillemets « " " » vs droits) gonfle le score
sans rien dire de l'auteur — c'est un artefact de format.

*Comment (moi) :* normaliser guillemets/tirets/apostrophes dans `features.py`
avant extraction, retirer `curly_quote_ratio` des features discriminantes, puis
ré-entraîner et comparer. Dites « applique la normalisation typographique ».

## Priorité 4 — Compléter IA pour l'anglais et le latin

*Pourquoi :* EN = 8 IA seulement, latin = 0 IA → pas de test possible hors FR.

*Comment (vous) :* soumettre le **même texte/prompt** à plusieurs modèles en
anglais (et en latin si vous voulez tester l'augustinien), enregistrer en nommant
par modèle (`par Claude.docx`…) dans `… > fichier expert > IA`. Visez ≥ 5 modèles.

## Priorité 5 — Ré-entraîner, comparer, interpréter (moi)

Une fois le corpus enrichi :
- RF + CV 5 plis **par langue** (FR, puis EN si assez d'IA) ;
- test de robustesse (avec/sans artefacts) pour voir si le signal « pur » tient ;
- importance de Gini → vérifier qu'on ne « triche » plus ;
- si le corpus FR humain est devenu large et diversifié : **recalibrer les seuils
  heuristiques FR** de `scoring.py` (reporté aujourd'hui faute de données fiables).

## Optionnel — « Quel modèle ? » (multi-classes)

Quand chaque modèle aura assez d'échantillons (≥ 15-20), matrice de confusion
inter-modèles. Aujourd'hui trop déséquilibré (Claude domine).

---
### Récap des commandes utiles (pour mémoire)
```
PYTHONPATH=. python3 tests/test_features.py                      # tests
PYTHONPATH=. python3 -m styloscan.cli analyze fichier.txt --html r.html
PYTHONPATH=. python3 -m styloscan.cli train <dir> --lang fr --gini-plot g.png
```
Branche de travail : `claude/video-speech-ai-analysis-xZ9EV`.
