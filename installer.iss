; Nazmul Tweaks Tool — Inno Setup installer
; Build: scripts\build_installer.ps1

#ifndef MyAppVersion
  #define MyAppVersion "1.0.18"
#endif

#define MyAppName "Nazmul Tweaks Tool"
#define MyAppPublisher "MD Nazmul Hasan"
#define MyAppURL "https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool"
#define MyAppExeName "Nazmul Tweaks Tool.exe"

[Setup]
AppId={{A7B3C9D1-E5F2-4A8B-9C0D-1E2F3A4B5C6D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases/latest
DefaultDirName={localappdata}\NazmulTweaksTool
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=installer
OutputBaseFilename=Nazmul-Tweaks-Tool-Setup-v{#MyAppVersion}
SetupIconFile=assets\logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "release\Nazmul-Tweaks-Tool.exe"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion
Source: "assets\logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\github-mark.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\logo.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\logo.ico"; Tasks: desktopicon
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  VerFile: string;
  VerContent: string;
begin
  if CurStep = ssPostInstall then
  begin
    VerFile := ExpandConstant('{app}\version.txt');
    VerContent := '{#MyAppVersion}';
    SaveStringToFile(VerFile, VerContent, False);
  end;
end;