/* TP Risk Management SMS — Shared Data Layer v1.1 */
const SMS = (() => {
  const KEYS   = { risks:'sms_risks', incidents:'sms_incidents', cars:'sms_cars', audits:'sms_audits' };
  const PREFIX = { risks:'R', incidents:'I', cars:'C', audits:'A' };

  function get(key) {
    try { return JSON.parse(localStorage.getItem(KEYS[key]) || '[]'); } catch { return []; }
  }
  function save(key, data) { localStorage.setItem(KEYS[key], JSON.stringify(data)); }
  function nextId(key) {
    const nums = get(key).map(r => parseInt((r.id||'').replace(/\D/g,''))||0);
    return `${PREFIX[key]}${String((nums.length ? Math.max(...nums) : 0) + 1).padStart(4,'0')}`;
  }
  function add(key, rec) {
    const data = get(key);
    rec.id = rec.id || nextId(key);
    if (data.some(r => r.id === rec.id)) return data.find(r => r.id === rec.id); // dedup: skip if ID exists
    rec.created = rec.created || new Date().toISOString();
    rec.updated = new Date().toISOString();
    data.push(rec); save(key, data); return rec;
  }
  function update(key, id, patch) {
    const data = get(key);
    const i = data.findIndex(r => r.id === id);
    if (i < 0) return null;
    data[i] = { ...data[i], ...patch, updated: new Date().toISOString() };
    save(key, data); return data[i];
  }
  function remove(key, id) { save(key, get(key).filter(r => r.id !== id)); }

  function riskScore(l, c) { return (+l||0) * (+c||0); }
  function riskBand(score) {
    if (score >= 20) return { label:'Critical', cls:'band-critical' };
    if (score >= 12) return { label:'High',     cls:'band-high' };
    if (score >= 5)  return { label:'Medium',   cls:'band-medium' };
    if (score >= 1)  return { label:'Low',      cls:'band-low' };
    return                  { label:'—',        cls:'' };
  }
  const L_LABELS = ['','Rare','Unlikely','Possible','Likely','Almost Certain'];
  const C_LABELS = ['','Insignificant','Minor','Moderate','Major','Catastrophic'];

  function fmtDate(iso) {
    if (!iso) return '—';
    const d = new Date(iso); return isNaN(d) ? iso : d.toLocaleDateString('en-AU',{day:'2-digit',month:'short',year:'numeric'});
  }
  function isOverdue(dateStr, status) {
    if (!dateStr || status==='Closed'||status==='Complete'||status==='Cancelled') return false;
    return new Date(dateStr) < new Date(new Date().toDateString());
  }
  function today() { return new Date().toISOString().split('T')[0]; }

  function exportXlsx(rows, filename, sheet) {
    const ws = XLSX.utils.json_to_sheet(rows);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, sheet||'Data');
    XLSX.writeFile(wb, filename);
  }
  function importXlsx(file, cb) {
    const r = new FileReader();
    r.onload = e => { const wb = XLSX.read(e.target.result,{type:'array'}); cb(XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]],{defval:''})); };
    r.readAsArrayBuffer(file);
  }

  function exportAll() {
    const snap = {};
    Object.keys(KEYS).forEach(k => snap[k] = get(k));
    snap._exported = new Date().toISOString();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([JSON.stringify(snap,null,2)],{type:'application/json'}));
    a.download = 'sms-backup-'+new Date().toISOString().split('T')[0]+'.json';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
  }
  function importAll(file, cb) {
    const r = new FileReader();
    r.onload = e => {
      try {
        const snap = JSON.parse(e.target.result);
        let count = 0;
        Object.keys(KEYS).forEach(k => { if(Array.isArray(snap[k])) { save(k, snap[k]); count += snap[k].length; } });
        if(cb) cb(null, count);
      } catch(err) { if(cb) cb(err); }
    };
    r.readAsText(file);
  }

  function stats() {
    const risks=get('risks'), incidents=get('incidents'), cars=get('cars'), audits=get('audits');
    const now = new Date(new Date().toDateString());
    const band = r => riskBand(riskScore(r.resLikelihood||r.likelihood, r.resConsequence||r.consequence)).label;
    return {
      riskTotal:risks.length, riskOpen:risks.filter(r=>r.status!=='Closed').length,
      riskCritical:risks.filter(r=>band(r)==='Critical').length, riskHigh:risks.filter(r=>band(r)==='High').length,
      riskReviewsDue:risks.filter(r=>r.status!=='Closed'&&r.reviewDate&&new Date(r.reviewDate)<now).length,
      incidentTotal:incidents.length, incidentOpen:incidents.filter(i=>i.status!=='Closed').length,
      incidentThisMth:incidents.filter(i=>{const d=new Date(i.dateTime||i.created);return d.getMonth()===now.getMonth()&&d.getFullYear()===now.getFullYear();}).length,
      carTotal:cars.length, carOpen:cars.filter(c=>c.status!=='Closed').length,
      carOverdue:cars.filter(c=>isOverdue(c.dueDate,c.status)).length,
      auditTotal:audits.length,
      auditUpcoming:audits.filter(a=>a.plannedDate&&a.status!=='Complete'&&a.status!=='Cancelled'&&new Date(a.plannedDate)>=now).length,
      auditOverdue:audits.filter(a=>isOverdue(a.plannedDate,a.status)).length,
    };
  }

  return { get, save, add, update, remove, nextId, riskScore, riskBand, L_LABELS, C_LABELS,
           fmtDate, isOverdue, today, exportXlsx, importXlsx, exportAll, importAll, stats };
})();
