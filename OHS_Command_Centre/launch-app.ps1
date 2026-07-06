# VRTP OHS Command Centre — desktop app launcher
# Starts a local static server (if not already running) rooted at the repo folder,
# then opens the launcher in an isolated Edge/Chrome app window (no tabs/address bar).
# When the app window closes, the server this script started is shut down.
# Root is derived from this script's own location so the folder can be cloned anywhere.

$ErrorActionPreference = 'SilentlyContinue'

# Script lives in <repo>\OHS_Command_Centre\ ; serve the repo root (its parent).
$Root = Split-Path -Parent $PSScriptRoot
$Port = 3939
$Url  = "http://localhost:$Port/OHS_Command_Centre/index.html"
$UserDataDir = Join-Path $env:LOCALAPPDATA 'OHSCommandCentre\browser'

# ── Locate python ──
$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { $python = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $python) {
  [System.Windows.Forms.MessageBox]::Show('Python not found on PATH. Cannot start local server.','OHS Command Centre') | Out-Null
  exit 1
}

# ── Start server only if the port is not already serving ──
$serverProc = $null
$listening = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if (-not $listening) {
  # Quote the directory — it contains a space ("CLAUDE COWORK"); an unquoted
  # array element would be split and python would reject the stray argument.
  $serverArgs = '-m http.server {0} --directory "{1}"' -f $Port, $Root
  $serverProc = Start-Process -FilePath $python `
    -ArgumentList $serverArgs `
    -WindowStyle Hidden -PassThru
  # wait up to 10s for the port to come up
  for ($i=0; $i -lt 50; $i++) {
    Start-Sleep -Milliseconds 200
    if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) { break }
  }
}

# ── Locate a Chromium browser (Edge preferred, Chrome fallback) ──
$browsers = @(
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
)
$browser = $browsers | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($browser) {
  $args = @(
    "--app=$Url",
    "--user-data-dir=$UserDataDir",
    "--window-size=1400,900",
    "--no-first-run",
    "--no-default-browser-check"
  )
  $app = Start-Process -FilePath $browser -ArgumentList $args -PassThru
  # Block until the isolated app window is closed
  if ($app) { Wait-Process -Id $app.Id -ErrorAction SilentlyContinue }
} else {
  # No Chromium browser — fall back to default handler (opens in normal browser)
  Start-Process $Url
}

# ── Clean up the server we started ──
if ($serverProc -and -not $serverProc.HasExited) {
  Stop-Process -Id $serverProc.Id -Force -ErrorAction SilentlyContinue
}
