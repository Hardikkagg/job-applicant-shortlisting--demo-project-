/* ============================================================
   TalentLens — Frontend Application JavaScript
   Handles all API calls, DOM rendering, and UI interactions
   ============================================================ */

'use strict';

// ── STATE ─────────────────────────────────────────────────────────
let allCandidates = [];
let charts = {};

// ── INIT ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  startClock();
  loadDashboard();
});

// ══════════════════════════════════════════════════════════════════
//  NAVIGATION
// ══════════════════════════════════════════════════════════════════

function showView(viewName, el) {
  event && event.preventDefault();

  // Update active nav item
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  if (el) el.classList.add('active');

  // Hide all views, show target
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  const target = document.getElementById(`view-${viewName}`);
  if (target) target.classList.add('active');

  // Update topbar title
  const titles = {
    dashboard: 'Dashboard',
    candidates: 'All Candidates',
    add: 'Add Candidate',
    search: 'Search Candidates',
    shortlist: 'Shortlist',
    algorithms: 'Algorithm Reference'
  };
  document.getElementById('pageTitle').textContent = titles[viewName] || viewName;

  // Load data for view
  if (viewName === 'dashboard') loadDashboard();
  if (viewName === 'candidates') loadCandidates();
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// ══════════════════════════════════════════════════════════════════
//  CLOCK
// ══════════════════════════════════════════════════════════════════

function startClock() {
  const el = document.getElementById('liveClock');
  const tick = () => {
    const now = new Date();
    el.textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };
  tick();
  setInterval(tick, 1000);
}

// ══════════════════════════════════════════════════════════════════
//  TOAST NOTIFICATIONS
// ══════════════════════════════════════════════════════════════════

function toast(msg, type = 'success') {
  const icons = { success: 'bi-check-circle-fill', error: 'bi-x-circle-fill', info: 'bi-info-circle-fill' };
  const el = document.createElement('div');
  el.className = `tl-toast ${type}`;
  el.innerHTML = `<i class="bi ${icons[type]}" style="color:var(--accent-${type === 'success' ? 'g' : type === 'error' ? 'danger' : 'b'})"></i>${msg}`;
  document.getElementById('toastWrapper').appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

// ══════════════════════════════════════════════════════════════════
//  API HELPERS
// ══════════════════════════════════════════════════════════════════

async function apiFetch(url, options = {}) {
  try {
    const res = await fetch(url, options);
    return await res.json();
  } catch (e) {
    toast('Network error: ' + e.message, 'error');
    return null;
  }
}

// ══════════════════════════════════════════════════════════════════
//  DASHBOARD
// ══════════════════════════════════════════════════════════════════

async function loadDashboard() {
  const data = await apiFetch('/get_candidates');
  if (!data || !data.success) return;

  allCandidates = data.candidates;
  const candidates = allCandidates;

  // ── STATS ──
  document.getElementById('statTotal').textContent   = candidates.length;
  document.getElementById('statAvgScore').textContent =
    candidates.length ? (candidates.reduce((s, c) => s + (c.score || 0), 0) / candidates.length).toFixed(1) : '—';
  document.getElementById('statAvgExp').textContent  =
    candidates.length ? (candidates.reduce((s, c) => s + (c.experience || 0), 0) / candidates.length).toFixed(1) : '—';
  document.getElementById('statTopScore').textContent =
    candidates.length ? Math.max(...candidates.map(c => c.score || 0)).toFixed(1) : '—';

  // ── TOP 8 CHART ──
  const top8 = candidates.slice(0, 8);
  renderBarChart(top8);

  // ── EXP DISTRIBUTION PIE ──
  renderPieChart(candidates);

  // ── RECENT TABLE ──
  const recent = [...candidates]
    .sort((a, b) => b.id - a.id)
    .slice(0, 5);
  document.getElementById('recentTable').innerHTML = renderTable(recent, { compact: true });
}

function renderBarChart(top8) {
  const ctx = document.getElementById('chartTopCandidates').getContext('2d');
  if (charts.bar) charts.bar.destroy();

  charts.bar = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: top8.map(c => c.name.split(' ')[0]),
      datasets: [{
        label: 'Score',
        data: top8.map(c => c.score || 0),
        backgroundColor: top8.map((_, i) => `hsla(${160 + i * 15}, 70%, 65%, 0.8)`),
        borderColor: top8.map((_, i) => `hsl(${160 + i * 15}, 70%, 65%)`),
        borderWidth: 1,
        borderRadius: 6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` Score: ${ctx.raw}` } }
      },
      scales: {
        x: { grid: { color: '#1c2235' }, ticks: { color: '#8892ab', font: { size: 11 } } },
        y: { grid: { color: '#1c2235' }, ticks: { color: '#8892ab' }, suggestedMin: 0, suggestedMax: 100 }
      }
    }
  });
}

