$ErrorActionPreference = 'SilentlyContinue'
try {
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }

    $data = $raw | ConvertFrom-Json
    $path = $data.tool_input.file_path
    if ([string]::IsNullOrWhiteSpace($path)) { exit 0 }

    if ($path -match '\\core\\' -and $path -match '\.py$') {
        $filename = [System.IO.Path]::GetFileName($path)
        Write-Output "[qa-reminder] '$filename' modificado em core/. Rodar o agent qa antes do commit."
    }
} catch { exit 0 }
exit 0
