/* URL Parser — app.js
 * Reads an Excel/CSV file via SheetJS, finds URL columns, parses each URL
 * with the native URL API, then renders a sortable/filterable table.
 */

'use strict';

// ── State ────────────────────────────────────────────────────────────────────
const state = {
  workbook:     null,
  rawRows:      [],   // all parsed row objects from the sheet
  parsed:       [],   // fully decomposed URL objects
  filtered:     [],   // after search + scheme filter
  sortCol:      null,
  sortDir:      'asc',
  page:         1,
  pageSize:     50,
};

// ── DOM refs ─────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const dropZone      = $('dropZone');
const fileInput     = $('fileInput');
const sheetSelect   = $('sheetSelect');
const urlColInput   = $('urlColInput');
const firstRowHdr   = $('firstRowHeader');
const parseBtn      = $('parseBtn');
const statsBar      = $('statsBar');
const toolbar       = $('toolbar');
const tableCard     = $('tableCard');
const tbody         = $('resultsBody');
const filterInput   = $('filterInput');
const schemeFilter  = $('schemeFilter');
const rowCount      = $('rowCount');
const pagination    = $('pagination');
const detailOverlay = $('detailOverlay');
const detailUrl     = $('detailUrl');
const detailTable   = $('detailTable');
const detailParams  = $('detailParams');
const copyBtn       = $('copyBtn');
const exportBtn     = $('exportBtn');
const exportXlsxBtn = $('exportXlsxBtn');
const resetBtn      = $('resetBtn');

// ── File loading ─────────────────────────────────────────────────────────────
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  handleFile(e.dataTransfer.files[0]);
});
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => handleFile(fileInput.files[0]));

function handleFile(file) {
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    const data = new Uint8Array(e.target.result);
    state.workbook = XLSX.read(data, { type: 'array' });
    populateSheetSelect();
    parseBtn.disabled = false;
  };
  reader.readAsArrayBuffer(file);
}

function populateSheetSelect() {
  sheetSelect.innerHTML = '';
  sheetSelect.disabled = false;
  state.workbook.SheetNames.forEach(name => {
    const opt = document.createElement('option');
    opt.value = opt.textContent = name;
    sheetSelect.appendChild(opt);
  });
}

// ── Parsing pipeline ─────────────────────────────────────────────────────────
parseBtn.addEventListener('click', runParse);

function runParse() {
  const sheetName = sheetSelect.value;
  const sheet = state.workbook.Sheets[sheetName];
  const hasHeader = firstRowHdr.checked;

  // Convert sheet → array of arrays
  const aoa = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });
  if (!aoa.length) return;

  const headers = hasHeader ? aoa[0].map(h => String(h).trim()) : null;
  const dataRows = hasHeader ? aoa.slice(1) : aoa;

  // Convert to objects
  state.rawRows = dataRows.map(row => {
    if (headers) {
      const obj = {};
      headers.forEach((h, i) => { obj[h] = row[i] !== undefined ? String(row[i]) : ''; });
      return obj;
    }
    return row.map(c => String(c));
  });

  // Find URL column
  const urlColHint = urlColInput.value.trim();
  const urlKey = detectUrlColumn(state.rawRows, headers, urlColHint);

  // Parse each URL
  state.parsed = state.rawRows.map((row, idx) => {
    const rawUrl = headers ? (row[urlKey] || '') : (row[urlKey] || '');
    return { rowIdx: idx + (hasHeader ? 2 : 1), raw: rawUrl.trim(), ...decomposeUrl(rawUrl.trim()) };
  });

  buildUI();
}

