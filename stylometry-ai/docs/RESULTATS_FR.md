# Résultats — expérience française (humain vs IA)

Première expérience supervisée sur le corpus réuni (mai 2026). À considérer comme
**exploratoire** : petit échantillon, classes déséquilibrées, sources humaines
peu diversifiées.

## Corpus

| Classe | fr | en | la | nl |
|---|---|---|---|---|
| humain | 23 | 104 | 33 | 0 |
| IA | 118 | 8 | 0 | 1 |

- **IA** : sorties de Claude (×2 fichiers), Grok (×2), ChatGPT, Mistral, Deepseek,
  Gemma/Ollama, Perplexity, Magisterium, JenAi — surtout en français, générées à
  partir d'un même texte source. Après découpage : Claude 63, Grok 28, Mistral 13,
  Gemma 10, autres ≤ 3 échantillons.
- **humain (fr)** : 2 sources seulement (traduction XIXᵉ du *De Trinitate*, article
  *Augustin et Jérôme*). **C'est la principale limite.**
- Seul le **français** a assez des deux classes pour un test. EN : 8 IA seulement.
  Latin : 0 IA. Multi-classes « quel modèle » : trop déséquilibré (Claude domine).

## Random Forest (validation croisée stratifiée 5 plis, classes équilibrées)

| Jeu de features | Accuracy | F1 macro |
|---|---|---|
| Toutes | 98.6 % ± 1.7 | 97.0 % ± 3.7 |
| Sans artefacts de format (guillemets, listes) | 90.7 % ± 6.6 | 82.3 % ± 11.2 |
| Sans artefacts ni registre lexical | 89.3 % ± 2.3 | 77.3 % ± 6.8 |
| Style « pur » (rythme + connecteurs + variété) | 91.5 % ± 3.7 | 77.7 % ± 16.8 |

Top features (importance de Gini, toutes features) : `list_marker_ratio` (0.19),
`curly_quote_ratio` (0.12), `long_word_ratio` (0.11), `mean_word_len` (0.11),
`syllables_per_word` (0.08), `transition_density` (0.06).

## Interprétation

- **Signal réel** : même en retirant artefacts et registre, le style « pur »
  (burstiness, connecteurs, variété n-gramme, redondance) sépare encore les classes
  à ~90 % d'accuracy. La différence humain/IA n'est donc pas qu'un artefact.
- **Confusions qui gonflent le score** :
  - `curly_quote_ratio` — **artefact de source/format** : les sorties IA (.md/.docx)
    emploient des guillemets typographiques, les textes humains (numérisés/anciens)
    des guillemets droits. Aucun rapport avec l'auteur ⇒ à neutraliser.
  - `list_marker_ratio` — en partie signal IA réel, en partie **artefact de genre**
    (l'IA a produit des cours/essais à listes ; l'humain, de la prose continue).
  - `mean_word_len` / `long_word_ratio` — **confusion de registre/époque** (français
    générique moderne vs traduction savante du XIXᵉ).
- **Fragilité** : 23 humains issus de 2 sources ⇒ forte variance (F1 « style pur »
  ±16.8), risque que le modèle apprenne ces 2 auteurs plutôt que « l'humain » en
  général. Ne généralise pas tel quel à d'autres écrits humains français.

## Recommandations

1. **Diversifier la classe humaine FR** : plusieurs auteurs, registre **moderne et
   académique** comparable aux sorties IA (cf. `docs/SOURCES_LIBRES.md`). Viser
   ≥ 30-50 textes humains FR variés.
2. **Apparier genre/sujet/longueur** : idéalement, faire rédiger par des humains le
   *même prompt* que celui soumis aux IA (étalon-or anti-confusion).
3. **Neutraliser la typographie** avant extraction (normaliser guillemets/tirets)
   pour supprimer l'artefact `curly_quote_ratio`.
4. **Ne pas recalibrer les seuils heuristiques FR sur ce seul échantillon** : trop
   petit et confondu, le risque de surajustement est élevé. Attendre un corpus FR
   humain plus large et diversifié.