function renderPieChart(candidates) {
  const ctx = document.getElementById('chartExpDist').getContext('2d');
  if (charts.pie) charts.pie.destroy();

  const buckets = { '0–2 yrs': 0, '3–5 yrs': 0, '6–9 yrs': 0, '10+ yrs': 0 };
  candidates.forEach(c => {
    const e = c.experience || 0;
    if (e <= 2)      buckets['0–2 yrs']++;
    else if (e <= 5) buckets['3–5 yrs']++;
    else if (e <= 9) buckets['6–9 yrs']++;
    else             buckets['10+ yrs']++;
  });

  charts.pie = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: Object.keys(buckets),
      datasets: [{
        data: Object.values(buckets),
        backgroundColor: ['#6ee7b7', '#fcd34d', '#93c5fd', '#f9a8d4'],
        borderColor: '#161b27',
        borderWidth: 3,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#8892ab', padding: 14, font: { size: 12 } }
        }
      }
    }
  });
}

// ══════════════════════════════════════════════════════════════════
//  CANDIDATES TABLE
// ══════════════════════════════════════════════════════════════════

async function loadCandidates() {
  const container = document.getElementById('candidatesTable');
  container.innerHTML = `<div class="section-card"><table class="tl-table"><tbody><tr class="loading-row"><td colspan="8"><span class="spinner-ring"></span> Loading…</td></tr></tbody></table></div>`;

  const data = await apiFetch('/get_candidates');
  if (!data || !data.success) return;
  allCandidates = data.candidates;
  container.innerHTML = renderTable(allCandidates, { showActions: true });
  document.getElementById('sortAlgoBadge').style.display = 'none';
}