function detectUrlColumn(rows, headers, hint) {
  if (hint && headers && headers.includes(hint)) return hint;
  if (hint && headers) {
    const ci = headers.findIndex(h => h.toLowerCase() === hint.toLowerCase());
    if (ci !== -1) return headers[ci];
  }
  if (headers) {
    // Prefer column whose header contains 'url'
    const urlHeader = headers.find(h => /url/i.test(h));
    if (urlHeader) return urlHeader;
    // Fallback: first column with the most URL-looking values
    const scores = headers.map((h, col) => {
      return rows.reduce((n, row) => n + (looksLikeUrl(row[h]) ? 1 : 0), 0);
    });
    return headers[scores.indexOf(Math.max(...scores))];
  }
  // No headers — find column index with most URL-looking values
  const colCount = rows[0] ? rows[0].length : 0;
  const scores = Array.from({ length: colCount }, (_, col) =>
    rows.reduce((n, row) => n + (looksLikeUrl(row[col]) ? 1 : 0), 0)
  );
  return scores.indexOf(Math.max(...scores));
}

function looksLikeUrl(val) {
  if (!val) return false;
  return /^(https?|ftp|file|mailto|data|ssh|tel):/i.test(String(val).trim()) ||
         /^www\./i.test(String(val).trim());
}

// ── URL decomposition ─────────────────────────────────────────────────────────
function decomposeUrl(raw) {
  if (!raw) return { valid: false, scheme: '', username: '', password: '', hostname: '', port: '', pathname: '', search: '', params: {}, hash: '' };

  // Try with mailto / tel as-is
  let urlStr = raw;
  if (!/^[a-zA-Z][a-zA-Z\d+\-.]*:/.test(raw)) {
    // Prepend https:// if no scheme
    urlStr = 'https://' + raw;
  }

  try {
    const u = new URL(urlStr);
    const params = {};
    u.searchParams.forEach((v, k) => {
      if (params[k] !== undefined) {
        params[k] = Array.isArray(params[k]) ? [...params[k], v] : [params[k], v];
      } else {
        params[k] = v;
      }
    });
    return {
      valid:    true,
      scheme:   u.protocol.replace(':', ''),
      username: u.username,
      password: u.password,
      hostname: u.hostname,
      port:     u.port,
      pathname: u.pathname,
      search:   u.search,
      params,
      hash:     u.hash,
    };
  } catch {
    return { valid: false, scheme: '', username: '', password: '', hostname: '', port: '', pathname: '', search: '', params: {}, hash: '' };
  }
}

// ── Build UI after parse ──────────────────────────────────────────────────────
function buildUI() {
  // Stats
  const valid   = state.parsed.filter(r => r.valid).length;
  const invalid = state.parsed.length - valid;
  const schemes = [...new Set(state.parsed.filter(r => r.valid).map(r => r.scheme))];
  const hosts   = [...new Set(state.parsed.filter(r => r.valid).map(r => r.hostname))];

  $('statTotal').textContent   = state.parsed.length;
  $('statValid').textContent   = valid;
  $('statInvalid').textContent = invalid;
  $('statSchemes').textContent = schemes.length;
  $('statHosts').textContent   = hosts.length;

  // Scheme filter options
  schemeFilter.innerHTML = '<option value="">All schemes</option>';
  schemes.sort().forEach(s => {
    const o = document.createElement('option');
    o.value = o.textContent = s;
    schemeFilter.appendChild(o);
  });

  statsBar.classList.remove('hidden');
  toolbar.classList.remove('hidden');
  tableCard.classList.remove('hidden');

  applyFilter();
}

// ── Filter + sort + paginate ─────────────────────────────────────────────────
filterInput.addEventListener('input',   applyFilter);
schemeFilter.addEventListener('change', applyFilter);

function applyFilter() {
  const q  = filterInput.value.toLowerCase();
  const sc = schemeFilter.value;

  state.filtered = state.parsed.filter(r => {
    const matchScheme = !sc || r.scheme === sc;
    const matchText   = !q || JSON.stringify(r).toLowerCase().includes(q);
    return matchScheme && matchText;
  });

  state.page = 1;
  renderTable();
}

// Sorting
document.querySelectorAll('th.sortable').forEach(th => {
  th.addEventListener('click', () => {
    const col = th.dataset.col;
    if (state.sortCol === col) {
      state.sortDir = state.sortDir === 'asc' ? 'desc' : 'asc';
    } else {
      state.sortCol = col;
      state.sortDir = 'asc';
    }
    document.querySelectorAll('th.sortable').forEach(t => t.classList.remove('sort-asc', 'sort-desc'));
    th.classList.add(state.sortDir === 'asc' ? 'sort-asc' : 'sort-desc');
    renderTable();
  });
});

