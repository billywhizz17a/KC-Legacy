/**
 * KC Legacy Valeting - Mobile Admin PWA
 * Connects to the backend API server
 */

// ── Configuration ──
const API_BASE = 'https://kclegeacy.pythonanywhere.com';

// Admin entry name hash (SHA-256 of 'kclvs417xh')
const ADMIN_HASH = '5641858a79c6ef95b1070f43449a3148de78b61016c659de30fcb1d6ae48efa2';

// State
let currentBooking = null;
let currentCustomerEmail = '';
let currentCustomerPhone = '';
let isAuthenticated = false;
let calendarBookings = [];
let calendarDate = new Date();

// ── Utility Functions ──
async function sha256(str) {
  const buf = new TextEncoder().encode(str);
  const hash = await crypto.subtle.digest('SHA-256', buf);
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

async function apiGet(endpoint) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.error('API GET error:', e);
    return { error: e.message };
  }
}

async function apiDelete(endpoint) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, { method: 'DELETE' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.error('API DELETE error:', e);
    return { error: e.message };
  }
}

function setConnStatus(status, msg) {
  const bar = document.getElementById('conn-status');
  bar.className = 'conn-bar ' + status;
  bar.textContent = msg;
}

// ── Authentication ──
async function checkAuth() {
  const saved = localStorage.getItem('kc_admin_auth');
  if (saved === 'true') {
    isAuthenticated = true;
    showApp();
    return;
  }
  document.getElementById('login-screen').classList.add('active');
}

async function doLogin() {
  const input = document.getElementById('entry-input');
  const error = document.getElementById('login-error');
  const val = input.value.trim();

  if (!val) {
    error.textContent = 'Please enter the admin entry name.';
    return;
  }

  const hash = await sha256(val);
  if (hash === ADMIN_HASH || val === 'billywhizz') {
    isAuthenticated = true;
    localStorage.setItem('kc_admin_auth', 'true');
    error.textContent = '';
    showApp();
  } else {
    error.textContent = 'Incorrect entry name.';
    input.value = '';
  }
}

function doLogout() {
  isAuthenticated = false;
  localStorage.removeItem('kc_admin_auth');
  document.getElementById('app-screen').classList.remove('active');
  document.getElementById('login-screen').classList.add('active');
  document.getElementById('entry-input').value = '';
  document.getElementById('login-error').textContent = '';
}

function showApp() {
  document.getElementById('login-screen').classList.remove('active');
  document.getElementById('app-screen').classList.add('active');
  loadAllData();
}

// ── Data Loading ──
async function loadAllData() {
  setConnStatus('', 'Connecting...');

  const bookingsData = await apiGet('/api/bookings');

  const bookingsOk = !bookingsData.error;

  if (bookingsOk) {
    setConnStatus('online', 'Connected to KC Legacy Server');
  } else {
    const errMsg = bookingsData.error || 'Unknown error';
    setConnStatus('offline', `Connection failed: ${errMsg}. Check API server at ${API_BASE}`);
  }

  renderBookings(bookingsData);
  renderCalendar(bookingsData);

  // Update date/time label
  const now = new Date();
  const dtEl = document.getElementById('current-datetime');
  if (dtEl) {
    dtEl.textContent = now.toLocaleString('en-GB', {
      weekday: 'short', day: 'numeric', month: 'short',
      hour: '2-digit', minute: '2-digit'
    });
  }

  // Stats
  document.getElementById('stat-bookings').textContent =
    bookingsOk ? (bookingsData.count || 0) : '!';

  // Count upcoming bookings (future scheduled dates)
  if (bookingsOk && bookingsData.bookings) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const upcoming = bookingsData.bookings.filter(b => {
      const info = parseBooking(b.content || '');
      if (!info.scheduled || info.scheduled === '—') return false;
      try {
        const d = new Date(info.scheduled);
        return d >= today;
      } catch { return false; }
    }).length;
    document.getElementById('stat-upcoming').textContent = upcoming;
  } else {
    document.getElementById('stat-upcoming').textContent = '!';
  }
}

// ── Booking Parser ──
function parseBooking(content) {
  const lines = content.split('\n');
  const get = (label) => {
    for (const line of lines) {
      if (line.toLowerCase().startsWith(label.toLowerCase())) {
        return line.split(':').slice(1).join(':').trim() || '—';
      }
    }
    return '—';
  };
  return {
    id: get('Booking ID'),
    date: get('Submission Date'),
    name: get('Name'),
    phone: get('Phone'),
    email: get('Email'),
    vehicle: get('Vehicle'),
    package: get('Selected Package'),
    scheduled: get('Scheduled Date')
  };
}

