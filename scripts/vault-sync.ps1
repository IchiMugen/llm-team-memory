# vault-sync.ps1
# Background daemon: commits+pushes local changes, pulls from remote.
# No Python required — runs on any Windows machine.
# Started by setup-autosync.bat (once per device).

$VAULT = (Get-Item $PSScriptRoot).Parent.FullName
$LOG   = "$VAULT\scripts\vault-sync.log"
$PULL_INTERVAL  = 120  # seconds between pulls
$DEBOUNCE       = 5    # seconds after last change before committing
$CHECK_INTERVAL = 2    # seconds between status checks

function Log($msg) {
    $ts   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] $msg"
    Add-Content -Path $LOG -Value $line -Encoding UTF8
    # Trim log to 400 lines when over 500
    $lines = Get-Content $LOG -Encoding UTF8
    if ($lines.Count -gt 500) {
        $lines | Select-Object -Last 400 | Set-Content $LOG -Encoding UTF8
    }
}

function Git($cmd) {
    $r = & git -C $VAULT $cmd.Split(" ") 2>&1
    return @{ Out = ($r | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] }) -join "`n"
              Err = ($r | Where-Object { $_ -is  [System.Management.Automation.ErrorRecord] }) -join "`n"
              Code = $LASTEXITCODE }
}

function HasChanges {
    $r = & git -C $VAULT status --porcelain 2>$null
    return ($r -ne $null -and "$r".Trim() -ne "")
}

function Pull {
    $r = & git -C $VAULT pull --rebase --autostash 2>&1
    $out = "$r"
    if ($LASTEXITCODE -ne 0) { Log "PULL ERROR: $out" }
    elseif ($out -notmatch "Already up to date" -and $out.Trim() -ne "") {
        Log "Pulled: $($out.Substring(0, [Math]::Min(120,$out.Length)))"
    }
}

function Push {
    & git -C $VAULT add -A 2>$null
    $ts  = Get-Date -Format "HH:mm"
    $r   = & git -C $VAULT commit -m "vault: auto-sync $ts" 2>&1
    $out = "$r"
    if ($out -match "nothing to commit" -or $LASTEXITCODE -ne 0) { return }
    Log "Committed: $($out.Substring(0, [Math]::Min(80,$out.Length)))"

    foreach ($remote in @("github","origin")) {
        & git -C $VAULT push $remote main 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { Log "Pushed to $remote" }
    }
}

Log "vault-sync started — watching $VAULT"

# Commit any pending changes immediately on startup (no debounce)
if (HasChanges) { Push }

$lastPull    = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$pendingSince = $null

while ($true) {
    try {
        $now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()

        if ($now - $lastPull -ge $PULL_INTERVAL) {
            Pull
            $lastPull = $now
        }

        if (HasChanges) {
            if ($null -eq $pendingSince) { $pendingSince = $now }
        } else {
            $pendingSince = $null
        }

        if ($null -ne $pendingSince -and ($now - $pendingSince) -ge $DEBOUNCE) {
            Push
            $pendingSince = $null
        }
    } catch {
        Log "ERROR: $_"
    }

    Start-Sleep -Seconds $CHECK_INTERVAL
}
