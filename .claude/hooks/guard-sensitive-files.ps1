$ErrorActionPreference = 'SilentlyContinue'
try {
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }

    $data = $raw | ConvertFrom-Json
    $cmd  = $data.tool_input.command
    if ([string]::IsNullOrWhiteSpace($cmd)) { exit 0 }
    if ($cmd -notmatch '^\s*git\s+add\b') { exit 0 }

    # Extrai apenas os argumentos após "git add" para não casar padrões em mensagens de commit
    $afterAdd = ($cmd -replace '^.*?git\s+add\s*', '')
    $blocked = $afterAdd -match '(?<![A-Za-z0-9_\-])config\.py|user_prefs\.json|verse_cache\.json|\.db\b'
    if ($blocked) {
        [Console]::Error.WriteLine('BLOQUEADO: arquivo sensivel detectado no git add.')
        [Console]::Error.WriteLine('Nao commitar config.py, *.db, user_prefs.json ou verse_cache.json.')
        exit 2
    }
} catch { exit 0 }
exit 0
