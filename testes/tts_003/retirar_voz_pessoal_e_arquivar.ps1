$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$rootPrefix = $projectRoot.TrimEnd('\') + '\'
function Assert-WorkspaceTarget([string]$candidate) {
    $resolved = [IO.Path]::GetFullPath($candidate)
    if (-not $resolved.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) { throw "Fora do workspace: $resolved" }
    if (Test-Path -LiteralPath $resolved) {
        $items = @(Get-Item -LiteralPath $resolved -Force)
        if ($items[0].PSIsContainer) { $items += @(Get-ChildItem -LiteralPath $resolved -Force -Recurse) }
        foreach ($item in $items) {
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Link/junction recusado: $($item.FullName)" }
            if (-not $item.FullName.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Destino escapou do workspace' }
        }
    }
    return $resolved
}
$removeRelative = @(
    'audio\referencias_vocais\narrador_br_001',
    'audio\narracoes\TESTES_LOCAIS_002\qwen_base_br_V1.wav',
    'audio\narracoes\TESTES_LOCAIS_002\qwen_base_br_V1.wav.meta.json',
    'models\voice_prompts',
    'testes\tts_002\qwen_base_stdout.log',
    'testes\tts_002\register_stdout.log',
    'testes\tts_002\register_exit.json',
    'testes\tts_002\asr_reference.json',
    'testes\tts_002\asr_reference_stdout.log',
    'testes\tts_002\asr_reference_stderr.log',
    'testes\tts_002\asr_reference_exit.json',
    'testes\tts_002\reference_conversion.json',
    'testes\tts_002\reference_conversion_stdout.log',
    'testes\tts_002\reference_conversion_stderr.log',
    'testes\tts_002\reference_conversion_exit.json'
)
$archiveRelative = @(
    'audio\narracoes\TESTES_LOCAIS_001',
    'audio\narracoes\TESTES_LOCAIS_002',
    'models\5d83992436eae1d760afd27aff78a71d676296fc',
    'models\85e237c12c027371202489a0ec509ded67b5e4b5',
    'models\piper_faber'
)
$archiveRoot = Join-Path $projectRoot 'arquivo\tts_locais_rejeitados\TTS_003'
$deletions = @(); $moves = @()
# Resolve and verify every source/destination before any removal or move.
foreach ($relative in $removeRelative) {
    $absolute = Assert-WorkspaceTarget (Join-Path $projectRoot $relative)
    if (Test-Path -LiteralPath $absolute) {
        $item = Get-Item -LiteralPath $absolute -Force
        $files = if ($item.PSIsContainer) { @(Get-ChildItem -LiteralPath $absolute -Recurse -File -Force) } else { @($item) }
        $deletions += [pscustomobject]@{source=$relative;absolute=$absolute;files=@($files | ForEach-Object { $_.FullName.Substring($rootPrefix.Length) })}
    }
}
foreach ($relative in $archiveRelative) {
    $source = Assert-WorkspaceTarget (Join-Path $projectRoot $relative)
    $destination = Assert-WorkspaceTarget (Join-Path $archiveRoot $relative)
    if (Test-Path -LiteralPath $destination) { throw "Arquivo de destino ja existe: $destination" }
    if (Test-Path -LiteralPath $source) { $moves += [pscustomobject]@{source=$relative;destination=$destination.Substring($rootPrefix.Length);absoluteSource=$source;absoluteDestination=$destination} }
}
$plan = [pscustomobject]@{authorization='User explicitly requested removal of personal voice and separation of rejected local tests in TTS-003';deletions=$deletions;moves=$moves}
$planPath = Join-Path $PSScriptRoot 'retirada_e_arquivo.json'
if (Test-Path -LiteralPath $planPath) { throw 'Plano ja existe; nao repetir automaticamente' }
$plan | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $planPath -Encoding UTF8
foreach ($entry in $deletions) { Remove-Item -LiteralPath $entry.absolute -Force -Recurse }
foreach ($entry in $moves) {
    $parent = Split-Path -Parent $entry.absoluteDestination
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    Move-Item -LiteralPath $entry.absoluteSource -Destination $entry.absoluteDestination
}
Write-Output ('Removed personal-data groups: ' + $deletions.Count + '; archived groups: ' + $moves.Count)
