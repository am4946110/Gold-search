/* ── DOM refs ──────────────────────────────────────────── */
const form       = document.getElementById('searchForm');
const queryInput = document.getElementById('query');
const submitBtn  = document.getElementById('submitBtn');
const statusEl   = document.getElementById('status');
const resultsEl  = document.getElementById('results');

/* ── Helpers ───────────────────────────────────────────── */
function setStatus(type, html) {
  statusEl.className = 'status ' + (type || '');
  statusEl.innerHTML = html;
}

function clearResults() {
  resultsEl.innerHTML = '';
}

function hostname(url) {
  try { return new URL(url).hostname.replace(/^www\./, ''); }
  catch { return url; }
}

function escHtml(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ── Safe JSON fetch ────────────────────────────────────── */
/**
 * Fetches a URL and parses JSON.
 * Throws a descriptive Error if the server returns HTML or a non-JSON body,
 * so the caller gets a useful message instead of a raw SyntaxError.
 */
async function fetchJSON(url) {
  let res;
  try {
    res = await fetch(url);
  } catch (networkErr) {
    // Network-level failure (server truly not running, CORS, etc.)
    throw new Error('Cannot reach the server — is it running? (' + networkErr.message + ')');
  }

  const contentType = res.headers.get('content-type') || '';

  if (!contentType.includes('application/json')) {
    // Server returned HTML (404 page, error page, redirect, etc.)
    const preview = await res.text();
    const hint    = preview.trim().slice(0, 120);
    throw new Error(
      `Server returned HTTP ${res.status} with non-JSON body.\n` +
      `Content-Type: ${contentType}\n` +
      `Body preview: ${hint}`
    );
  }

  const data = await res.json();
  return data;
}

/* ── Render results ─────────────────────────────────────── */
function renderResults(data) {
  clearResults();

  const items = Array.isArray(data.results) ? data.results : [];

  if (!items.length) {
    resultsEl.innerHTML = `
      <div class="empty-state">
        <div class="icon">✦</div>
        <p>No results found. Try a different search term.</p>
      </div>`;
    return;
  }

  /* header */
  const header = document.createElement('div');
  header.className = 'results-header';
  header.innerHTML = `
    <span class="count">${items.length}</span>
    <span>result${items.length !== 1 ? 's' : ''} found</span>`;
  resultsEl.appendChild(header);

  /* cards */
  items.forEach((item, i) => {
    const card = document.createElement('a');
    card.className = 'result-card';
    card.href      = item.url || item.link || '#';
    card.target    = '_blank';
    card.rel       = 'noopener noreferrer';
    card.style.animationDelay = (i * 45) + 'ms';

    const src     = escHtml(hostname(item.url || item.link || ''));
    const title   = escHtml(item.title   || 'Untitled');
    const snippet = escHtml(item.snippet || item.description || item.body || '');
    const url     = escHtml(item.url     || item.link || '');

    card.innerHTML = `
      <span class="result-index">${String(i + 1).padStart(2, '0')}</span>
      ${src     ? `<p class="result-source">${src}</p>`     : ''}
      <h2 class="result-title">${title}</h2>
      ${snippet ? `<p class="result-snippet">${snippet}</p>` : ''}
      ${url     ? `<p class="result-url">${url}</p>`         : ''}`;

    resultsEl.appendChild(card);
  });
}

/* ── Search ─────────────────────────────────────────────── */
async function doSearch(query) {
  submitBtn.classList.add('loading');
  submitBtn.textContent = 'Searching…';
  clearResults();
  setStatus('', '<span class="spinner"></span> Searching for <em>' + escHtml(query) + '</em>…');

  try {
    const data = await fetchJSON('/api/search?' + new URLSearchParams({ q: query }));

    if (data.ok) {
      const n = Array.isArray(data.results) ? data.results.length : 0;
      setStatus('ok',
        `<span class="dot"></span> ${n} result${n !== 1 ? 's' : ''} for <em>${escHtml(query)}</em>`);
      renderResults(data);
    } else {
      /* Server responded but reported a failure (bad bat output, timeout, etc.) */
      const msg = data.error || 'Unknown server error';
      setStatus('error', `<span class="dot"></span> ${escHtml(msg)}`);

      /* Show extra debug info in console so you can fix the batch file */
      if (data.stdout || data.stderr) {
        console.group('Server debug info');
        if (data.stdout) console.log('stdout:', data.stdout);
        if (data.stderr) console.warn('stderr:', data.stderr);
        console.groupEnd();
      }

      clearResults();
    }
  } catch (err) {
    /* fetchJSON throws with a descriptive message — show it in the UI */
    setStatus('error', `<span class="dot"></span> ${escHtml(err.message)}`);
    console.error('[Gold Search] fetch error:', err);
    clearResults();
  } finally {
    submitBtn.classList.remove('loading');
    submitBtn.textContent = 'Search';
  }
}

/* ── Form submit ────────────────────────────────────────── */
form.addEventListener('submit', e => {
  e.preventDefault();
  const q = queryInput.value.trim();
  if (q) doSearch(q);
});

/* ── Restore query from URL on load ─────────────────────── */
window.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(location.search);
  const q = params.get('q') || params.get('query');
  if (q) {
    queryInput.value = q;
    doSearch(q);
  }
});