function renderTable(candidates, opts = {}) {
  if (!candidates.length) {
    return `<div class="section-card"><div class="empty-state"><i class="bi bi-inbox"></i><p>No candidates found.</p></div></div>`;
  }

  const rows = candidates.map((c, i) => {
    const rankClass = c.rank === 1 ? 'gold' : c.rank === 2 ? 'silver' : c.rank === 3 ? 'bronze' : '';
    const scorePill  = c.score >= 70 ? 'high' : c.score >= 40 ? 'medium' : 'low';
    const expPct     = Math.min(100, ((c.experience || 0) / 15) * 100);
    const skillTags  = (c.skills || '').split(',').slice(0, 4).map(s =>
      `<span class="skill-tag">${s.trim()}</span>`).join('');
    const extraSkills = (c.skills || '').split(',').length > 4
      ? `<span class="skill-tag" style="opacity:.6">+${(c.skills || '').split(',').length - 4}</span>` : '';

    const actions = opts.showActions ? `
      <td>
        <button class="btn-icon edit" onclick="openEdit(${JSON.stringify(c).replace(/"/g, '&quot;')})" title="Edit"><i class="bi bi-pencil"></i></button>
        <button class="btn-icon del" onclick="deleteCandidate(${c.id})" title="Delete"><i class="bi bi-trash"></i></button>
      </td>` : '';

    return `
      <tr style="animation-delay:${i * 30}ms">
        <td><span class="rank-badge ${rankClass}">${c.rank || i + 1}</span></td>
        <td style="font-weight:500">${c.name}</td>
        <td style="max-width:220px">${skillTags}${extraSkills}</td>
        <td>
          <div class="exp-bar">
            <span>${c.experience}</span>
            <div class="exp-bar-bg"><div class="exp-bar-fill" style="width:${expPct}%"></div></div>
          </div>
        </td>
        <td>$${Number(c.expected_salary || 0).toLocaleString()}</td>
        <td><span class="score-pill ${scorePill}">${(c.score || 0).toFixed(1)}</span></td>
        ${actions}
      </tr>`;
  }).join('');

  const actionHeader = opts.showActions ? '<th>Actions</th>' : '';
  const compact = opts.compact;

  return `
    <div class="section-card">
      <table class="tl-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Name</th>
            <th>Skills</th>
            ${!compact ? '<th>Experience</th><th>Salary</th><th>Score</th>' : '<th>Exp</th><th>Salary</th><th>Score</th>'}
            ${actionHeader}
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

// ── QUICK FILTER (client-side) ──────────────────────────────────
function quickFilterTable() {
  const q = document.getElementById('quickFilter').value.toLowerCase();
  const filtered = allCandidates.filter(c => c.name.toLowerCase().includes(q));
  document.getElementById('candidatesTable').innerHTML = renderTable(filtered, { showActions: true });
}

// ══════════════════════════════════════════════════════════════════
//  QUICK SORT
// ══════════════════════════════════════════════════════════════════

async function sortCandidates() {
  const key   = document.getElementById('sortKey').value;
  const order = document.getElementById('sortOrder').value;

  const container = document.getElementById('candidatesTable');
  container.innerHTML = `<div class="section-card"><table class="tl-table"><tbody><tr class="loading-row"><td colspan="8"><span class="spinner-ring"></span> Quick Sorting…</td></tr></tbody></table></div>`;

  const data = await apiFetch(`/sort_candidates?key=${key}&order=${order}`);
  if (!data || !data.success) { toast('Sort failed', 'error'); return; }

  allCandidates = data.candidates;
  container.innerHTML = renderTable(allCandidates, { showActions: true });

  const badge = document.getElementById('sortAlgoBadge');
  badge.style.display = 'inline-flex';
  badge.innerHTML = `<i class="bi bi-lightning-charge-fill"></i> Quick Sort by <strong>${key}</strong> (${order}) — O(n log n)`;
  toast(`Sorted by ${key} (${order}) using Quick Sort`, 'success');
}

// ══════════════════════════════════════════════════════════════════
//  ADD CANDIDATE
// ══════════════════════════════════════════════════════════════════

function previewScore() {
  const exp    = parseFloat(document.getElementById('addExperience').value) || 0;
  const salary = parseFloat(document.getElementById('addSalary').value) || 0;
  const skills = document.getElementById('addSkills').value || '';

  // Build skill tags
  const tags = skills.split(',').filter(s => s.trim()).map(s =>
    `<span class="skill-tag">${s.trim()}</span>`).join('');
  document.getElementById('skillTagsRow').innerHTML = tags;

  if (exp || salary || skills) {
    const skillsCount = skills.split(',').filter(s => s.trim()).length;
    const score = Math.max(0, Math.min(100, (exp * 2) + (skillsCount * 3) - (salary / 10000)));
    document.getElementById('scorePreviewVal').textContent = score.toFixed(1);
    document.getElementById('scorePreview').style.display = 'block';
  } else {
    document.getElementById('scorePreview').style.display = 'none';
  }
}

// Also trigger on skills input change
document.addEventListener('DOMContentLoaded', () => {
  const skillsInput = document.getElementById('addSkills');
  if (skillsInput) skillsInput.addEventListener('input', previewScore);
});

async function addCandidate() {
  const name     = document.getElementById('addName').value.trim();
  const skills   = document.getElementById('addSkills').value.trim();
  const exp      = document.getElementById('addExperience').value;
  const salary   = document.getElementById('addSalary').value;
  const score    = document.getElementById('addScore').value;

  if (!name || !skills || !exp) {
    toast('Name, skills, and experience are required!', 'error');
    return;
  }

  const data = await apiFetch('/add_candidate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, skills, experience: exp, expected_salary: salary || 0, score: score || null })
  });

  if (data && data.success) {
    toast(`${name} added! Auto-score: ${data.score}`, 'success');
    clearForm();
  } else {
    toast(data?.error || 'Failed to add candidate', 'error');
  }
}

function clearForm() {
  ['addName', 'addSkills', 'addExperience', 'addSalary', 'addScore'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  document.getElementById('scorePreview').style.display = 'none';
  document.getElementById('skillTagsRow').innerHTML = '';
}

// ══════════════════════════════════════════════════════════════════
//  SEARCH
// ══════════════════════════════════════════════════════════════════

function switchSearchTab(panel, el) {
  document.querySelectorAll('.search-tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  document.querySelectorAll('.search-panel').forEach(p => p.classList.remove('active'));
  document.getElementById(`searchPanel-${panel}`).classList.add('active');
  document.getElementById('searchResults').innerHTML = '';
  document.getElementById('searchResultBadge').style.display = 'none';
}

function toggleSearchType() {
  const type = document.getElementById('searchType').value;
  document.getElementById('exactValCol').style.display = type === 'exact' ? '' : 'none';
  document.getElementById('rangeValCol').style.display = type === 'range'  ? '' : 'none';
}

async function searchNumeric() {
  const field = document.getElementById('searchField').value;
  const type  = document.getElementById('searchType').value;
  let url;

  if (type === 'exact') {
    const val = document.getElementById('searchValue').value;
    if (!val) { toast('Enter a value to search', 'error'); return; }
    url = `/search_candidate?field=${field}&value=${val}`;
  } else {
    const min = document.getElementById('searchMin').value;
    const max = document.getElementById('searchMax').value;
    if (!min || !max) { toast('Enter min and max values', 'error'); return; }
    url = `/search_candidate?field=${field}&min=${min}&max=${max}`;
  }

  const data = await apiFetch(url);
  showSearchResults(data);
}

async function searchBySkill() {
  const skills = document.getElementById('searchSkills').value.trim();
  if (!skills) { toast('Enter skills to filter by', 'error'); return; }
  const data = await apiFetch(`/search_candidate?skill=${encodeURIComponent(skills)}`);
  showSearchResults(data);
}

async function searchByName() {
  const name = document.getElementById('searchName').value.trim();
  if (!name) { toast('Enter a name to search', 'error'); return; }
  const data = await apiFetch(`/search_candidate?name=${encodeURIComponent(name)}`);
  showSearchResults(data);
}

function showSearchResults(data) {
  if (!data) return;

  const badge = document.getElementById('searchResultBadge');
  badge.style.display = 'inline-flex';
  badge.innerHTML = `<i class="bi bi-check2-circle"></i> ${data.method || 'Search'} — ${data.count} result(s) found`;

  const container = document.getElementById('searchResults');
  if (!data.success) {
    container.innerHTML = `<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><p>${data.error}</p></div>`;
    return;
  }
  container.innerHTML = renderTable(data.candidates, { showActions: false });
}

// ══════════════════════════════════════════════════════════════════
//  SHORTLIST
// ══════════════════════════════════════════════════════════════════

async function getShortlist() {
  const n      = document.getElementById('shortlistN').value || 5;
  const skills = document.getElementById('shortlistSkills').value.trim();
  let url = `/shortlist_candidates?n=${n}`;
  if (skills) url += `&skill=${encodeURIComponent(skills)}`;

  const container = document.getElementById('shortlistResults');
  container.innerHTML = `<div class="empty-state"><span class="spinner-ring"></span></div>`;

  const data = await apiFetch(url);
  if (!data || !data.success) { toast('Failed to get shortlist', 'error'); return; }

  const maxScore = Math.max(...data.shortlist.map(c => c.score || 0), 1);

  const cards = data.shortlist.map((c, i) => {
    const rankClass = i === 0 ? 'r1' : i === 1 ? 'r2' : i === 2 ? 'r3' : '';
    const medal     = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `#${c.rank}`;
    const pct       = ((c.score || 0) / maxScore * 100).toFixed(0);
    const skillTags = (c.skills || '').split(',').slice(0, 5).map(s =>
      `<span class="skill-tag">${s.trim()}</span>`).join('');

    return `
      <div class="shortlist-card" style="animation-delay:${i * 80}ms">
        <div class="shortlist-rank ${rankClass}">${medal}</div>
        <div class="shortlist-info">
          <div class="shortlist-name">${c.name}</div>
          <div class="shortlist-meta">
            <i class="bi bi-clock"></i> ${c.experience} yrs experience &nbsp;·&nbsp;
            <i class="bi bi-currency-dollar"></i> $${Number(c.expected_salary || 0).toLocaleString()} expected
          </div>
          <div class="skill-tags-row" style="margin-top:8px">${skillTags}</div>
          <div class="progress-bar-wrap">
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" style="width:${pct}%"></div>
            </div>
          </div>
        </div>
        <div class="shortlist-score">${(c.score || 0).toFixed(1)}</div>
      </div>`;
  }).join('');

  container.innerHTML = cards || `<div class="empty-state"><i class="bi bi-inbox"></i><p>No candidates match your criteria.</p></div>`;
  toast(`Top ${data.count} candidates shortlisted!`, 'success');
}

