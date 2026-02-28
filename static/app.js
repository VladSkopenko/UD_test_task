const API = '/api/v1';
let currentLotId = null;
let ws = null;

// ── Utils ──────────────────────────────────────────────────────────────────

const fmt = (v) => parseFloat(v).toFixed(2);
const tsNow = () => new Date().toLocaleTimeString();

function timeLeft(end) {
  const diff = new Date(end) - Date.now();
  if (diff <= 0) return 'Ended';
  const m = Math.floor(diff / 60000);
  const s = Math.floor((diff % 60000) / 1000);
  return `${m}m ${s}s`;
}

// ── Lots list ──────────────────────────────────────────────────────────────

async function loadLots() {
  try {
    const res = await fetch(`${API}/lots`);
    const lots = await res.json();
    renderLotsList(lots);
  } catch {
    document.getElementById('lots-list').innerHTML = '<div class="muted" style="color:#cf5e5e;">Failed to load</div>';
  }
}

function renderLotsList(lots) {
  const el = document.getElementById('lots-list');
  if (!lots.length) {
    el.innerHTML = '<div class="muted">No active lots</div>';
    return;
  }
  el.innerHTML = lots.map(lot => `
    <div class="lot-card ${lot.id === currentLotId ? 'active' : ''}" onclick="selectLot(${lot.id}, '${lot.title}', '${lot.starting_price}', '${lot.end_time}')">
      <div class="lot-title">${lot.title}</div>
      <div class="lot-meta">
        <span class="lot-price">$${fmt(lot.starting_price)}</span>
        <span class="status-badge status-${lot.status}">${lot.status}</span>
      </div>
      <div class="lot-meta" style="margin-top:4px;">
        <span>ends in ${timeLeft(lot.end_time)}</span>
        <span>#${lot.id}</span>
      </div>
    </div>
  `).join('');
}

// ── Create lot ─────────────────────────────────────────────────────────────

async function createLot() {
  const title = document.getElementById('new-title').value.trim();
  const price = parseFloat(document.getElementById('new-price').value);
  const err = document.getElementById('create-error');
  err.textContent = '';

  if (!title)               { err.textContent = 'Title is required'; return; }
  if (!price || price <= 0) { err.textContent = 'Price must be > 0'; return; }

  try {
    const res = await fetch(`${API}/lots`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, starting_price: price }),
    });
    if (!res.ok) { err.textContent = 'Failed to create lot'; return; }
    document.getElementById('new-title').value = '';
    document.getElementById('new-price').value = '';
    await loadLots();
  } catch {
    err.textContent = 'Network error';
  }
}

// ── Lot detail ─────────────────────────────────────────────────────────────

function selectLot(id, title, startingPrice, endTime) {
  currentLotId = id;
  if (ws) ws.close();

  renderLotDetail({ id, title, starting_price: startingPrice, end_time: endTime });
  connectWs(id);
  loadLots();
}

function renderLotDetail(lot) {
  document.getElementById('lot-detail').innerHTML = `
    <div class="detail-header">
      <div>
        <h2>${lot.title}</h2>
        <div class="detail-meta">Lot #${lot.id}</div>
      </div>
    </div>

    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">Starting price</div>
        <div class="stat-value">$${fmt(lot.starting_price)}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Current price</div>
        <div class="stat-value green" id="detail-price">$${fmt(lot.starting_price)}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Time left</div>
        <div class="stat-value" id="detail-timer">${timeLeft(lot.end_time)}</div>
      </div>
    </div>

    <div class="bid-form-card">
      <h3>Place a bid</h3>
      <div class="row">
        <div>
          <div class="field-label">Your name</div>
          <input id="bid-bidder-name" type="text" placeholder="Alice" style="margin-bottom:0;" />
        </div>
        <div>
          <div class="field-label">Amount</div>
          <input id="bid-amount" type="number" placeholder="0.00" min="0.01" step="0.01" style="margin-bottom:0;" />
        </div>
        <button class="success sm" onclick="placeBid(${lot.id})">Bid</button>
      </div>
      <div class="error-msg" id="bid-error"></div>
    </div>

    <div class="feed-card">
      <h3>
        Live feed
        <span class="ws-dot" id="ws-dot"></span>
      </h3>
      <div class="feed-events" id="feed-events"></div>
    </div>
  `;

  startTimer(lot.end_time);
}

// ── Timer ──────────────────────────────────────────────────────────────────

function startTimer(endTime) {
  clearInterval(window._timerInterval);
  window._currentEndTime = endTime;
  window._timerInterval = setInterval(() => {
    const el = document.getElementById('detail-timer');
    if (el) el.textContent = timeLeft(window._currentEndTime);
    else clearInterval(window._timerInterval);
  }, 1000);
}

// ── WebSocket ──────────────────────────────────────────────────────────────

function connectWs(lotId) {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${proto}://${location.host}/api/v1/ws/lots/${lotId}`);

  ws.onopen = () => {
    const dot = document.getElementById('ws-dot');
    if (dot) dot.classList.add('connected');
  };

  ws.onclose = () => {
    const dot = document.getElementById('ws-dot');
    if (dot) dot.classList.remove('connected');
  };

  ws.onmessage = (e) => handleWsEvent(JSON.parse(e.data));
}

function handleWsEvent(data) {
  const feed = document.getElementById('feed-events');
  if (!feed) return;

  let html = '';

  if (data.type === 'new_bid') {
    html = `
      <div class="event-item new_bid">
        <span class="event-time">${tsNow()}</span>
        <strong>${data.bidder_name}</strong> bid <strong>$${fmt(data.amount)}</strong>
      </div>`;
    const priceEl = document.getElementById('detail-price');
    if (priceEl) priceEl.textContent = `$${fmt(data.amount)}`;
  }

  if (data.type === 'time_extended') {
    html = `
      <div class="event-item time_extended">
        <span class="event-time">${tsNow()}</span>
        ⏱ Time extended to ${new Date(data.end_time).toLocaleTimeString()}
      </div>`;
    window._currentEndTime = data.end_time;
  }

  if (data.type === 'lot_ended') {
    html = `
      <div class="event-item lot_ended">
        <span class="event-time">${tsNow()}</span>
        🔴 Lot ended
      </div>`;
    loadLots();
  }

  if (html) feed.insertAdjacentHTML('afterbegin', html);
}

// ── Place bid ──────────────────────────────────────────────────────────────

async function placeBid(lotId) {
  const bidderName = document.getElementById('bid-bidder-name').value.trim();
  const amount     = parseFloat(document.getElementById('bid-amount').value);
  const err        = document.getElementById('bid-error');
  err.textContent  = '';

  if (!bidderName)            { err.textContent = 'Name is required'; return; }
  if (!amount || amount <= 0) { err.textContent = 'Amount must be > 0'; return; }

  try {
    const res = await fetch(`${API}/lots/${lotId}/bids`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bidder_name: bidderName, amount }),
    });
    const json = await res.json();
    if (!res.ok) { err.textContent = json.detail || 'Failed to place bid'; return; }
    document.getElementById('bid-amount').value = '';
  } catch {
    err.textContent = 'Network error';
  }
}

// ── Init ───────────────────────────────────────────────────────────────────

loadLots();
setInterval(loadLots, 15000);
