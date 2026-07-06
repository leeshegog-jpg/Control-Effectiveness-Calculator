# OHS Command Centre

A single tabbed launcher that unifies the VRTP OHS tools in one window:

| Tab | Loads |
|-----|-------|
| SMS Hub | `../index.html` — the TP Risk Management SMS suite (repo root) |
| Hazard Register | `hazard_register.html` (React) |
| Incident Report | `incident_report.html` |
| Safety Dashboard | `safety_dashboard.html` |
| Import Reference | `ohs_import_reference.html` |

Each tool loads in its own iframe (lazily, on first tab click), so the different
stacks never collide. The SMS Hub tab embeds the live suite at the repo root — no
duplication.

## Run it

**Static / GitHub Pages:** serve the repo root and open `/OHS_Command_Centre/index.html`.
The `../index.html` reference resolves to the suite at the root.

**Desktop app (Windows):** run `launch-app.ps1`. It starts a hidden local
`python -m http.server` rooted at the repo folder (only if the port is free),
opens the launcher in an isolated Edge/Chrome `--app` window (no tabs/address bar),
and shuts the server down when the window closes. Server root is derived from the
script's own location, so the folder works cloned anywhere.

Requires Python and Edge or Chrome on PATH. The Hazard Register needs internet
(React + related libs load from CDN).
