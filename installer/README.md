# Windows installer (Inno Setup)

This folder produces a single `.exe` installer that registers Augustinus
Citator as a trusted Word add-in catalog — so the user double-clicks the
`.exe`, opens Word, and the add-in is there. No manual sideloading.

## How it works

Word can be configured to trust a folder as an add-in catalog via a per-user
registry key under `HKCU\Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\`.
The installer:

1. Copies the production `manifest.xml` to `%LOCALAPPDATA%\AugustinusCitator\`.
2. Writes the registry key pointing Word at that folder.
3. Cleans up both on uninstall.

The actual `taskpane.html` and `assets/` stay on a public HTTPS host
(GitHub Pages, Netlify, etc.) — the manifest just tells Word where to
load them from. The installer does NOT bundle the HTML/JS.

## Prerequisites

- **Inno Setup 6+** installed on a Windows machine —
  <https://jrsoftware.org/isinfo.php> (free, MIT-style license).
- A public HTTPS host serving `taskpane.html`, `assets/`, and
  `passages.public.json`. The simplest is GitHub Pages (the workflow
  `.github/workflows/pages.yml` does that automatically on push to `main`).

## Build steps

### 1. Generate the production manifest

The repo's root `manifest.xml` is a template with `YOUR-DOMAIN.example`
as a placeholder. Substitute it with the real host (without protocol):

```bash
# Linux/macOS
cd installer/
./build-manifest.sh elom-max.github.io/augustine-citator
```

```powershell
# Windows
cd installer\
.\build-manifest.ps1 -HostName elom-max.github.io/augustine-citator
```

This writes `installer/manifest.xml`.

### 2. Compile the installer

Open `AugustinusCitator.iss` in Inno Setup Compiler and press **Compile**
(or run `ISCC.exe AugustinusCitator.iss` from the command line). The
output `.exe` is written to `installer/output/AugustinusCitator-Setup.exe`.

### 3. Distribute

Share the `.exe` directly, or attach it to a GitHub Release. Users
double-click → installer runs → Word picks up the trusted catalog
automatically on next launch.

## What the user sees

1. Double-click `AugustinusCitator-Setup.exe`.
2. Click through the standard install wizard (5 seconds).
3. Open Word (or restart Word if already open).
4. **Insert → Add-ins → My Add-ins → SHARED FOLDER tab** → select
   "Augustine Citation Tool" → click Add.
5. The "Cite Augustine" button is in the Home ribbon.

The "Shared Folder" tab is the standard Microsoft entry point for
catalog-registered add-ins. Users only need to do this once per
machine; the add-in stays in their Recently Used list.

## macOS / Linux equivalent

Microsoft Word on macOS reads sideloaded manifests from:

```
~/Library/Containers/com.microsoft.Word/Data/Documents/wef/
```

To install on Mac without an installer, drop the production `manifest.xml`
into that folder and restart Word. We do not ship a `.pkg` installer
because the registry-based "Trusted Catalog" mechanism is Windows-only;
on Mac the manifest-in-folder approach is what Microsoft documents.

A shell one-liner the user can run:

```bash
HOST=elom-max.github.io/augustine-citator
mkdir -p ~/Library/Containers/com.microsoft.Word/Data/Documents/wef
curl -s "https://${HOST}/manifest.xml" \
  > ~/Library/Containers/com.microsoft.Word/Data/Documents/wef/AugustinusCitator.xml
```

## Uninstall

Windows: standard "Add or Remove Programs" → Augustinus Citator → Uninstall.
This removes the manifest folder and registry key. Office picks up the
removal on the next Word restart.

macOS: delete the manifest file from
`~/Library/Containers/com.microsoft.Word/Data/Documents/wef/`.