// ══════════════════════════════════════════════════════════════════
//  EDIT / DELETE
// ══════════════════════════════════════════════════════════════════

function openEdit(candidate) {
  document.getElementById('editId').value         = candidate.id;
  document.getElementById('editName').value       = candidate.name;
  document.getElementById('editSkills').value     = candidate.skills;
  document.getElementById('editExperience').value = candidate.experience;
  document.getElementById('editSalary').value     = candidate.expected_salary;
  document.getElementById('editScore').value      = '';

  const modal = new bootstrap.Modal(document.getElementById('editModal'));
  modal.show();
}

async function saveEdit() {
  const id      = document.getElementById('editId').value;
  const name    = document.getElementById('editName').value.trim();
  const skills  = document.getElementById('editSkills').value.trim();
  const exp     = document.getElementById('editExperience').value;
  const salary  = document.getElementById('editSalary').value;
  const score   = document.getElementById('editScore').value;

  const data = await apiFetch(`/update_candidate/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, skills, experience: exp, expected_salary: salary, score: score || null })
  });

  if (data && data.success) {
    bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
    toast(`${name} updated! New score: ${data.score}`, 'success');
    loadCandidates();
  } else {
    toast(data?.error || 'Update failed', 'error');
  }
}

async function deleteCandidate(id) {
  if (!confirm('Delete this candidate? This cannot be undone.')) return;

  const data = await apiFetch(`/delete_candidate/${id}`, { method: 'DELETE' });
  if (data && data.success) {
    toast('Candidate deleted', 'info');
    loadCandidates();
  } else {
    toast(data?.error || 'Delete failed', 'error');
  }
}

// ══════════════════════════════════════════════════════════════════
//  EXPORT CSV
// ══════════════════════════════════════════════════════════════════

function exportCSV() {
  window.location.href = '/export_csv';
  toast('Downloading CSV…', 'info');
}
