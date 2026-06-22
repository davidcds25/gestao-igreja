# scripts/build_installer.ps1
# Gera o instalador completo do sistema: app.exe + VLC embutido
#
# Uso:
#   .\scripts\build_installer.ps1
#   .\scripts\build_installer.ps1 -SkipPyInstaller   (usa dist\ existente)
#   .\scripts\build_installer.ps1 -SkipVlcDownload   (usa build\vlc-installer.exe existente)

param(
    [switch]$SkipPyInstaller,
    [switch]$SkipVlcDownload
)

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot

Set-Location $Root

# Usa o Python do venv se existir, senão usa o do PATH
$PythonExe = if (Test-Path "venv\Scripts\python.exe") { "venv\Scripts\python.exe" } else { "python" }
Write-Host "Python: $PythonExe" -ForegroundColor Gray

# ── 1. PyInstaller ─────────────────────────────────────────────────────────
if (-not $SkipPyInstaller) {
    Write-Host "`n[1/3] Gerando executável com PyInstaller..." -ForegroundColor Cyan
    & $PythonExe -m PyInstaller --onefile --windowed --name "gestao-igreja" main.py
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller falhou (exit $LASTEXITCODE)" }
    Write-Host "Executável gerado: dist\gestao-igreja.exe" -ForegroundColor Green
} else {
    Write-Host "`n[1/3] Pulando PyInstaller (flag -SkipPyInstaller)" -ForegroundColor Yellow
    if (-not (Test-Path "dist\gestao-igreja.exe")) {
        throw "dist\gestao-igreja.exe não encontrado. Remova -SkipPyInstaller ou gere antes."
    }
}

# ── 2. VLC installer ───────────────────────────────────────────────────────
$BuildDir     = Join-Path $Root "build"
$VlcInstaller = Join-Path $BuildDir "vlc-installer.exe"
$VlcUrl       = "https://download.videolan.org/pub/videolan/vlc/3.0.23/win64/vlc-3.0.23-win64.exe"

if (-not (Test-Path $BuildDir)) {
    New-Item -ItemType Directory -Path $BuildDir | Out-Null
}

if (-not $SkipVlcDownload -and -not (Test-Path $VlcInstaller)) {
    Write-Host "`n[2/3] Baixando instalador do VLC (~44 MB)..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $VlcUrl -OutFile $VlcInstaller -UseBasicParsing
    Write-Host "Download concluído." -ForegroundColor Green
} elseif (Test-Path $VlcInstaller) {
    $vlcSizeMB = [math]::Round((Get-Item $VlcInstaller).Length / 1MB, 1)
    Write-Host "`n[2/3] VLC installer encontrado (${vlcSizeMB} MB): build\vlc-installer.exe" -ForegroundColor Green
} else {
    Write-Host "`n[2/3] Pulando download do VLC (flag -SkipVlcDownload)" -ForegroundColor Yellow
    Write-Host "      AVISO: instalador gerado não incluirá o VLC." -ForegroundColor Yellow
}

# ── 3. Inno Setup ──────────────────────────────────────────────────────────
Write-Host "`n[3/3] Compilando instalador com Inno Setup..." -ForegroundColor Cyan

$IsccCandidates = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
)
$ISCC = $IsccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $ISCC) {
    throw "Inno Setup 6 não encontrado.`nInstale via: winget install JRSoftware.InnoSetup"
}
Write-Host "Inno Setup: $ISCC" -ForegroundColor Gray

& $ISCC (Join-Path $Root "installer.iss")
if ($LASTEXITCODE -ne 0) { throw "Inno Setup falhou (exit $LASTEXITCODE)" }

# ── Resultado ──────────────────────────────────────────────────────────────
$Output = Get-ChildItem (Join-Path $Root "dist") -Filter "gestao-igreja-setup-*.exe" |
          Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($Output) {
    $sizeMB = [math]::Round($Output.Length / 1MB, 1)
    Write-Host "`n✅ Instalador pronto: $($Output.Name) (${sizeMB} MB)" -ForegroundColor Green
    Write-Host "   Caminho: $($Output.FullName)" -ForegroundColor Gray
} else {
    Write-Host "`n✅ Instalador gerado em dist\" -ForegroundColor Green
}
