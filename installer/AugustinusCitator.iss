; Inno Setup script for Augustinus Citator (Windows installer)
;
; This installer registers a "Trusted Catalog" so Word loads the add-in as if
; it were sideloaded — no need for the user to click Insert > Upload My Add-in.
;
; The catalog is per-user (HKCU) so no admin privileges are required.
;
; Build:
;   1. Generate installer/manifest.xml with the production host URL substituted.
;      See installer/build-manifest.sh (Linux/macOS) or build-manifest.ps1
;      (Windows). Example:
;        bash build-manifest.sh elom-max.github.io/augustine-citator
;   2. Open this .iss in Inno Setup Compiler (https://jrsoftware.org/isinfo.php)
;      and click Compile. Output goes to installer/output/.

#define AppName "Augustinus Citator"
#define AppVersion "1.0.0"
#define AppPublisher "Augustinus Citator"
#define AppExeName "AugustinusCitator-Setup"
; This GUID identifies the Trusted Catalog entry in the Windows registry.
; It is fixed so that uninstall removes the same key the install created.
#define CatalogGuid "{F8E7D9C0-3A4B-4C5D-9E1F-2A3B4C5D6E7F}"

[Setup]
; Inno Setup AppId; brace-doubled per Inno conventions.
AppId={{F8E7D9C0-3A4B-4C5D-9E1F-2A3B4C5D6E7F}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\AugustinusCitator
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=output
OutputBaseFilename={#AppExeName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName={#AppName}

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "fr"; MessagesFile: "compiler:Languages\French.isl"
Name: "nl"; MessagesFile: "compiler:Languages\Dutch.isl"

[Files]
; The manifest must have been built with the production host URL before
; running ISCC. See installer/build-manifest.*.
Source: "manifest.xml"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
; Register the install folder as a Word Trusted Catalog. Flag 1 = "show in menu".
Root: HKCU; Subkey: "Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{#CatalogGuid}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{#CatalogGuid}"; ValueType: string; ValueName: "Id"; ValueData: "{#CatalogGuid}"
Root: HKCU; Subkey: "Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{#CatalogGuid}"; ValueType: string; ValueName: "Url"; ValueData: "{app}"
Root: HKCU; Subkey: "Software\Microsoft\Office\16.0\WEF\TrustedCatalogs\{#CatalogGuid}"; ValueType: dword; ValueName: "Flags"; ValueData: 1

[Messages]
en.SetupAppTitle=Augustinus Citator setup
fr.SetupAppTitle=Installation Augustinus Citator
nl.SetupAppTitle=Augustinus Citator installatie

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox(
      'Augustinus Citator is installed.' + #13#10 + #13#10 +
      '1. Close all Word windows (if any are open).' + #13#10 +
      '2. Re-open Word.' + #13#10 +
      '3. Go to: Insert -> Add-ins -> My Add-ins -> SHARED FOLDER tab.' + #13#10 +
      '4. Select "Augustine Citation Tool" and click Add.' + #13#10 + #13#10 +
      'The "Cite Augustine" button will appear in the Home ribbon.',
      mbInformation, MB_OK);
  end;
end;
