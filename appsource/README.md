# AppSource submission kit

This folder contains everything needed to submit Augustine Citation
Tool to Microsoft AppSource (the Office add-ins store).

## Files

- **`SUBMISSION-CHECKLIST.md`** — go through this from top to bottom
  before clicking Submit in Partner Center.
- **`store-listing.md`** — the copy (name, descriptions, search terms,
  categories) you paste into the Partner Center listing form.
- **`test-instructions.md`** — paste this into the Partner Center
  "Test instructions for certification" field so Microsoft validators
  know how to exercise the add-in.
- **`PRIVACY-POLICY.md`** — required by AppSource. Host it publicly
  (e.g. `https://elom-max.github.io/augustine-citator/privacy.html`)
  and put that URL in Partner Center.
- **`TERMS-OF-USE.md`** — required by AppSource. Host and link
  similarly.

## Order of operations

1. Run the GitHub Pages workflow (push to `main`) so the production
   `taskpane.html` is live at the URL you'll declare to Microsoft.
2. Convert `PRIVACY-POLICY.md` and `TERMS-OF-USE.md` to HTML (any
   Markdown renderer; `pandoc -s --metadata title="Privacy Policy"
   PRIVACY-POLICY.md -o ../privacy.html` works) and commit them to the
   repo so the Pages workflow publishes them too.
3. Open Partner Center → Office → New product → "Add-in for Word".
4. Walk through `SUBMISSION-CHECKLIST.md` step by step.
5. Submit.

Expected first-submission turnaround: 3-10 business days. Be ready to
bump the manifest `Version` for a resubmission if the validators come
back with a request.
