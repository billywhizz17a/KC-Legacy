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
let currentImage = null;
let isAuthenticated = false;

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

  const [bookingsData, imagesData] = await Promise.all([
    apiGet('/api/bookings'),
    apiGet('/api/images')
  ]);

  const bookingsOk = !bookingsData.error;
  const imagesOk = !imagesData.error;

  if (bookingsOk && imagesOk) {
    setConnStatus('online', `Connected - ${API_BASE}`);
  } else {
    const errMsg = bookingsData.error || imagesData.error || 'Unknown error';
    setConnStatus('offline', `Connection failed: ${errMsg}. Check API server at ${API_BASE}`);
  }

  renderBookings(bookingsData);
  renderGallery(imagesData);

  // Stats
  document.getElementById('stat-bookings').textContent =
    bookingsOk ? (bookingsData.count || 0) : '!';
  document.getElementById('stat-images').textContent =
    imagesOk ? (imagesData.count || 0) : '!';
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

// ── Gallery ──
function renderGallery(data) {
  const container = document.getElementById('gallery-grid');

  if (data.error) {
    container.innerHTML = `<div class="empty-state" style="grid-column:1/-1">Error: ${data.error}</div>`;
    return;
  }

  const images = data.images || [];
  if (images.length === 0) {
    container.innerHTML = `<div class="empty-state" style="grid-column:1/-1">No images found</div>`;
    return;
  }

  container.innerHTML = images.map(img => {
    const url = `${API_BASE}${img.url}`;
    return `
      <div class="gallery-item" data-filename="${escapeHtml(img.filename)}" data-url="${url}">
        <img src="${url}" alt="${escapeHtml(img.filename)}" loading="lazy">
        <div class="img-label">${escapeHtml(img.filename)}</div>
      </div>
    `;
  }).join('');

  container.querySelectorAll('.gallery-item').forEach(el => {
    el.addEventListener('click', () => {
      currentImage = el.dataset.filename;
      document.getElementById('viewer-img').src = el.dataset.url;
      document.getElementById('image-filename').textContent = el.dataset.filename;
      document.getElementById('image-modal').classList.add('active');
    });
  });
}

async function deleteCurrentImage() {
  if (!currentImage) return;
  if (!confirm(`Delete image: ${currentImage}?`)) return;

  const res = await apiDelete(`/api/images/${encodeURIComponent(currentImage)}`);
  if (res.error) {
    alert('Error: ' + res.error);
  } else {
    closeAllModals();
    loadAllData();
  }
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
  document.getElementById('refresh-gallery').addEventListener('click', loadAllData);

  // Modals
  document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', closeAllModals);
  });
  document.getElementById('delete-booking-btn').addEventListener('click', deleteCurrentBooking);
  document.getElementById('delete-image-btn').addEventListener('click', deleteCurrentImage);

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