function sortedData() {
  if (!state.sortCol) return state.filtered;
  return [...state.filtered].sort((a, b) => {
    const av = String(a[state.sortCol] ?? '');
    const bv = String(b[state.sortCol] ?? '');
    return state.sortDir === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av);
  });
}

// ── Table rendering ────────────────────────────────────────────────────────────
function renderTable() {
  const data  = sortedData();
  const total = data.length;
  const pages = Math.ceil(total / state.pageSize) || 1;
  state.page  = Math.min(state.page, pages);
  const start = (state.page - 1) * state.pageSize;
  const slice = data.slice(start, start + state.pageSize);

  tbody.innerHTML = '';
  slice.forEach((r, i) => {
    const tr = document.createElement('tr');
    if ((start + i) % 2 === 1) tr.classList.add('alt');

    const paramStr = Object.entries(r.params)
      .map(([k, v]) => `<span class="param-item"><span class="param-key">${esc(k)}</span>=${esc(Array.isArray(v) ? v.join(',') : v)}</span>`)
      .join('');

    tr.innerHTML = `
      <td>${r.rowIdx}</td>
      <td class="wrap" title="${esc(r.raw)}">${esc(r.raw)}</td>
      <td>${r.scheme ? `<span class="badge badge-scheme">${esc(r.scheme)}</span>` : ''}</td>
      <td>${esc(r.username)}</td>
      <td>${r.password ? '••••' : ''}</td>
      <td>${esc(r.hostname)}</td>
      <td>${esc(r.port)}</td>
      <td class="wrap">${esc(r.pathname)}</td>
      <td class="wrap">${esc(r.search)}</td>
      <td><div class="param-list">${paramStr}</div></td>
      <td>${esc(r.hash)}</td>
      <td><span class="badge ${r.valid ? 'badge-valid' : 'badge-invalid'}">${r.valid ? 'Yes' : 'No'}</span></td>
    `;

    tr.addEventListener('click', () => showDetail(r));
    tbody.appendChild(tr);
  });

  rowCount.textContent = `${total} row${total !== 1 ? 's' : ''}`;
  renderPagination(pages);
}

function renderPagination(pages) {
  pagination.innerHTML = '';
  if (pages <= 1) return;

  const addBtn = (label, page, disabled, active) => {
    const b = document.createElement('button');
    b.className = 'page-btn' + (active ? ' active' : '');
    b.textContent = label;
    b.disabled = disabled;
    b.addEventListener('click', () => { state.page = page; renderTable(); });
    pagination.appendChild(b);
  };

  addBtn('‹', state.page - 1, state.page === 1, false);
  const window = 2;
  for (let p = 1; p <= pages; p++) {
    if (p === 1 || p === pages || (p >= state.page - window && p <= state.page + window)) {
      addBtn(p, p, false, p === state.page);
    } else if (p === state.page - window - 1 || p === state.page + window + 1) {
      const dots = document.createElement('span');
      dots.textContent = '…';
      dots.style.padding = '4px 6px';
      pagination.appendChild(dots);
    }
  }
  addBtn('›', state.page + 1, state.page === pages, false);
}