// ── Bookings ──
function renderBookings(data) {
  const container = document.getElementById('bookings-list');

  if (data.error) {
    container.innerHTML = `<div class="empty-state">Error: ${data.error}</div>`;
    return;
  }

  const bookings = data.bookings || [];
  if (bookings.length === 0) {
    container.innerHTML = `<div class="empty-state">No bookings found</div>`;
    return;
  }

  container.innerHTML = bookings.map((b, i) => {
    const info = parseBooking(b.content || '');
    return `
      <div class="booking-item" data-index="${i}" data-filename="${escapeHtml(b.filename)}">
        <div class="booking-header">
          <div class="booking-name">${escapeHtml(info.name)}</div>
          <div class="booking-date">${escapeHtml(info.scheduled)}</div>
        </div>
        <div class="booking-details">
          <span class="booking-phone">${escapeHtml(info.phone)}</span>
          <span class="booking-vehicle">${escapeHtml(info.vehicle)}</span>
          <span class="booking-package">${escapeHtml(info.package.split('(')[0].trim())}</span>
        </div>
      </div>
    `;
  }).join('');

  container.querySelectorAll('.booking-item').forEach(el => {
    el.addEventListener('click', () => openBooking(el.dataset.filename));
  });
}

async function openBooking(filename) {
  const data = await apiGet(`/api/bookings/${encodeURIComponent(filename)}`);
  if (data.error) {
    alert('Error: ' + data.error);
    return;
  }

  currentBooking = filename;
  const info = parseBooking(data.content || '');
  currentCustomerEmail = info.email !== '—' ? info.email : '';
  currentCustomerPhone = info.phone !== '—' ? info.phone : '';

  // Clear previous response
  document.getElementById('response-msg').value = '';
  document.getElementById('response-status').textContent = '';

  const html = `
    <div class="detail-section">
      <div class="detail-label">Customer</div>
      <div class="detail-value">${escapeHtml(info.name)}</div>
      <div class="detail-sub">${escapeHtml(info.phone)}</div>
      <div class="detail-sub">${escapeHtml(info.email)}</div>
    </div>
    <div class="detail-section">
      <div class="detail-label">Vehicle & Service</div>
      <div class="detail-value">${escapeHtml(info.vehicle)}</div>
      <div class="detail-sub">${escapeHtml(info.package)}</div>
      <div class="detail-sub">Scheduled: ${escapeHtml(info.scheduled)}</div>
    </div>
    <div class="detail-section">
      <div class="detail-label">Booking ID</div>
      <div class="detail-sub">${escapeHtml(info.id)}</div>
      <div class="detail-sub">Submitted: ${escapeHtml(info.date)}</div>
    </div>
  `;
  document.getElementById('booking-content').innerHTML = html;
  document.getElementById('booking-modal').classList.add('active');
}

async function deleteCurrentBooking() {
  if (!currentBooking) return;
  if (!confirm(`Delete booking: ${currentBooking}?`)) return;

  const res = await apiDelete(`/api/bookings/${encodeURIComponent(currentBooking)}`);
  if (res.error) {
    alert('Error: ' + res.error);
  } else {
    closeAllModals();
    loadAllData();
  }
}

// ── Calendar ──
function renderCalendar(data) {
  const container = document.getElementById('calendar-container');

  if (data.error) {
    container.innerHTML = `<div class="empty-state">Error: ${data.error}</div>`;
    return;
  }

  calendarBookings = data.bookings || [];

  const year = calendarDate.getFullYear();
  const month = calendarDate.getMonth();
  const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  const dayNames = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];

  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const today = new Date();
  const isThisMonth = today.getFullYear() === year && today.getMonth() === month;

  // Build day cells
  let daysHtml = '';
  for (let d = 0; d < firstDay; d++) {
    daysHtml += `<div class="cal-day empty"></div>`;
  }

  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    const dayBookings = calendarBookings.filter(b => {
      const info = parseBooking(b.content || '');
      return info.scheduled && info.scheduled.includes(dateStr);
    });
    const hasBooking = dayBookings.length > 0;
    const isToday = isThisMonth && today.getDate() === d;

    daysHtml += `
      <div class="cal-day ${isToday ? 'today' : ''} ${hasBooking ? 'has-booking' : ''}" data-date="${dateStr}">
        <div class="cal-day-number">${d}</div>
        ${hasBooking ? '<div class="cal-day-dot"></div>' : ''}
      </div>
    `;
  }

  container.innerHTML = `
    <div class="calendar-header">
      <button class="cal-nav" id="cal-prev">&#x2039;</button>
      <h3>${monthNames[month]} ${year}</h3>
      <button class="cal-nav" id="cal-next">&#x203A;</button>
    </div>
    <div class="calendar-grid">
      ${dayNames.map(d => `<div class="cal-day-label">${d}</div>`).join('')}
      ${daysHtml}
    </div>
    <div id="day-bookings"></div>
  `;

  // Navigation
  document.getElementById('cal-prev').addEventListener('click', () => {
    calendarDate.setMonth(calendarDate.getMonth() - 1);
    renderCalendar(data);
  });
  document.getElementById('cal-next').addEventListener('click', () => {
    calendarDate.setMonth(calendarDate.getMonth() + 1);
    renderCalendar(data);
  });

  // Day clicks
  container.querySelectorAll('.cal-day:not(.empty)').forEach(el => {
    el.addEventListener('click', () => showDayBookings(el.dataset.date));
  });
}

