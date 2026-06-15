# sync_config.ps1
# Synchronisiert Konfigurationsdateien aus dem GitHub-Repo nach OneDrive.
# Wird automatisch vom post-commit Hook aufgerufen, wenn senders.json,
# profile.json oder SKILL.md committet wurden.
# Kann auch manuell aufgerufen werden: pwsh -File sync_config.ps1

$repo     = $PSScriptRoot
$onedrive = "C:\Users\joerg\OneDrive - die-weboptimierer\Dokumente\Claude\Scheduled\job-briefing-bewe"

if (-not (Test-Path $onedrive)) {
    Write-Host "WARN: OneDrive-Pfad nicht gefunden: $onedrive" -ForegroundColor Yellow
    exit 1
}

$files = @("senders.json", "profile.json", "SKILL.md")
$synced = 0

foreach ($f in $files) {
    $src = Join-Path $repo $f
    $dst = Join-Path $onedrive $f
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
        Write-Host "  OK  $f -> OneDrive" -ForegroundColor Green
        $synced++
    } else {
        Write-Host "  SKIP $f (nicht im Repo)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Sync abgeschlossen: $synced Datei(en) nach OneDrive kopiert." -ForegroundColor Cyan

# SKILL.md geaendert? Scheduled Task muss manuell aktualisiert werden.
$changed = & git diff HEAD~1 HEAD --name-only 2>$null
if ($changed -match "SKILL\.md") {
    Write-Host ""
    Write-Host "HINWEIS: SKILL.md hat sich geaendert!" -ForegroundColor Yellow
    Write-Host "Bitte den Scheduled Task aktualisieren:" -ForegroundColor Yellow
    Write-Host '  Claude fragen: "Bitte Scheduled Task job-briefing-bewe mit der SKILL.md aus dem Repo aktualisieren"' -ForegroundColor White
}
