# Privacy Policy — Augustine Citation Tool

*Last updated: 2026-05-20*

Augustine Citation Tool is a Word add-in for inserting formatted
citations from the works of Augustine of Hippo. This page describes
what data, if any, the add-in processes.

## Summary

The add-in does not collect, transmit or share any personal data.
It runs entirely inside Microsoft Word's task pane on your own device.

## What data the add-in processes

1. **Text you type into the citation builder** (book / chapter /
   paragraph numbers, Latin quotation, translated quotation, translator
   name) is used only to produce the citation that the add-in inserts
   into your active Word document. It is never sent to any server.

2. **Citation history** — when you insert a citation, a record of it
   is stored in Word's per-document settings (RoamingSettings) and in
   your browser's `localStorage`, so the History tab can show it back
   to you later. This data stays on your device and inside the Word
   document. It is removed if you delete the document or clear your
   browser data.

3. **Local passage bank** — passages you add via the "Importer CAG"
   button are stored the same way as the citation history. They are
   not transmitted to any third party.

## What data the add-in does NOT process

- No account, no sign-in, no user identifier.
- No analytics, telemetry or usage tracking.
- No cookies.
- No reading of the Word document's existing content beyond the
  cursor position needed to insert the footnote.
- No outbound network requests other than: (a) loading the static
  add-in files (`taskpane.html`, `assets/*.png`,
  `passages.public.json`) from our hosting domain
  `elom-max.github.io`; (b) loading the Microsoft Office.js library
  from `appsforoffice.microsoft.com` (required by every Office
  add-in); (c) loading the Google Fonts stylesheet for the parchment
  typography (standard Office Fabric pattern).

## Third-party services

The add-in itself communicates with no third-party API. The hosting
provider (GitHub Pages, owned by Microsoft) and the Google Fonts CDN
log standard HTTP request metadata (IP address, User-Agent, timestamp)
when the browser fetches the static files. We have no access to those
logs. Their respective privacy policies apply:

- GitHub Pages: <https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement>
- Google Fonts: <https://developers.google.com/fonts/faq/privacy>

If you prefer to avoid the Google Fonts request, the add-in degrades
gracefully to system fonts; the Latin and translations remain readable.

## Data retention

We retain no data because we collect none. Data stored locally on your
device (citation history, local passage bank) is retained until you
manually clear it, delete the parent Word document, or uninstall the
add-in.

## Changes to this policy

If we materially change what the add-in processes, we will bump the
"Last updated" date and describe the change at the top of this page.

## Contact

For privacy questions, open an issue at
<https://github.com/elom-max/augustine-citator/issues>
or e-mail the publisher listed in the AppSource listing.
