; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "WebAppReader"
#define MyAppVersion "1.3.7"
#define MyAppPublisher "Sergei Shekin"
#define MyAppURL "https://mintguide.org/"
#define MyAppExeName "webappreader.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{C0C3DC62-0811-4395-8011-D5C0ACA2AE33}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL=https://www.linkedin.com/in/sergei-shekin/
AppUpdatesURL=https://mintguide.org/post/webappreader/
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
InfoBeforeFile=C:\Users\Sergei\Desktop\webappreader\Windows\InnoSetup\before_installation.txt
LicenseFile=C:\Users\Sergei\Desktop\webappreader\Windows\InnoSetup\license.txt
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=C:\Users\Sergei\Desktop\webappreader\Windows\InnoSetup
OutputBaseFilename=webappreader_x64_{#MyAppVersion}_setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupLogging=yes
MinVersion=10.0
UninstallDisplayIcon={app}\_internal\src\logo.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "C:\Users\Sergei\Desktop\webappreader\Windows\pyinstaller\dist\webappreader\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
;Source: "C:\Users\Sergei\Desktop\webappreader\Windows\pyinstaller\dist\webappreader\src\*"; DestDir: "{app}\src\"; Flags: ignoreversion recursesubdirs createallsubdirs
;Source: "C:\Users\Sergei\Desktop\webappreader\Windows\pyinstaller\dist\webappreader\wget2.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Sergei\Desktop\webappreader\Windows\pyinstaller\dist\webappreader\_internal\*"; DestDir: "{app}\_internal\"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

