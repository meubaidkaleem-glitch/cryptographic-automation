#define MyAppName "AutoCrypt"
#define MyAppVersion "0.3.0"
#define MyAppPublisher "AutoCrypt Project"
#define MyAppExeName "AutoCrypt.exe"

[Setup]
AppId={{F06E2B45-9AA6-4E8E-AE53-1D9D86D12A10}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\AutoCrypt
DefaultGroupName=AutoCrypt
DisableProgramGroupPage=yes
OutputDir=..\release
OutputBaseFilename=AutoCrypt-Setup-Windows-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
UninstallDisplayIcon={app}\AutoCrypt.exe

[Files]
Source: "..\dist\AutoCrypt\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AutoCrypt"; Filename: "{app}\AutoCrypt.exe"
Name: "{autodesktop}\AutoCrypt"; Filename: "{app}\AutoCrypt.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\AutoCrypt.exe"; Description: "Launch AutoCrypt"; Flags: postinstall nowait skipifsilent
