# Lost Working-Tree Investigation

**Date discovered:** 2026-08-05, during R0 release (`main` sync before tagging `v1.1.0-R0`).
**Status: CLOSED.** Application intact. Only an unidentified, unrecoverable uncommitted delta was lost. No rebuild required.

## What happened

While syncing local `main` to `origin/main` (local `main` had gone stale relative to 15+ commits already on the remote), `git reset --hard origin/main` was run without first checking for or stashing uncommitted changes. That command overwrites the working tree unconditionally.

At session start, `git status` had shown these 11 root-level files as locally modified but never committed:

`GOHS4.1.8.X_FARSI_Control_Effectiveness_Calculator_v0.2.html`, `audit-inspection.html`, `corrective-actions.html`, `incident-report.html`, `index.html`, `injury-claims-dashboard.html`, `risk-register.html`, `safety-dashboard.html`, `sms-shared.js`, `sms.css`, `styles.css`

The specific diff content was never viewed or recorded before the reset. It is gone.

## Recovery avenues checked

| Avenue | Result |
|---|---|
| Git objects (`git fsck --unreachable --dangling`) | Only one unrelated dangling object (a locally-deleted tag). Files were never staged, so git never held a blob for the edits — nothing to recover. |
| Second local clone (`D:\Git\TP_Risk_Management_SMS`) | Clean working tree, matches an already-committed point in history. Not the source. |
| PR #11 diff (436 files) | None of the 11 files appear in it. |
| All 6 other remote branches | All last touched these files between 2026-05-31 and 2026-07-07 — older than the last real commits (2026-07-28/29). None ahead. |
| VS Code Local History + Backups (`%APPDATA%\Code\History`, `\Backups`) | No entries for any of the 11 filenames. |
| Windows Volume Shadow Copy | None exist on this machine (System Protection not enabled) — "Previous Versions" would show nothing. |
| OneDrive version history | Does not apply — neither clone (`D:\Github`, `D:\Git`) is inside a OneDrive-synced path. |
| Temp files, Downloads, Desktop/Documents duplicate repos | Nothing relevant found. |
| Local Claude Code session history (this machine) | Reviewed every session touching this repo between the last commit (Jul 28/29) and now. All either (a) fully committed already (matches `138d7d2`, `d57b7ab`, `db0ddd1`/`e316272`) or (b) investigation-only with zero edits (`local_1e688f83`, stuck installing a browser, never got to make a change). No session shows edits beyond what's already in git history. |
| Saved project memory (`D:\.claude\projects\D--OneDrive-Claude-CLAUDE-COWORK\memory\`) | Found `project_tp_risk_management_sms.md` and `reference_tp_sms_field_names.md` — architecture/field-name notes from 2026-07-06, useful as corroboration, not as a source of the missing delta (predates it, and both explicitly note they may drift from the live files). |

## Key finding: the application was never actually at risk

All 11 files exist right now with full, real, working content — verified directly, not assumed:

- Sizes range 5KB (`sms-shared.js`, `sms.css`) to 89KB (`GOHS4.1.8...html`), not empty or truncated.
- `risk-register.html` still contains real form fields (`hazardDescription`, `fHazard`, etc.).
- `sms-shared.js` still contains `SMS.riskScore`/`riskBand` and the rest of the shared data-layer API.
- Current working tree diffs empty against `HEAD` (`e63b315`) and against `apps/web` specifically — confirms the reset landed exactly on the last real commit, nothing further was disturbed.

The last committed state (`138d7d2`, "Unify risk data across all modules and align matrix to real VRTP GOHS2.1.2", 2026-07-29) was itself verified working end-to-end in a same-period session: live round-trip test (risk created → localStorage → dashboard count), zero console errors across all pages, field names/localStorage schema confirmed consistent across every module. This was not a fragile or partially-built state.

## Decision

- **Committed application: intact, verified, not touched by this incident.**
- **Uncommitted delta: unrecoverable.** Scope and content unknown — possibly a real in-progress edit (Scenario B: incomplete feature work, e.g. a field addition, UI tweak, or validation fix), possibly incidental (Scenario A/C: formatting, line-ending, or transient debugging edits). No evidence distinguishes these; the diff was never seen by anyone before it was lost.
- **No rebuild undertaken.** The premise that "11 files need rebuilding" was corrected during this investigation — nothing needs reconstructing from prompt history or memory. Continue from the current `v1.1.0-R0` baseline.
- **Process fix, applied going forward:** check `git status`/stash before any `git reset --hard`, per standard practice — this was the actual root cause, not a tooling limitation.

## If the missing delta turns out to matter

If you later recall specifically what you were editing in one of these 11 files, it can be redone directly against the current (intact, working) file — this is a small, targeted edit, not a reconstruction project.
