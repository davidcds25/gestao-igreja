; Gestão Igreja — Script Inno Setup
; Para gerar o instalador: scripts\build_installer.ps1

#define AppName      "Gestão Igreja"
#define AppVersion   "1.3.0"
#define AppPublisher "Projeto Gestão Igreja"
#define AppExeName   "gestao-igreja.exe"

[Setup]
AppId={{8F5A2B1C-4D9E-4F6B-A3C7-2E8D1B9F0A5C}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
; Instala em AppData\Local — pasta gravável pelo usuário sem elevação
; O app precisa criar config.py, igreja.db etc. no mesmo diretório do exe
DefaultDirName={localappdata}\GestaoIgreja
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=dist
OutputBaseFilename=gestao-igreja-setup-{#AppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=lowest
WizardStyle=modern
SetupIconFile=
UninstallDisplayName={#AppName}

[Languages]
Name: "pt_BR"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Ícones:"; Flags: checkedonce

[Files]
; Executável principal
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Instalador do VLC — copiado para temp e apagado após uso
; Só é incluído quando o arquivo existe (gerado pelo script de build)
Source: "build\vlc-installer.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: NeedVLC

[Icons]
Name: "{group}\{#AppName}";               Filename: "{app}\{#AppExeName}"
Name: "{group}\Desinstalar {#AppName}";   Filename: "{uninstallexe}"
Name: "{commondesktop}\{#AppName}";       Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
; Instala VLC silenciosamente se não detectado — shellexec aciona o UAC automaticamente
Filename: "{tmp}\vlc-installer.exe"; Parameters: "/S"; \
  StatusMsg: "Instalando VLC (suporte a vídeo)..."; \
  Check: NeedVLC; Flags: shellexec waituntilterminated

; Oferece iniciar o app após a instalação
Filename: "{app}\{#AppExeName}"; Description: "Iniciar {#AppName}"; \
  Flags: nowait postinstall skipifsilent

[Code]
{ Retorna True se o VLC NÃO está instalado — dispara a instalação silenciosa }
function NeedVLC: Boolean;
begin
  Result := not FileExists('C:\Program Files\VideoLAN\VLC\libvlc.dll') and
            not FileExists('C:\Program Files (x86)\VideoLAN\VLC\libvlc.dll');
end;
