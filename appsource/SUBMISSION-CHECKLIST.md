# AppSource submission checklist — Augustine Citation Tool

Microsoft AppSource (the Office Add-ins store) reviews every submission
against its validation policies. Use this checklist before clicking
"Submit" in Partner Center to avoid the typical 1-2 week back-and-forth.

## 1. Partner Center account (one-off, ~1 hour)

- [ ] Create a Microsoft Partner Center account at
  <https://partner.microsoft.com/dashboard/office/>.
- [ ] Complete the **publisher profile** (legal name, address, tax info).
  This is the name that appears as "Publisher" on AppSource.
- [ ] Verify the publisher e-mail.
- [ ] Either: pay the one-time **registration fee** (USD 19 individual,
  USD 99 company) for the Microsoft Developer programme — required to
  publish, even free add-ins. *Universities sometimes have a free path
  via their Microsoft education licence — check with KUL IT.*

## 2. Public hosting (must be live BEFORE submission)

AppSource will fetch your `taskpane.html`, `assets/`, and `manifest.xml`
from public HTTPS URLs during validation. The `.github/workflows/pages.yml`
in this repo deploys exactly that on push to `main`.

- [ ] GitHub Pages is enabled (repo → Settings → Pages → Source =
  "GitHub Actions").
- [ ] The Pages URL `https://elom-max.github.io/augustine-citator/`
  returns HTTP 200 with a valid TLS certificate.
- [ ] `…/manifest.xml` is downloadable and has **no** `YOUR-DOMAIN.example`
  placeholder.
- [ ] `…/taskpane.html` loads in an incognito browser window without
  console errors.
- [ ] `…/assets/icon-16.png`, `…/icon-32.png`, `…/icon-64.png`,
  `…/icon-80.png` are all reachable.
- [ ] `…/passages.public.json` returns valid JSON.

## 3. Required URLs hosted publicly

AppSource requires these three URLs to exist on your domain (or a domain
you control) before submission:

- [ ] **Privacy policy** — a public page describing what the add-in does
  with user data. See `appsource/PRIVACY-POLICY.md` for a starter you
  can publish at `https://elom-max.github.io/augustine-citator/privacy.html`.
- [ ] **Terms of use** — same: see `appsource/TERMS-OF-USE.md`.
- [ ] **Support URL** — a page or e-mail where users can request help.
  Re-using the GitHub Issues page (`https://github.com/elom-max/augustine-citator/issues`)
  is acceptable.

Update these in Partner Center → Properties → URLs (NOT in the manifest).

## 4. Manifest validation

- [ ] Run the official validator (no install needed):
  ```bash
  npx office-addin-validator manifest.xml
  ```
  Expected: "The manifest is valid."
- [ ] `Id` GUID is unique and not reused from another add-in
  (this repo uses `b4e2d9c1-8f7a-4b3c-9a2d-1e5f8c7b6a4d`).
- [ ] `Version` is `1.0.0.0` for the first submission, then bump for
  each resubmission (AppSource refuses to validate the same version).
- [ ] `SupportUrl` resolves over HTTPS.
- [ ] `IconUrl`, `HighResolutionIconUrl` and all `<bt:Image>` URLs are
  served with `Content-Type: image/png` (the GitHub Pages workflow does
  this; if hosting elsewhere check).

## 5. Add-in functional requirements (Microsoft tests these)

- [ ] The add-in loads within 5 seconds on a 4G connection (target).
- [ ] **No telemetry, no analytics** that send personally identifiable
  information without explicit opt-in. *This add-in has none — confirm
  no Google Analytics / Sentry / etc. is added later.*
- [ ] Works in Word desktop (Windows + Mac), Word Online, Word iPad.
  *Test all four before submitting.*
- [ ] Works in all manifest-declared locales (this add-in supports
  en-US default; FR/EN/NL via UI selector).
- [ ] Handles offline / poor-network gracefully (the add-in already
  falls back to clipboard if Office.js isn't ready).
- [ ] No console errors during typical usage.

## 6. Store listing assets (created in Partner Center, NOT in repo)

You'll need to upload these during the listing step:

- [ ] **App name**: "Augustine Citation Tool"
- [ ] **Short description** (100 chars max): see `store-listing.md`
- [ ] **Long description** (4000 chars max): see `store-listing.md`
- [ ] **Search terms** (7 max, 30 chars each): see `store-listing.md`
- [ ] **Categories**: Productivity (primary) + Education (secondary)
- [ ] **Logo** (300x300 PNG): generate from `assets/logo.png`
- [ ] **Screenshots** (1-5 PNG, 1366x768 each):
  - Cite tab with a work selected and citation built
  - Settings tab showing the language and style options
  - History tab with a few citations
  - The CAG import modal (without showing actual CAG content)
  - A Word document with an inserted footnote citation
- [ ] **Video** (optional, but boosts approval): 60-90s screencast.

## 7. Microsoft validator test account

Microsoft's validators need a way to test your add-in. They use a
generic Microsoft 365 account; you do NOT need to provide one for this
add-in (no login required). But:

- [ ] Fill in `appsource/test-instructions.md` content into Partner
  Center → "Test environment & instructions for certification".
- [ ] Re-verify the add-in still works in a fresh Word install without
  any prior state.

## 8. Accessibility (WCAG 2.1 AA)

Microsoft increasingly enforces accessibility. Verify:

- [ ] All interactive elements have `aria-label` or visible text.
- [ ] Colour contrast ratio ≥ 4.5:1 for normal text. *Current parchment
  + ink colour scheme: contrast ratio measured at 11.6:1 — passes.*
- [ ] Keyboard navigation: Tab key reaches all controls; Esc closes the
  CAG import modal.
- [ ] No flashing/blinking content (we have none).

## 9. Submit

- [ ] Partner Center → Office → Augustine Citation Tool → Submit.
- [ ] Wait for the validation e-mail (typically 3-10 business days).
- [ ] If rejected, the e-mail lists exact reasons. Fix, bump `Version`
  to `1.0.0.1` in the manifest, redeploy GitHub Pages, resubmit.

## Useful links

- Submission process: <https://learn.microsoft.com/office/dev/store/submit-to-appsource-via-partner-center>
- Validation policies: <https://learn.microsoft.com/office/dev/store/validation-policies>
- Manifest schema reference: <https://learn.microsoft.com/javascript/api/manifest>
- Word JS API support matrix: <https://learn.microsoft.com/javascript/api/requirement-sets/word/word-api-requirement-sets>
