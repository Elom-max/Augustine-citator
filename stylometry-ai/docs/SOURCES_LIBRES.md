# Sources libres de droit pour enrichir le corpus « humain »

Textes du domaine public (auteurs anciens / éditions et traductions anciennes)
utiles pour étoffer la classe **humain** de StyloScan dans le domaine
augustinien et patristique, par langue. Récupérez les fichiers et déposez-les
dans `Google Drive > Divers > fichier expert > Humain` (ou envoyez-les dans le
chat) ; je les ingérerai.

> Pourquoi vous et pas moi ? Le scraping direct est bloqué dans cet
> environnement (proxy : `curl` → 403) et je ne dois pas redistribuer d'œuvres
> sous droits. Les références ci-dessous sont libres de droit ; à vous de
> télécharger les fichiers texte/PDF, à moi de les traiter.

## Latin (texte original)

- **Corpus Corporum** (Univ. Zurich) — dépôt de textes latins avec recherche,
  inclut Augustin : <https://www.mlat.uzh.ch/>
- **Documenta Catholica Omnia** — Pères de l'Église, reprend la *Patrologia
  Latina* de Migne (Augustin = PL 32–47) : <https://www.documentacatholicaomnia.eu/>
- **The Latin Library** — Augustin (sélection) : <https://www.thelatinlibrary.com/august.html>
- **Patrologia Latina (PL), volumes PDF** (recension de R. Pearse) :
  <https://www.roger-pearse.com/weblog/patrologia-latina-pl-volumes-available-online/>

## Français (traductions anciennes, domaine public)

- **Œuvres complètes de Saint Augustin, éd. Raulx (1864-1873)** sur Wikisource :
  <https://fr.wikisource.org/wiki/%C5%92uvres_compl%C3%A8tes_de_Saint_Augustin_(Raulx)>
- **Augustin d'Hippone — page auteur Wikisource** (index des œuvres) :
  <https://fr.wikisource.org/wiki/Auteur:Augustin_d%E2%80%99Hippone>
- **Traduction Péronne/Vincent/Écalle… (Benédictins, 1869-1878, 33 vol.)** via
  Gallica/BnF — texte latin + traduction : catalogue <https://gallica.bnf.fr/>
- **Les Confessions, trad. L. Moreau** (Gallica) :
  <https://gallica.bnf.fr/ark:/12148/bpt6k1170247f>
- **Bibliothèque monastique** (traductions FR en clair, source du *De Trinitate*
  déjà fourni) : <https://www.bibliotheque-monastique.ch/>

## Anglais (traductions anciennes, domaine public)

- **Christian Classics Ethereal Library (CCEL)** — Augustin, trad. NPNF :
  <https://www.ccel.org/fathers.html>
- **New Advent — Church Fathers** (NPNF, Augustin) :
  <https://www.newadvent.org/fathers/>
- **Internet Archive** — éditions anciennes numérisées :
  <https://archive.org/>

## Portails de référence (pour retrouver éditions/traductions)

- **Augustine: Texts and Translations** (J. O'Donnell, Georgetown) :
  <https://faculty.georgetown.edu/jod/augustine/textstrans.html>
- **Augustine Research Guide** (Catholic University of America) :
  <https://guides.lib.cua.edu/c.php?g=590233&p=4079938>

## Conseils pour un corpus exploitable

- Préférez le **texte brut** (.txt) ou un PDF avec couche texte propre ; évitez
  les scans OCR très bruités (l'ingestion nettoie en-têtes/numéros de page, mais
  un OCR trop sale dégrade les features).
- Pour une comparaison **non biaisée** humain vs IA, visez des textes **de même
  langue, registre et longueur** que vos sorties d'IA (idéalement le *même
  sujet/prompt* rédigé par un humain).
- Indiquez la langue dans le nom de fichier si vous le pouvez (sinon la détection
  automatique s'en charge : fr / en / nl / la).
