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

*Décidé avec l'utilisateur (cadrage du 27/05) :*
- **Étendue : tout le Drive, par mots-clés.** Je recherche dans l'ensemble du Drive
  les articles/livres du domaine (augustinien, patristique, philosophie ancienne,
  rhétorique/théologie), **je soumets la liste des fichiers trouvés AVANT toute
  ingestion**, et je n'extrais qu'après feu vert. Contenu gardé hors de mon
  contexte (via sous-agent), rien n'est reproduit.
- **Langues : FR et EN moderne en parallèle** (combler FR en priorité de fait,
  mais collecter les deux).
- Mots-clés de départ : Augustin/Augustine, Hippone, *De Trinitate*, *Confessiones*,
  *De ordine*, *De doctrina christiana*, patristique, rhétorique antique, Lamberigts,
  Dupont… (à ajuster).
- Déclencheur demain : « cherche des textes humains dans mon Drive ».

*Compléments :*
- `docs/SOURCES_LIBRES.md` (Wikisource, Gallica, CCEL…) si besoin de plus.
- **reMarkable : non accessible** ici (pas de connecteur). Synchroniser
  reMarkable → Drive, ou exporter les PDF vers Drive, pour que je puisse les lire.
- Préférer des sources **nées-numériques** (cf. Priorité 3 : typographie fiable).

*Idéal (étalon-or) :* faire rédiger par un humain **le même prompt** que celui
soumis aux IA → supprime la confusion genre/sujet.

## Priorité 3 — Exploiter la typographie comme SIGNATURE (et non la supprimer)

*Constat de l'utilisateur (validé) :* la typographie est un **critère discriminant**
des outils IA — tiret cadratin (—) sur-employé par ChatGPT, guillemets droits de
Claude, guillemets courbes d'autres, puces, etc. On la **conserve et on l'enrichit**.

*Comment (moi) :*
- Garder `emdash_per_1k`, `curly_quote_ratio`, `list_marker_ratio` ; ajouter des
  **signatures par modèle** dans `_guess_tool` (`scoring.py`) : ex. em-dash élevé →
  ChatGPT ; guillemets droits + peu de puces → Claude ; etc.
- **Garde-fou anti-confusion** (≠ neutralisation) : ne comparer que des textes à
  **chaîne de mise en forme comparable**. Préférer des sources humaines
  **nées-numériques** (pas d'OCR de scans anciens) pour que la typographie reflète
  l'auteur et non la numérisation. Quand ce n'est pas possible, signaler la réserve.
- Dire « ajoute les signatures typographiques par modèle » pour lancer ce volet.

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