// ── Detail panel ──────────────────────────────────────────────────────────────
function showDetail(r) {
  detailUrl.textContent = r.raw || '(empty)';

  const fields = [
    ['Scheme',   r.scheme],
    ['Username', r.username],
    ['Password', r.password ? '(hidden)' : ''],
    ['Hostname', r.hostname],
    ['Port',     r.port],
    ['Path',     r.pathname],
    ['Query',    r.search],
    ['Fragment', r.hash],
    ['Valid',    r.valid ? 'Yes' : 'No'],
  ];

  detailTable.innerHTML = fields.map(([k, v]) =>
    `<tr><th>${esc(k)}</th><td>${esc(v)}</td></tr>`
  ).join('');

  const entries = Object.entries(r.params);
  if (entries.length) {
    detailParams.innerHTML = `<h3>Query Parameters</h3>
      <table>
        <thead><tr><th>Key</th><th>Value</th></tr></thead>
        <tbody>${entries.map(([k, v]) =>
          `<tr><td>${esc(k)}</td><td>${esc(Array.isArray(v) ? v.join(', ') : v)}</td></tr>`
        ).join('')}</tbody>
      </table>`;
  } else {
    detailParams.innerHTML = '';
  }

  detailOverlay.classList.remove('hidden');
}

$('detailClose').addEventListener('click', () => detailOverlay.classList.add('hidden'));
detailOverlay.addEventListener('click', e => { if (e.target === detailOverlay) detailOverlay.classList.add('hidden'); });

// ── Export ─────────────────────────────────────────────────────────────────────
copyBtn.addEventListener('click', () => {
  const rows  = sortedData();
  const lines = [
    ['Row','URL','Scheme','Username','Password','Hostname','Port','Path','Query','Fragment','Valid'].join('\t'),
    ...rows.map(r => [
      r.rowIdx, r.raw, r.scheme, r.username,
      r.password ? '(hidden)' : '', r.hostname,
      r.port, r.pathname, r.search, r.hash, r.valid ? 'Yes' : 'No'
    ].join('\t'))
  ].join('\n');
  navigator.clipboard.writeText(lines).then(() => flash(copyBtn, 'Copied!'));
});

exportBtn.addEventListener('click', () => {
  const rows = sortedData();
  const csv  = [
    ['Row','URL','Scheme','Username','Hostname','Port','Path','Query','Fragment','Valid'],
    ...rows.map(r => [
      r.rowIdx, r.raw, r.scheme, r.username,
      r.hostname, r.port, r.pathname, r.search, r.hash, r.valid ? 'Yes' : 'No'
    ])
  ].map(row => row.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\r\n');

  download('url_parsed.csv', 'text/csv', csv);
});

exportXlsxBtn.addEventListener('click', () => {
  const rows = sortedData();
  const aoa  = [
    ['Row','Original URL','Scheme','Username','Hostname','Port','Path','Query String','Params','Fragment','Valid'],
    ...rows.map(r => [
      r.rowIdx, r.raw, r.scheme, r.username,
      r.hostname, r.port, r.pathname, r.search,
      Object.entries(r.params).map(([k,v]) => `${k}=${Array.isArray(v)?v.join(','):v}`).join('; '),
      r.hash, r.valid ? 'Yes' : 'No'
    ])
  ];
  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.aoa_to_sheet(aoa);
  ws['!cols'] = [5,60,10,12,30,6,30,30,40,15,8].map(w => ({ wch: w }));
  XLSX.utils.book_append_sheet(wb, ws, 'Parsed URLs');
  XLSX.writeFile(wb, 'url_parsed.xlsx');
});

resetBtn.addEventListener('click', () => {
  state.workbook = state.rawRows = state.parsed = state.filtered = null;
  state.sortCol = null; state.sortDir = 'asc'; state.page = 1;
  fileInput.value = '';
  sheetSelect.innerHTML = '<option>— load a file first —</option>';
  sheetSelect.disabled = true;
  urlColInput.value = '';
  parseBtn.disabled = true;
  statsBar.classList.add('hidden');
  toolbar.classList.add('hidden');
  tableCard.classList.add('hidden');
  filterInput.value = '';
  schemeFilter.innerHTML = '<option value="">All schemes</option>';
  tbody.innerHTML = '';
});

// ── Helpers ───────────────────────────────────────────────────────────────────
function esc(s) {
  return String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function download(name, mime, content) {
  const a  = document.createElement('a');
  const blob = new Blob([content], { type: mime });
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}

function flash(btn, msg) {
  const orig = btn.textContent;
  btn.textContent = msg;
  setTimeout(() => { btn.textContent = orig; }, 1800);
}