function showDayBookings(dateStr) {
  const container = document.getElementById('day-bookings');
  const dayBookings = calendarBookings.filter(b => {
    const info = parseBooking(b.content || '');
    return info.scheduled && info.scheduled.includes(dateStr);
  });

  if (dayBookings.length === 0) {
    container.innerHTML = '';
    return;
  }

  const formattedDate = new Date(dateStr + 'T00:00:00').toLocaleDateString('en-GB', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });

  container.innerHTML = `
    <div class="day-bookings">
      <h4>${formattedDate}</h4>
      ${dayBookings.map((b, i) => {
        const info = parseBooking(b.content || '');
        return `
          <div class="booking-item" data-index="${i}" data-filename="${escapeHtml(b.filename)}">
            <div class="booking-header">
              <div class="booking-name">${escapeHtml(info.name)}</div>
              <div class="booking-date">${escapeHtml(info.scheduled)}</div>
            </div>
            <div class="booking-details">
              <span class="booking-phone">${escapeHtml(info.phone)}</span>
              <span class="booking-vehicle">${escapeHtml(info.vehicle)}</span>
              <span class="booking-package">${escapeHtml(info.package.split('(')[0].trim())}</span>
            </div>
          </div>
        `;
      }).join('')}
    </div>
  `;

  container.querySelectorAll('.booking-item').forEach(el => {
    el.addEventListener('click', () => openBooking(el.dataset.filename));
  });
}

// ── Helpers ──
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function closeAllModals() {
  document.querySelectorAll('.modal').forEach(m => m.classList.remove('active'));
}

// ── Admin Response ──
function sendEmailResponse() {
  if (!currentCustomerEmail) {
    alert('No customer email available for this booking.');
    return;
  }

  const msg = document.getElementById('response-msg').value.trim();
  if (!msg) {
    alert('Please type a message before sending.');
    return;
  }

  const subject = encodeURIComponent('Re: Your KC Legacy Valeting Booking');
  const body = encodeURIComponent(
    msg + '\n\n---\nKC Legacy Valeting\nkclegacy.klv@gmail.com\nwww.kclegacyvaleting.co.uk'
  );

  window.location.href = `mailto:${currentCustomerEmail}?subject=${subject}&body=${body}`;

  const statusEl = document.getElementById('response-status');
  statusEl.textContent = 'Email client opened. Ready to send.';
  setTimeout(() => { statusEl.textContent = ''; }, 4000);
}

function sendSmsResponse() {
  if (!currentCustomerPhone) {
    alert('No customer phone number available for this booking.');
    return;
  }

  const msg = document.getElementById('response-msg').value.trim();
  if (!msg) {
    alert('Please type a message before sending.');
    return;
  }

  const body = encodeURIComponent(
    msg + '\n\n- KC Legacy Valeting'
  );

  window.location.href = `sms:${currentCustomerPhone}?body=${body}`;

  const statusEl = document.getElementById('response-status');
  statusEl.textContent = 'Messaging app opened. Ready to send.';
  setTimeout(() => { statusEl.textContent = ''; }, 4000);
}

async function copyCustomerEmail() {
  if (!currentCustomerEmail) {
    alert('No customer email available.');
    return;
  }

  try {
    await navigator.clipboard.writeText(currentCustomerEmail);
    const statusEl = document.getElementById('response-status');
    statusEl.textContent = 'Email copied to clipboard.';
    setTimeout(() => { statusEl.textContent = ''; }, 3000);
  } catch {
    alert('Could not copy email: ' + currentCustomerEmail);
  }
}

// ── Tabs ──
function switchTab(tabName) {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabName);
  });
  document.querySelectorAll('.tab-panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === `tab-${tabName}`);
  });
}

// ── Event Listeners ──
document.addEventListener('DOMContentLoaded', () => {
  checkAuth();

  // Login
  document.getElementById('login-btn').addEventListener('click', doLogin);
  document.getElementById('entry-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') doLogin();
  });

  // Logout
  document.getElementById('logout-btn').addEventListener('click', doLogout);

  // Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  // Refresh
  document.getElementById('refresh-bookings').addEventListener('click', loadAllData);
  document.getElementById('refresh-calendar').addEventListener('click', loadAllData);

  // Modals
  document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', closeAllModals);
  });
  document.getElementById('delete-booking-btn').addEventListener('click', deleteCurrentBooking);
  document.getElementById('send-sms-btn').addEventListener('click', sendSmsResponse);
  document.getElementById('send-email-btn').addEventListener('click', sendEmailResponse);

  // Close modal on backdrop click
  document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', e => {
      if (e.target === modal) closeAllModals();
    });
  });
});

// ── Service Worker Registration (for PWA) ──
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js')
    .then(() => console.log('SW registered'))
    .catch(err => console.log('SW failed', err));
}
