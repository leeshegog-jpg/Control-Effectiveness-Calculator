/* TP Risk Management SMS — Obsidian Vault Sync
 * Requires the "Obsidian Local REST API" community plugin.
 * Settings stored in localStorage under 'sms_obsidian'.
 */
const ObsidianSync = (() => {
  const KEY = 'sms_obsidian';
  const LL = ['','Rare','Unlikely','Possible','Likely','Almost Certain'];
  const CL = ['','Insignificant','Minor','Moderate','Major','Catastrophic'];

  function get() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch { return {}; }
  }
  function set(s) { localStorage.setItem(KEY, JSON.stringify(s)); }
  function isEnabled() { const s=get(); return !!(s.enabled && s.apiKey && s.baseUrl); }

  function vaultPath(type, id) {
    const s = get();
    const map = {
      risks:     s.folderRisks     || 'SMS/Risks',
      incidents: s.folderIncidents || 'SMS/Incidents',
      cars:      s.folderCARs      || 'SMS/CARs',
      audits:    s.folderAudits    || 'SMS/Audits'
    };
    return `${map[type] || 'SMS'}/${id}.md`;
  }

  function band(score) {
    return score >= 20 ? 'Critical' : score >= 12 ? 'High' : score >= 5 ? 'Medium' : score >= 1 ? 'Low' : '—';
  }

  function buildMarkdown(type, r) {
    if (type === 'risks') {
      const iS = (+r.likelihood||0) * (+r.consequence||0);
      const rS = (+r.resLikelihood||0) * (+r.resConsequence||0);
      return `---
id: ${r.id}
type: risk
status: ${r.status||'Open'}
category: ${r.category||''}
location: ${r.location||''}
owner: ${r.controlOwner||''}
reviewDate: ${r.reviewDate||''}
residualBand: ${band(rS)}
updated: ${r.updated||new Date().toISOString()}
---

# ${r.id} — ${r.hazardDescription||''}

| Field | Value |
|---|---|
| Category | ${r.category||'—'} |
| Location | ${r.location||'—'} |
| Activity | ${r.activity||'—'} |
| Status | ${r.status||'Open'} |
| Owner | ${r.controlOwner||'—'} |
| Review Date | ${r.reviewDate||'—'} |
| Date Identified | ${r.dateIdentified||'—'} |

## Risk Rating

| | Likelihood | Consequence | Score | Band |
|---|---|---|---|---|
| **Inherent** | ${r.likelihood||'—'} – ${LL[+r.likelihood]||''} | ${r.consequence||'—'} – ${CL[+r.consequence]||''} | ${iS||'—'} | ${band(iS)} |
| **Residual** | ${r.resLikelihood||'—'} – ${LL[+r.resLikelihood]||''} | ${r.resConsequence||'—'} – ${CL[+r.resConsequence]||''} | ${rS||'—'} | ${band(rS)} |

## Existing Controls
${r.existingControls||'_None recorded_'}

## Additional Controls
${r.additionalControls||'_None recorded_'}

## Notes
${r.notes||'_None_'}
`;
    }
    if (type === 'incidents') {
      return `---
id: ${r.id}
type: incident
status: ${r.status||'Open'}
incidentType: ${r.incidentType||''}
severity: ${r.severity||''}
location: ${r.location||''}
dateTime: ${r.dateTime||''}
updated: ${r.updated||new Date().toISOString()}
---

# ${r.id} — ${r.description||''}

| Field | Value |
|---|---|
| Type | ${r.incidentType||'—'} |
| Severity | ${r.severity||'—'} |
| Location | ${r.location||'—'} |
| Date/Time | ${r.dateTime||'—'} |
| Reporter | ${r.reporterName||'—'} |
| Status | ${r.status||'Open'} |

## Description
${r.description||'_None_'}

## Injuries / People Affected
${r.injuries||'_None reported_'}

## Immediate Actions
${r.immediateActions||'_None recorded_'}

## Cause Analysis
**Immediate Cause:** ${r.immediateCause||'_Not identified_'}
**Root Cause:** ${r.rootCause||'_Not identified_'}

## Corrective Actions
${r.carRefs||'_None raised_'}

## Notes
${r.notes||'_None_'}
`;
    }
    if (type === 'cars') {
      return `---
id: ${r.id}
type: car
status: ${r.status||'Open'}
priority: ${r.priority||''}
source: ${r.source||''}
assignedTo: ${r.assignedTo||''}
dueDate: ${r.dueDate||''}
updated: ${r.updated||new Date().toISOString()}
---

# ${r.id} — ${r.description||''}

| Field | Value |
|---|---|
| Source | ${r.source||'—'}${r.sourceRef?' ('+r.sourceRef+')':''} |
| Priority | ${r.priority||'—'} |
| Assigned To | ${r.assignedTo||'—'} |
| Due Date | ${r.dueDate||'—'} |
| Status | ${r.status||'Open'} |
| Root Cause Category | ${r.rootCauseCategory||'—'} |

## Description
${r.description||'_None_'}

## Completion
**Date:** ${r.completionDate||'_Not closed_'}
**Effectiveness:** ${r.effectiveness||'_Not reviewed_'}

## Notes
${r.notes||'_None_'}
`;
    }
    if (type === 'audits') {
      return `---
id: ${r.id}
type: audit
status: ${r.status||'Planned'}
auditType: ${r.auditType||''}
auditor: ${r.auditor||''}
plannedDate: ${r.plannedDate||''}
area: ${r.area||''}
updated: ${r.updated||new Date().toISOString()}
---

# ${r.id} — ${r.title||''}

| Field | Value |
|---|---|
| Audit Type | ${r.auditType||'—'} |
| Planned Date | ${r.plannedDate||'—'} |
| Actual Date | ${r.actualDate||'—'} |
| Auditor | ${r.auditor||'—'} |
| Area | ${r.area||'—'} |
| Status | ${r.status||'Planned'} |

## Scope
${r.scope||'_Not defined_'}

## Findings Summary
${r.findingsSummary||'_None recorded_'}

### Finding Counts
- Total: ${r.findingsTotal||0} · High: ${r.findingsHigh||0} · Medium: ${r.findingsMedium||0} · Low: ${r.findingsLow||0}

## Recommendations
${r.recommendations||'_None_'}

## Corrective Actions
${r.carRefs||'_None raised_'}

## Notes
${r.notes||'_None_'}
`;
    }
    return `---\nid: ${r.id}\ntype: ${type}\n---\n`;
  }

  async function push(type, record) {
    if (!isEnabled()) return { ok: false, reason: 'disabled' };
    const s = get();
    try {
      const res = await fetch(`${s.baseUrl}/vault/${vaultPath(type, record.id)}`, {
        method: 'PUT',
        headers: { 'Authorization': 'Bearer ' + s.apiKey, 'Content-Type': 'text/markdown' },
        body: buildMarkdown(type, record)
      });
      return { ok: res.ok, status: res.status };
    } catch(e) { return { ok: false, reason: e.message }; }
  }

  async function remove(type, record) {
    if (!isEnabled()) return;
    const s = get();
    try {
      await fetch(`${s.baseUrl}/vault/${vaultPath(type, record.id)}`, {
        method: 'DELETE',
        headers: { 'Authorization': 'Bearer ' + s.apiKey }
      });
    } catch(e) {}
  }

  function toast(msg, ok) {
    const t = document.createElement('div');
    t.style.cssText = `position:fixed;bottom:24px;right:24px;background:${ok?'#16A34A':'#D97706'};color:#fff;padding:10px 18px;border-radius:8px;font-size:13px;font-weight:600;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,.2);transition:opacity .4s`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; setTimeout(() => t.remove(), 400); }, 2500);
  }

  async function pushAndToast(type, record) {
    if (!isEnabled()) return;
    const r = await push(type, record);
    toast(r.ok ? '✓ Synced to Obsidian' : '⚠ Obsidian sync failed', r.ok);
  }

  async function testConnection() {
    const s = get();
    if (!s.baseUrl || !s.apiKey) return { ok: false, reason: 'Missing URL or API key' };
    try {
      const res = await fetch(`${s.baseUrl}/`, { headers: { 'Authorization': 'Bearer ' + s.apiKey } });
      return { ok: res.ok, status: res.status };
    } catch(e) { return { ok: false, reason: e.message }; }
  }

  return { get, set, isEnabled, push, remove, pushAndToast, toast, testConnection };
})();
