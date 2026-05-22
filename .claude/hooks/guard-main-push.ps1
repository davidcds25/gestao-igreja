$ErrorActionPreference = 'SilentlyContinue'
try {
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }

    $data = $raw | ConvertFrom-Json
    $cmd  = $data.tool_input.command
    if ([string]::IsNullOrWhiteSpace($cmd)) { exit 0 }
    if ($cmd -notmatch 'git\s+push') { exit 0 }

    if ($cmd -match 'origin\s+main' -and $cmd -notmatch '--tags') {
        [Console]::Error.WriteLine('BLOQUEADO: push direto para main nao permitido.')
        [Console]::Error.WriteLine('Use o agent release -> merge na main -> git push origin main --tags')
        exit 2
    }
} catch { exit 0 }
exit 0
