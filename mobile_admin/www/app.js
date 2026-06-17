/**
 * KC Legacy Valeting - Mobile Admin PWA
 * Connects to the backend API server
 */

// ── Configuration ──
let API_BASE = localStorage.getItem('kc_api_url') || 'https://kclegeacy.pythonanywhere.com';

// Admin entry name hash (SHA-256 of 'kclvs417xh')
const ADMIN_HASH = '5641858a79c6ef95b1070f43449a3148de78b61016c659de30fcb1d6ae48efa2';

// State
let currentBooking = null;
let isAuthenticated = false;
let refreshTimer = null;
let lastBookingCount = 0;

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

async function apiPost(endpoint, data) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.error('API POST error:', e);
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
  const savedUrl = localStorage.getItem('kc_api_url');
  if (savedUrl) {
    document.getElementById('api-url-input').value = savedUrl;
    API_BASE = savedUrl;
  }
  // Auto-login for preview (bypass login screen)
  isAuthenticated = true;
  showApp();
}

async function doLogin() {
  const input = document.getElementById('entry-input');
  const apiInput = document.getElementById('api-url-input');
  const error = document.getElementById('login-error');
  const val = input.value.trim();
  const apiUrl = apiInput.value.trim();

  if (!apiUrl) {
    error.textContent = 'Please enter the API server URL.';
    return;
  }
  if (!val) {
    error.textContent = 'Please enter the admin entry name.';
    return;
  }

  // Save API URL
  localStorage.setItem('kc_api_url', apiUrl);
  API_BASE = apiUrl;

  const hash = await sha256(val);
  if (hash === ADMIN_HASH) {
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
  stopAutoRefresh();
  localStorage.removeItem('kc_admin_auth');
  document.getElementById('app-screen').classList.remove('active');
  document.getElementById('login-screen').classList.add('active');
  document.getElementById('entry-input').value = '';
  document.getElementById('login-error').textContent = '';
}

function startAutoRefresh() {
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(() => {
    if (isAuthenticated) loadAllData();
  }, 10000); // Refresh every 10 seconds
}

function stopAutoRefresh() {
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
}

function showApp() {
  document.getElementById('login-screen').classList.remove('active');
  document.getElementById('app-screen').classList.add('active');
  loadAllData();
  startAutoRefresh();
}

function showToast(message) {
  const existing = document.querySelector('.toast-notification');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast-notification';
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: #d4af37;
    color: #000;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: bold;
    z-index: 9999;
    animation: slideDown 0.3s ease;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  `;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'slideUp 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ── Calendar State ──
let calendarDate = new Date();
let allBookings = [];

// ── Filter State ──
let currentSearch = '';
let currentStatusFilter = 'all';

function filterBookings(bookings) {
  return bookings.filter(b => {
    const p = b.parsed || parseBookingContent(b.content || '');
    const statuses = JSON.parse(localStorage.getItem('kc_booking_statuses') || '{}');
    const status = statuses[b.filename] || 'pending';

    // Status filter
    if (currentStatusFilter !== 'all' && status !== currentStatusFilter) {
      return false;
    }

    // Search filter (name, phone, car, package)
    if (currentSearch) {
      const q = currentSearch.toLowerCase();
      const hay = [
        p.name || '',
        p.phone || '',
        p.carMake || '',
        p.package || '',
        p.carReg || '',
        p.email || ''
      ].join(' ').toLowerCase();
      if (!hay.includes(q)) return false;
    }

    return true;
  });
}

// ── Data Loading ──
async function loadAllData() {
  setConnStatus('', 'Connecting...');

  const bookingsData = await apiGet('/api/bookings');
  const bookingsOk = !bookingsData.error;

  if (bookingsOk) {
    setConnStatus('online', 'Connected to the KC Legacy Server');
  } else {
    setConnStatus('offline', 'Connection failed - check API server');
  }

  // Check for new bookings
  const currentCount = bookingsOk ? (bookingsData.count || 0) : 0;
  if (lastBookingCount > 0 && currentCount > lastBookingCount) {
    const newCount = currentCount - lastBookingCount;
    showToast(`🎉 ${newCount} new booking${newCount > 1 ? 's' : ''} received!`);
  }
  lastBookingCount = currentCount;

  // Store for calendar
  allBookings = bookingsData.bookings || [];

  const filtered = filterBookings(allBookings);
  renderBookings({ bookings: filtered, count: filtered.length });
  renderCalendar();

  // Stats
  document.getElementById('stat-bookings').textContent =
    bookingsOk ? (bookingsData.count || 0) : '!';
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
    const hasFilter = currentSearch || currentStatusFilter !== 'all';
    const msg = hasFilter ? 'No bookings match your filters' : 'No bookings found';
    container.innerHTML = `<div class="empty-state">${msg}</div>`;
    return;
  }

  // Check if booking is from last 24 hours
  function isNew(submissionDate) {
    if (!submissionDate) return false;
    try {
      const sub = new Date(submissionDate);
      const now = new Date();
      const diff = (now - sub) / (1000 * 60 * 60); // hours
      return diff < 24;
    } catch { return false; }
  }

  // Load cached response statuses
  const statuses = JSON.parse(localStorage.getItem('kc_booking_statuses') || '{}');

  container.innerHTML = bookings.map((b, i) => {
    const p = b.parsed || parseBookingContent(b.content || '');
    const newBadge = isNew(p.submissionDate) ? '<span class="badge-new">NEW</span>' : '';
    const addonsCount = p.addons ? p.addons.length : 0;
    const addonsText = addonsCount > 0 ? `+ ${addonsCount} add-on${addonsCount > 1 ? 's' : ''}` : '';
    const status = statuses[b.filename] || 'pending';
    const statusClass = `status-${status}`;
    const statusLabel = status === 'reschedule' ? 'Reschedule' : status.charAt(0).toUpperCase() + status.slice(1);

    const addonsDetail = p.addons && p.addons.length > 0
      ? p.addons.map(a => `• ${escapeHtml(a)}`).join('<br>')
      : '';
    const emailLine = p.email ? `<div class="booking-detail-line">✉️ ${escapeHtml(p.email)}</div>` : '';
    const regLine = p.carReg ? `<span class="booking-reg">| 🔖 ${escapeHtml(p.carReg)}</span>` : '';
    const specialLine = p.specialRequests ? `<div class="booking-special">💬 ${escapeHtml(p.specialRequests.substring(0, 60))}${p.specialRequests.length > 60 ? '...' : ''}</div>` : '';

    return `
      <div class="booking-card" data-index="${i}" data-filename="${escapeHtml(b.filename)}">
        <div class="booking-card-header">
          <div class="booking-name">${escapeHtml(p.name || 'Unknown')}</div>
          <div style="display:flex;gap:6px;align-items:center;">
            <span class="status-badge ${statusClass}">${statusLabel}</span>
            ${newBadge}
          </div>
        </div>
        <div class="booking-phone">📞 ${escapeHtml(p.phone || 'No phone')}</div>
        ${emailLine}
        <div class="booking-details-row">
          <span class="booking-package">${escapeHtml(p.package || 'No package')}</span>
          <span class="booking-price">£${escapeHtml(p.totalPrice || p.packagePrice || '0')}</span>
        </div>
        <div class="booking-details-row">
          <span class="booking-date">📅 ${escapeHtml(p.scheduledDate || 'No date')}</span>
          <span class="booking-car">🚗 ${escapeHtml(p.carMake || 'No vehicle')}</span>
          ${regLine}
        </div>
        ${addonsDetail ? `<div class="booking-addons-detail">${addonsDetail}</div>` : ''}
        ${specialLine}
        <div class="booking-ref">Ref: #${escapeHtml(p.bookingId || '')}</div>
      </div>
    `;
  }).join('');

  container.querySelectorAll('.booking-card').forEach(el => {
    el.addEventListener('click', () => openBooking(el.dataset.filename));
  });
}

function parseBookingContent(content) {
  const lines = content.split('\n');
  const p = {
    name: '', phone: '', email: '', carMake: '', carReg: '',
    package: '', packagePrice: '', scheduledDate: '',
    addons: [], totalPrice: '', specialRequests: '',
    bookingId: '', submissionDate: ''
  };
  let inAddons = false, inSpecial = false;
  for (let line of lines) {
    line = line.trim();
    if (line.startsWith('Booking ID:')) p.bookingId = line.split(':')[1].trim();
    else if (line.startsWith('Submission Date:')) p.submissionDate = line.split(':').slice(1).join(':').trim();
    else if (line.startsWith('Name:')) p.name = line.split(':')[1].trim();
    else if (line.startsWith('Phone:')) p.phone = line.split(':')[1].trim();
    else if (line.startsWith('Email:')) p.email = line.split(':')[1].trim();
    else if (line.startsWith('Vehicle:')) p.carMake = line.split(':')[1].trim();
    else if (line.startsWith('Registration:')) p.carReg = line.split(':')[1].trim();
    else if (line.startsWith('Selected Package:')) {
      const pkg = line.split(':').slice(1).join(':').trim();
      p.package = pkg.split('(')[0].trim();
      const m = pkg.match(/£(\d+)/);
      if (m) p.packagePrice = m[1];
    }
    else if (line.startsWith('Scheduled Date:')) p.scheduledDate = line.split(':').slice(1).join(':').trim();
    else if (line.startsWith('ADD-ONS INCLUDED:')) { inAddons = true; inSpecial = false; }
    else if (line.startsWith('SPECIAL REQUESTS:')) { inAddons = false; inSpecial = true; }
    else if (line.startsWith('ESTIMATED TOTAL:')) {
      inSpecial = false;
      const total = line.split(':').slice(1).join(':').trim();
      p.totalPrice = total.replace('£', '');
    }
    else if (inAddons && line.startsWith('-')) p.addons.push(line.substring(1).trim());
    else if (inSpecial && line && !line.startsWith('=') && !line.startsWith('-')) {
      p.specialRequests += (p.specialRequests ? ' ' : '') + line;
    }
  }
  return p;
}

async function openBooking(filename) {
  const data = await apiGet(`/api/bookings/${encodeURIComponent(filename)}`);
  if (data.error) {
    alert('Error: ' + data.error);
    return;
  }

  currentBooking = filename;
  // Use parsed data if available, otherwise parse from content
  const p = data.parsed || parseBookingContent(data.content || '');

  // Build rich detail view
  const addonsHtml = p.addons && p.addons.length > 0
    ? p.addons.map(a => `<li>${escapeHtml(a)}</li>`).join('')
    : '<li>None</li>';

  const detailHtml = `
    <div class="detail-section">
      <div class="detail-label">Customer</div>
      <div class="detail-value">${escapeHtml(p.name || 'Unknown')}</div>
      <div class="detail-sub">📞 ${escapeHtml(p.phone || 'N/A')} ${p.email ? ' | ✉️ ' + escapeHtml(p.email) : ''}</div>
    </div>
    <div class="detail-section">
      <div class="detail-label">Vehicle</div>
      <div class="detail-value">${escapeHtml(p.carMake || 'N/A')}</div>
      <div class="detail-sub">Reg: ${escapeHtml(p.carReg || 'N/A')}</div>
    </div>
    <div class="detail-section">
      <div class="detail-label">Package</div>
      <div class="detail-value">${escapeHtml(p.package || 'N/A')} (from £${escapeHtml(p.packagePrice || '0')})</div>
      <div class="detail-sub">Scheduled: ${escapeHtml(p.scheduledDate || 'N/A')}</div>
    </div>
    <div class="detail-section">
      <div class="detail-label">Add-Ons</div>
      <ul class="detail-list">${addonsHtml}</ul>
    </div>
    <div class="detail-section">
      <div class="detail-label">Special Requests</div>
      <div class="detail-sub">${escapeHtml(p.specialRequests || 'None')}</div>
    </div>
    <div class="detail-section total-section">
      <div class="detail-label">Total Price</div>
      <div class="detail-total">£${escapeHtml(p.totalPrice || '0')}</div>
    </div>
    <div class="detail-ref">Ref: #${escapeHtml(p.bookingId || '')} | ${escapeHtml(p.submissionDate || '')}</div>
  `;

  document.getElementById('booking-content').innerHTML = detailHtml;

  // Load cached response for this booking
  const statuses = JSON.parse(localStorage.getItem('kc_booking_statuses') || '{}');
  const responses = JSON.parse(localStorage.getItem('kc_booking_responses') || '{}');
  document.getElementById('status-select').value = statuses[filename] || 'pending';
  document.getElementById('response-text').value = responses[filename] || '';
  document.getElementById('response-status-msg').textContent = '';

  document.getElementById('booking-modal').classList.add('active');
}

async function saveResponse() {
  if (!currentBooking) return;
  const status = document.getElementById('status-select').value;
  const text = document.getElementById('response-text').value.trim();

  // Save locally for immediate UI feedback
  const statuses = JSON.parse(localStorage.getItem('kc_booking_statuses') || '{}');
  statuses[currentBooking] = status;
  localStorage.setItem('kc_booking_statuses', JSON.stringify(statuses));

  // Save to server
  const msgEl = document.getElementById('response-status-msg');
  try {
    const res = await apiPost(`/api/bookings/${encodeURIComponent(currentBooking)}/response`, {status, message: text});
    if (res.success) {
      msgEl.textContent = 'Response saved. Customer will see it in their booking app.';
      msgEl.style.color = '#4caf50';
    } else {
      msgEl.textContent = 'Server error: ' + (res.error || 'Unknown');
      msgEl.style.color = '#ff4444';
    }
  } catch (e) {
    msgEl.textContent = 'Saved locally only (server offline)';
    msgEl.style.color = 'var(--muted)';
  }
  setTimeout(() => { msgEl.textContent = ''; }, 3000);

  // Refresh list to show new status badge
  loadAllData();
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
function renderCalendar() {
  const year = calendarDate.getFullYear();
  const month = calendarDate.getMonth();

  // Update label
  const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  document.getElementById('cal-month-label').textContent = `${monthNames[month]} ${year}`;

  // Get bookings by date
  const bookingDates = {};
  allBookings.forEach(b => {
    const p = b.parsed || parseBookingContent(b.content || '');
    if (p.scheduledDate) {
      const d = p.scheduledDate;
      bookingDates[d] = (bookingDates[d] || 0) + 1;
    }
  });

  // Build grid
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const today = new Date();
  const isTodayMonth = today.getFullYear() === year && today.getMonth() === month;

  let html = '';
  // Empty cells before start of month
  for (let i = 0; i < firstDay; i++) {
    html += '<div class="cal-day empty"></div>';
  }
  // Days
  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const count = bookingDates[dateStr] || 0;
    const isToday = isTodayMonth && today.getDate() === day;
    const hasBooking = count > 0;

    html += `
      <div class="cal-day ${isToday ? 'today' : ''} ${hasBooking ? 'has-booking' : ''}"
           data-date="${dateStr}">
        <span class="day-num">${day}</span>
        ${hasBooking ? `<span class="day-count">${count}</span>` : ''}
      </div>
    `;
  }

  document.getElementById('calendar-days').innerHTML = html;

  // Click handlers
  document.querySelectorAll('.cal-day:not(.empty)').forEach(el => {
    el.addEventListener('click', () => showDayBookings(el.dataset.date));
  });
}

function showDayBookings(dateStr) {
  const dayBookings = allBookings.filter(b => {
    const p = b.parsed || parseBookingContent(b.content || '');
    return p.scheduledDate === dateStr;
  });

  document.getElementById('day-label').textContent = `Bookings for ${dateStr}`;
  const container = document.getElementById('day-bookings-list');

  if (dayBookings.length === 0) {
    container.innerHTML = '<div class="empty-state">No bookings for this date</div>';
  } else {
    const statuses = JSON.parse(localStorage.getItem('kc_booking_statuses') || '{}');
    container.innerHTML = dayBookings.map(b => {
      const p = b.parsed || parseBookingContent(b.content || '');
      const status = statuses[b.filename] || 'pending';
      return `
        <div class="booking-card" data-filename="${escapeHtml(b.filename)}">
          <div class="booking-card-header">
            <div class="booking-name">${escapeHtml(p.name || 'Unknown')}</div>
            <span class="status-badge status-${status}">${status}</span>
          </div>
          <div class="booking-phone">📞 ${escapeHtml(p.phone || 'No phone')}</div>
          <div class="booking-details-row">
            <span class="booking-package">${escapeHtml(p.package || 'No package')}</span>
            <span class="booking-price">£${escapeHtml(p.totalPrice || p.packagePrice || '0')}</span>
          </div>
        </div>
      `;
    }).join('');

    container.querySelectorAll('.booking-card').forEach(el => {
      el.addEventListener('click', () => openBooking(el.dataset.filename));
    });
  }

  document.getElementById('calendar-grid').style.display = 'none';
  document.getElementById('day-bookings').style.display = 'block';
}

function backToCalendar() {
  document.getElementById('calendar-grid').style.display = 'block';
  document.getElementById('day-bookings').style.display = 'none';
}

// ── Send to Customer ──
async function sendToCustomer() {
  if (!currentBooking) return;
  const status = document.getElementById('status-select').value;
  const text = document.getElementById('response-text').value.trim();

  if (!text) {
    alert('Please type a message before sending.');
    return;
  }

  // Save locally
  const statuses = JSON.parse(localStorage.getItem('kc_booking_statuses') || '{}');
  statuses[currentBooking] = status;
  localStorage.setItem('kc_booking_statuses', JSON.stringify(statuses));

  // Post to server
  const msgEl = document.getElementById('response-status-msg');
  try {
    const res = await apiPost(`/api/bookings/${encodeURIComponent(currentBooking)}/response`, {status, message: text});
    if (res.success) {
      msgEl.textContent = 'Message sent to customer! They\'ll see it in their booking app.';
      msgEl.style.color = '#4caf50';
    } else {
      msgEl.textContent = 'Server error: ' + (res.error || 'Unknown');
      msgEl.style.color = '#ff4444';
    }
  } catch (e) {
    msgEl.textContent = 'Saved locally only (server offline)';
    msgEl.style.color = 'var(--muted)';
  }
  setTimeout(() => { msgEl.textContent = ''; }, 4000);

  loadAllData();
}

// ── Live Date/Time ──
function updateDateTime() {
  const el = document.getElementById('live-datetime');
  if (!el) return;
  const now = new Date();
  const dateStr = now.toLocaleDateString('en-GB', {
    weekday: 'short', day: 'numeric', month: 'short', year: 'numeric'
  });
  const timeStr = now.toLocaleTimeString('en-GB', {
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  });
  el.innerHTML = `<span class="date-part">${dateStr}</span> | ${timeStr}`;
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

// ── Tabs ──
function switchTab(tabName) {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabName);
  });
  document.querySelectorAll('.tab-panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === `tab-${tabName}`);
  });
  if (tabName === 'calendar') {
    renderCalendar();
  }
}

// ── Event Listeners ──
document.addEventListener('DOMContentLoaded', () => {
  checkAuth();
  updateDateTime();
  setInterval(updateDateTime, 1000);

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

  // Search
  const searchInput = document.getElementById('booking-search');
  if (searchInput) {
    searchInput.addEventListener('input', e => {
      currentSearch = e.target.value.trim();
      const filtered = filterBookings(allBookings);
      renderBookings({ bookings: filtered, count: filtered.length });
    });
  }

  // Filter chips
  document.querySelectorAll('.filter-chips .chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.filter-chips .chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      currentStatusFilter = chip.dataset.status;
      const filtered = filterBookings(allBookings);
      renderBookings({ bookings: filtered, count: filtered.length });
    });
  });

  // Modals
  document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', closeAllModals);
  });
  document.getElementById('delete-booking-btn').addEventListener('click', deleteCurrentBooking);
  document.getElementById('save-response-btn').addEventListener('click', saveResponse);
  document.getElementById('send-email-btn').addEventListener('click', sendToCustomer);

  // Calendar navigation
  document.getElementById('cal-prev').addEventListener('click', () => {
    calendarDate.setMonth(calendarDate.getMonth() - 1);
    renderCalendar();
  });
  document.getElementById('cal-next').addEventListener('click', () => {
    calendarDate.setMonth(calendarDate.getMonth() + 1);
    renderCalendar();
  });
  document.getElementById('back-to-cal').addEventListener('click', backToCalendar);

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
