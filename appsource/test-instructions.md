# Test instructions for Microsoft AppSource validators

Paste this content into Partner Center → "Test instructions for
certification". Microsoft's validators read this verbatim, so keep it
short, concrete, and assume they know nothing about Augustine.

---

## Setup

The add-in requires no sign-in, no account creation and no licence
key. It works against a static HTTPS host (the `taskpane.html` and
`assets/` are served from `https://elom-max.github.io/augustine-citator/`).

There are no special test credentials. Any Microsoft 365 account with
Word desktop or Word Online is sufficient.

## Reproduction steps for the core flow

1. Sideload the manifest (or install from the AppSource preview link).
2. Open a blank Word document.
3. Click the "Cite Augustine" button in the Home ribbon. A task pane
   opens on the right.
4. In the search box, type "conf" (case-insensitive). The list filters
   to *Confessiones*, *Contra Faustum*, etc.
5. Click the "Confessiones" card. A citation builder appears below.
6. In the form, enter Book = "10", Chap. = "27", Para. = "38".
7. The preview at the bottom updates to:
   `Augustin, Confessiones X, 27, 38, ed. L. Verheijen, Corpus Christianorum: Series Latina 27.`
   (Or the equivalent for the selected style — see Settings.)
8. Click "Insérer en note de bas de page".
9. A footnote is inserted at the current cursor position in the Word
   document. A success toast appears at the bottom of the task pane.

Expected result: the footnote contains the formatted citation, with
*Confessiones* in italics. No console errors. No network requests
outside the configured `AppDomains`.

## Test the passage bank

1. Open the Cite tab and click a work (e.g. *Confessiones*).
2. The "Passage de référence" dropdown now lists public-domain
   passages (e.g. "X, 27, 38", "I, 1, 1").
3. Select "X, 27, 38". The form auto-fills Book/Chap./Para., Latin
   ("Sero te amavi…") and French translation.
4. Click Insert. The footnote contains the Latin + French translation
   + reference.

## Test the language switch

1. Open the Settings tab.
2. Change "Langue de votre document" to "English". The whole UI
   relabels in English (placeholders, buttons, tabs).
3. Return to Cite tab; select a work. The card title is shown in
   English where a translation exists.

## Test the CAG import (manual paste, no external request)

The add-in does NOT make any network request to Brepols / CAG. The
"Import CAG" button opens a local modal where the user pastes text
they copied manually from their own subscription.

1. Click "Importer CAG".
2. In the textarea, paste:
   ```
   Augustinus, Confessiones, lib. 10 cap. 27 par. 38
   Sero te amavi, pulchritudo tam antiqua et tam nova.
   ```
3. Click "Analyser".
4. The parsed preview shows: Work = Confessiones, Référence = 10, 27, 38,
   Latin = "Sero te amavi…".
5. Click "Enregistrer". A success toast appears, and the passage is
   added to the work's dropdown under "Mes passages".

## Negative tests

- Search for "xyz123" → list shows "0 works/œuvres/werken", no errors.
- Try to insert without selecting a work → button is disabled.
- Double-click Insert rapidly → only one footnote is inserted (the
  button disables during the async Word.run call).
- Disconnect from Office.js (use the add-in in a plain browser at
  `https://elom-max.github.io/augustine-citator/taskpane.html`) →
  Insert falls back to clipboard copy with a clear toast message.

## Where data is stored

- Citation history and the user's local passage bank are stored in
  Office Document Settings (RoamingSettings) and `localStorage`. They
  never leave the user's device.
- No cookies. No analytics. No external API calls (other than loading
  Google Fonts CSS for the parchment style, which is the standard
  Office Fabric pattern).
