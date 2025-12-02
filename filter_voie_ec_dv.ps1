param(
    [string]$InputFile = "levéRaildemo.txt",
    [string]$OutputDir = "."
)

$lines = Get-Content -LiteralPath $InputFile -ErrorAction Stop | Where-Object { $_ -and $_.Trim() -ne "" }

$voie01 = @()
$voie02 = @()
$voie01_ec = @()
$voie02_dv = @()

foreach ($line in $lines) {
    $tokens = $line -split "\s+"
    if ($tokens.Count -lt 1) { continue }
    $id = $tokens[0]
    $last = $tokens[$tokens.Count - 1]
    $code = if ($last -in @('EC','DV')) { $last } else { $null }

    if ($id -match '^VO0*1_') {
        $voie01 += $line
        if ($code -eq 'EC') { $voie01_ec += $line }
    } elseif ($id -match '^VO0*2_') {
        $voie02 += $line
        if ($code -eq 'DV') { $voie02_dv += $line }
    }
}

Set-Content -LiteralPath (Join-Path $OutputDir 'voie01.txt') -Value $voie01 -NoNewline:$false
Set-Content -LiteralPath (Join-Path $OutputDir 'voie02.txt') -Value $voie02 -NoNewline:$false
Set-Content -LiteralPath (Join-Path $OutputDir 'voie01_ec.txt') -Value $voie01_ec -NoNewline:$false
Set-Content -LiteralPath (Join-Path $OutputDir 'voie02_dv.txt') -Value $voie02_dv -NoNewline:$false

Write-Output "Fichiers générés dans $OutputDir : voie01.txt, voie02.txt, voie01_ec.txt, voie02_dv.txt"
