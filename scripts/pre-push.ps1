# pre-push.ps1
# Checklist guiado antes de fazer push para o GitHub.
# Uso: .\scripts\pre-push.ps1
#
# Valida o estado do git e exibe os agents a invocar no Claude Code.

Set-Location (Split-Path $PSScriptRoot)

$GREEN  = "Green"
$YELLOW = "Yellow"
$RED    = "Red"
$CYAN   = "Cyan"
$GRAY   = "DarkGray"

function Header([string]$text) {
    Write-Host ""
    Write-Host "--------------------------------------------" -ForegroundColor $GRAY
    Write-Host "  $text" -ForegroundColor $CYAN
    Write-Host "--------------------------------------------" -ForegroundColor $GRAY
}

function Ok([string]$msg)   { Write-Host "  [OK]  $msg" -ForegroundColor $GREEN  }
function Warn([string]$msg) { Write-Host "  [!]   $msg" -ForegroundColor $YELLOW }
function Fail([string]$msg) { Write-Host "  [X]   $msg" -ForegroundColor $RED    }
function Info([string]$msg) { Write-Host "        $msg" -ForegroundColor $GRAY   }

# ── Detecta release branch (usado em varias secoes) ──────────────────────────
$RELEASE_BRANCH = git branch --list "release/*" 2>$null |
    ForEach-Object { $_ -replace '^\*?\s+', '' } |
    Select-Object -First 1

# ── 1. Branch atual ──────────────────────────────────────────────────────────
Header "1. Branch atual"

$BRANCH = git rev-parse --abbrev-ref HEAD 2>$null
if (-not $BRANCH) { Fail "Nao e um repositorio Git."; exit 1 }

Write-Host "  Branch: " -NoNewline
Write-Host $BRANCH -ForegroundColor $CYAN

if ($BRANCH -eq "main") {
    Fail "Voce esta na main. Nunca commite direto na main."
    Info ""
    Info "  Crie uma feature branch a partir da release:"
    if ($RELEASE_BRANCH) {
        Info "    git checkout $RELEASE_BRANCH"
    } else {
        Info "    git checkout release/<data>"
    }
    Info "    git checkout -b feat/nome-da-feature"
    exit 1
}

if ($BRANCH -like "release/*") {
    Fail "Voce esta diretamente na branch release. Nunca commite aqui."
    Info ""
    Info "  Crie uma feature branch a partir desta release e commite nela:"
    Info "    git checkout -b feat/nome-da-feature"
    Info "    # faca seus commits na feature branch"
    Info "    # depois mergeie de volta: git checkout $BRANCH && git merge --no-ff feat/nome"
    exit 1
}

# ── 2. Branch release atual ──────────────────────────────────────────────────
Header "2. Branch release"

if ($RELEASE_BRANCH) {
    Ok "Release atual: $RELEASE_BRANCH"
} else {
    Fail "Nenhuma branch release/* encontrada."
    Warn "Crie com o agente de release no Claude Code."
}

# ── 3. Arquivos proibidos ─────────────────────────────────────────────────────
Header "3. Verificacao de seguranca"

$STAGED = git diff --cached --name-only 2>$null
$HAS_BLOCKED = $false

foreach ($file in $STAGED) {
    if ($file -eq "config.py" -or $file -like "*.db" -or
        $file -eq "user_prefs.json" -or $file -eq "verse_cache.json") {
        Fail "Arquivo proibido no staged: $file"
        $HAS_BLOCKED = $true
    }
}

if (-not $HAS_BLOCKED) { Ok "Nenhum arquivo sensivel no staged." }

# ── 4. Alteracoes pendentes ───────────────────────────────────────────────────
Header "4. Estado das alteracoes"

$UNSTAGED     = git diff --name-only 2>$null
$STAGED_FILES = git diff --cached --name-only 2>$null
$UNTRACKED    = git ls-files --others --exclude-standard 2>$null

if ($STAGED_FILES) {
    Ok "$($STAGED_FILES.Count) arquivo(s) em stage:"
    $STAGED_FILES | ForEach-Object { Info "    $_" }
} else {
    Warn "Nenhum arquivo em stage."
}

if ($UNSTAGED) {
    Warn "$($UNSTAGED.Count) arquivo(s) modificados mas nao adicionados:"
    $UNSTAGED | ForEach-Object { Info "    $_" }
}

if ($UNTRACKED) {
    Warn "$($UNTRACKED.Count) arquivo(s) nao rastreados:"
    $UNTRACKED | Select-Object -First 10 | ForEach-Object { Info "    $_" }
}

# ── 5. Commits a frente da release ───────────────────────────────────────────
Header "5. Commits na branch atual"

if ($RELEASE_BRANCH) {
    $AHEAD = git log "$RELEASE_BRANCH..HEAD" --oneline 2>$null
    if ($AHEAD) {
        Ok "$($AHEAD.Count) commit(s) a frente de $RELEASE_BRANCH :"
        $AHEAD | ForEach-Object { Info "    $_" }
    } else {
        Warn "Nenhum commit a frente da release. Branch vazia ou ja mergeada?"
    }
}

# ── 6. Checklist de agents ────────────────────────────────────────────────────
Header "6. Agents para invocar no Claude Code (nessa ordem)"

Write-Host ""
Write-Host "  Corrija os problemas de cada agent antes de passar ao proximo." -ForegroundColor $GRAY
Write-Host ""
Write-Host "  [ ]  1. qa          -> revisao de qualidade geral" -ForegroundColor $YELLOW
Write-Host "  [ ]  2. code-review -> analise tecnica profunda" -ForegroundColor $YELLOW
Write-Host "  [ ]  3. peer-review -> perspectiva critica de colega" -ForegroundColor $YELLOW
Write-Host "  [ ]  4. commit      -> commit semantico (na feature branch)" -ForegroundColor $YELLOW
Write-Host "  [ ]  5. merge-guard -> valida seguranca do merge na release" -ForegroundColor $YELLOW
Write-Host ""
Write-Host "  Se for deploy para producao, adicione:" -ForegroundColor $GRAY
Write-Host "  [ ]  6. release     -> versao + release notes + nova release branch" -ForegroundColor $GRAY
Write-Host "  [ ]  7. deploy      -> build do .exe via PyInstaller" -ForegroundColor $GRAY
Write-Host ""

# ── 7. Comandos git prontos ───────────────────────────────────────────────────
Header "7. Comandos git (rode apos todos os agents)"

Write-Host ""
Write-Host "  # Subir a feature branch:" -ForegroundColor $GRAY
Write-Host "  git push -u origin $BRANCH" -ForegroundColor $GREEN
Write-Host ""

if ($RELEASE_BRANCH) {
    Write-Host "  # Mergear na release (apos aprovacao):" -ForegroundColor $GRAY
    Write-Host "  git checkout $RELEASE_BRANCH" -ForegroundColor $GREEN
    Write-Host "  git merge --no-ff $BRANCH" -ForegroundColor $GREEN
    Write-Host "  git branch -d $BRANCH" -ForegroundColor $GREEN
    Write-Host "  git push origin --delete $BRANCH" -ForegroundColor $GREEN
    Write-Host ""
}

Write-Host "  Consulte .claude\WORKFLOW.md para o fluxo completo." -ForegroundColor $GRAY
Write-Host ""
