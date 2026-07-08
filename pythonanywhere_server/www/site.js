/**
 * KC Legacy Valeting - Main Website JS
 * Handles navigation, booking form, quote calculator, gallery, and booking lookup
 */

// ── Config ──
const API_BASE = window.location.origin;

// ── Utility ──
function $(id) { return document.getElementById(id); }

function showMsg(id, text, type) {
  const el = $(id);
  el.textContent = text;
  el.className = 'form-msg ' + (type || '');
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ── Navigation ──
function showPage(pageName) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const page = $('page-' + pageName);
  const nav = document.querySelector(`.nav-item[data-page="${pageName}"]`);
  if (page) page.classList.add('active');
  if (nav) nav.classList.add('active');
  if (pageName === 'gallery') loadGallery();
  window.scrollTo(0, 0);

  // Auto-close sidebar on mobile
  closeSidebar();
}

function toggleSidebar() {
  $('sidebar').classList.toggle('active');
  $('sidebar-overlay').classList.toggle('active');
  document.body.style.overflow = $('sidebar').classList.contains('active') ? 'hidden' : '';
}

function closeSidebar() {
  $('sidebar').classList.remove('active');
  $('sidebar-overlay').classList.remove('active');
  document.body.style.overflow = '';
}

document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', (e) => {
    e.preventDefault();
    showPage(item.dataset.page);
  });
});

// Mobile menu toggle
$('menu-toggle').addEventListener('click', toggleSidebar);
$('sidebar-overlay').addEventListener('click', closeSidebar);

// ── Live Packages Config ──
async function loadPackages() {
  try {
    const res = await fetch(`${API_BASE}/api/packages`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const config = await res.json();
    renderPackageCards(config.packages || []);
    renderAddonCards(config.addons || []);
    renderPackageSelect(config.packages || []);
    renderAddonSelect(config.addons || []);
    // Re-bind event listeners for the dynamically created elements
    document.querySelectorAll('input[name="site-package"]').forEach(el => {
      el.addEventListener('change', updateQuote);
    });
    document.querySelectorAll('.addon-select input').forEach(el => {
      el.addEventListener('change', updateQuote);
    });
    updateQuote();
  } catch (e) {
    console.error('Failed to load packages from server, using fallback:', e);
  }
}

function renderPackageCards(packages) {
  const container = document.querySelector('.package-grid');
  if (!container) return;
  container.innerHTML = packages.map(pkg => `
    <div class="luxury-card">
      <h3>${escapeHtml(pkg.icon || '')} ${escapeHtml(pkg.name)} - ${escapeHtml(pkg.subtitle)}</h3>
      <p class="card-sub">${escapeHtml(pkg.description || '')}</p>
      <p class="card-price">${escapeHtml(pkg.priceText || '')}</p>
      <div class="card-details">
        <b>Includes:</b><br>
        ${(pkg.features || []).map(f => `• ${escapeHtml(f)}`).join('<br>')}<br>
        <br><b style="color:#d4af37;">✨ Add Ons Available Below</b>${pkg.footerNote ? `<br><br><i>${escapeHtml(pkg.footerNote)}</i>` : ''}
      </div>
    </div>
  `).join('');
}

function renderAddonCards(addons) {
  const container = document.querySelector('.addon-grid');
  if (!container) return;
  container.innerHTML = addons.map(addon => `
    <div class="addon-card"><h4>${escapeHtml(addon.icon || '')} ${escapeHtml(addon.name)}</h4><p class="addon-price">${escapeHtml(addon.priceLabel || '')}</p><p class="addon-desc">${escapeHtml(addon.description || '')}</p></div>
  `).join('');
}

function renderPackageSelect(packages) {
  const container = document.querySelector('.package-select-grid');
  if (!container) return;
  container.innerHTML = packages.map((pkg, i) => `
    <label class="package-select"><input type="radio" name="site-package" value="${escapeHtml(pkg.name)}|${pkg.fromPrice}"${i === 0 ? ' checked' : ''}><span>${escapeHtml(pkg.name)} - ${escapeHtml(pkg.subtitle)} (from £${pkg.fromPrice})</span></label>
  `).join('');
}

function renderAddonSelect(addons) {
  const container = document.querySelector('.addon-select-grid');
  if (!container) return;
  container.innerHTML = addons.map(addon => `
    <label class="addon-select"><input type="checkbox" value="${escapeHtml(addon.name)}|${addon.price}"><span>${escapeHtml(addon.name)} +£${addon.price}</span></label>
  `).join('');
}

// ── Quote Calculator ──
function calculateQuote() {
  const pkgEl = document.querySelector('input[name="site-package"]:checked');
  if (!pkgEl) return { total: 0, breakdown: [] };
  const [pkgName, pkgPrice] = pkgEl.value.split('|');
  let total = parseInt(pkgPrice, 10);
  const breakdown = [`${pkgName}: £${pkgPrice}`];
  document.querySelectorAll('.addon-select input:checked').forEach(cb => {
    const [addonName, addonPrice] = cb.value.split('|');
    total += parseInt(addonPrice, 10);
    breakdown.push(`${addonName}: +£${addonPrice}`);
  });
  return { total, breakdown };
}

function updateQuote() {
  const quote = calculateQuote();
  $('site-quote-price').textContent = quote.total;
  $('site-quote-breakdown').innerHTML = quote.breakdown.join('<br>');
  const box = document.querySelector('.quote-box-site');
  if (box) {
    box.style.transition = 'none';
    box.style.background = 'rgba(212, 175, 55, 0.15)';
    setTimeout(() => {
      box.style.transition = 'background 0.4s';
      box.style.background = 'rgba(212, 175, 55, 0.05)';
    }, 50);
  }
}

// ── Request Quote via Messaging ──
async function requestQuote() {
  updateQuote();
  const name = $('site-name').value.trim();
  const phone = $('site-phone').value.trim();
  if (!name || !phone) {
    showMsg('site-form-msg', 'Please enter your name and phone number to request a quote.', 'error');
    return;
  }
  showMsg('site-form-msg', 'Sending quote request...', '');
  const pkgEl = document.querySelector('input[name="site-package"]:checked');
  const [pkgName, pkgPrice] = pkgEl.value.split('|');
  const addons = [];
  document.querySelectorAll('.addon-select input:checked').forEach(cb => {
    const [aName, aPrice] = cb.value.split('|');
    addons.push({ name: aName, price: parseInt(aPrice, 10) });
  });
  const quoteData = {
    name, phone,
    carMake: $('site-car-make').value.trim(),
    package: pkgName,
    packagePrice: parseInt(pkgPrice, 10),
    addons,
    totalPrice: calculateQuote().total
  };
  try {
    const res = await fetch(`${API_BASE}/api/quote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(quoteData)
    });
    if (res.ok) {
      const result = await res.json();
      showMsg('site-form-msg', `Quote request sent! Your reference is ${result.bookingId}. Check Your Booking below for a reply.`, 'success');
      $('site-check-ref').value = result.bookingId;
    } else {
      const err = await res.json();
      showMsg('site-form-msg', 'Error: ' + (err.error || `HTTP ${res.status}`), 'error');
    }
  } catch (e) {
    showMsg('site-form-msg', 'Error: ' + e.message, 'error');
  }
}

// ── Submit Booking ──
async function submitBooking(e) {
  e.preventDefault();
  const name = $('site-name').value.trim();
  const phone = $('site-phone').value.trim();
  const carMake = $('site-car-make').value.trim();
  const date = $('site-booking-date').value;
  if (!name || !carMake) {
    showMsg('site-form-msg', 'Please provide both your name and car model to submit your booking.', 'error');
    return;
  }
  showMsg('site-form-msg', 'Submitting booking...', '');
  const pkgEl = document.querySelector('input[name="site-package"]:checked');
  const [pkgName, pkgPrice] = pkgEl.value.split('|');
  const addons = [];
  document.querySelectorAll('.addon-select input:checked').forEach(cb => {
    const [aName, aPrice] = cb.value.split('|');
    addons.push({ name: aName, price: parseInt(aPrice, 10) });
  });
  const bookingData = {
    name, phone,
    email: $('site-email').value.trim(),
    carMake,
    carReg: $('site-car-reg').value.trim() || 'N/A',
    package: pkgName,
    packagePrice: parseInt(pkgPrice, 10),
    date,
    addons,
    totalPrice: calculateQuote().total,
    specialRequests: $('site-special-requests').value.trim() || 'None'
  };
  try {
    const res = await fetch(`${API_BASE}/api/bookings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(bookingData)
    });
    if (res.ok) {
      const result = await res.json();
      showMsg('site-form-msg', `🎉 Booking Confirmed! Your reference is #${result.bookingId}`, 'success');
      $('site-check-ref').value = result.bookingId;
      $('site-booking-form').reset();
      // Re-init defaults
      $('site-booking-date').min = new Date().toISOString().split('T')[0];
      updateQuote();
    } else {
      const err = await res.json();
      showMsg('site-form-msg', 'Error: ' + (err.error || `HTTP ${res.status}`), 'error');
    }
  } catch (e) {
    showMsg('site-form-msg', 'Error: ' + e.message, 'error');
  }
}

// ── Check Booking ──
async function checkBooking() {
  const ref = $('site-check-ref').value.trim().replace('#', '').toLowerCase();
  if (!ref) {
    showMsg('site-check-msg', 'Please enter a booking reference', 'error');
    return;
  }
  showMsg('site-check-msg', 'Looking up...', '');
  $('site-check-result').classList.add('hidden');
  try {
    const res = await fetch(`${API_BASE}/api/bookings/ref/${encodeURIComponent(ref)}`);
    const data = await res.json();
    if (!data.found) {
      showMsg('site-check-msg', '❌ Booking not found. Double-check your reference number.', 'error');
      return;
    }
    const responses = data.responses || [];
    const latestStatus = responses.length > 0 ? responses[responses.length - 1].status : 'pending';
    const content = data.content || '';
    const lines = content.split('\n');
    const detailLines = lines.filter(l =>
      l.startsWith('Name:') || l.startsWith('Phone:') || l.startsWith('Email:') ||
      l.startsWith('Vehicle:') || l.startsWith('Registration:') ||
      l.startsWith('Selected Package:') || l.startsWith('Scheduled Date:') ||
      l.startsWith('ESTIMATED TOTAL:')
    );
    let html = '<div class="check-detail-box">';
    html += '<p class="check-detail-title">📋 Your Booking Details</p>';
    detailLines.forEach(l => {
      html += `<p class="check-detail-line">${escapeHtml(l)}</p>`;
    });
    html += '</div>';
    if (responses.length > 0) {
      html += '<p style="color:#d4af37; font-weight:bold; margin-top:15px;">📨 Messages from KC Legacy</p>';
      responses.forEach(r => {
        const sc = r.status === 'confirmed' ? '#4caf50' : r.status === 'reschedule' ? '#ff9800' : '#2196f3';
        const st = (r.status || 'pending').charAt(0).toUpperCase() + (r.status || 'pending').slice(1);
        html += `<div class="check-response-card" style="border-left-color:${sc}">`;
        html += `<p class="check-response-time" style="color:${sc}">${st} — ${escapeHtml(r.timestamp || '')}</p>`;
        html += `<p class="check-response-text">${escapeHtml(r.message || '')}</p>`;
        html += '</div>';
      });
    } else {
      html += '<p style="color:#888; text-align:center; margin-top:15px;">ℹ️ No messages yet. We\'ll update you here once we review your booking.</p>';
    }
    $('site-check-result').innerHTML = html;
    $('site-check-result').classList.remove('hidden');
    showMsg('site-check-msg', '', '');
  } catch (e) {
    showMsg('site-check-msg', '❌ Could not check booking: ' + e.message, 'error');
  }
}

// ── Gallery ──
async function loadGallery() {
  const grid = $('gallery-grid');
  try {
    const res = await fetch(`${API_BASE}/api/images`);
    const data = await res.json();
    const images = data.images || [];
    // Filter out non-photos
    const excluded = ['facebook_logo', 'favicon', 'header2', 'KCLegacy', 'product', 'kclecy'];
    const realPhotos = images.filter(img => {
      const fn = img.filename || '';
      const dotIdx = fn.lastIndexOf('.');
      const base = dotIdx > 0 ? fn.substring(0, dotIdx).toLowerCase() : fn.toLowerCase();
      return !excluded.some(ex => base.includes(ex));
    });
    if (realPhotos.length === 0) {
      grid.innerHTML = '<p style="color:#888; text-align:center;">No images uploaded yet. Be the first to share your before &amp; after!</p>';
      return;
    }
    grid.innerHTML = realPhotos.map(img =>
      `<div class="gallery-item"><img src="${API_BASE}/api/images/${encodeURIComponent(img.filename)}" alt="KC Legacy Work" loading="lazy"></div>`
    ).join('');
  } catch (e) {
    grid.innerHTML = '<p style="color:#888; text-align:center;">Could not load gallery. Please try again later.</p>';
  }
}

// ── Init ──
function init() {
  // Set min date to today
  const today = new Date().toISOString().split('T')[0];
  $('site-booking-date').min = today;

  // Event listeners
  $('site-quote-btn').addEventListener('click', requestQuote);
  $('site-booking-form').addEventListener('submit', submitBooking);
  $('site-check-btn').addEventListener('click', checkBooking);
  $('site-check-ref').addEventListener('keydown', e => {
    if (e.key === 'Enter') { e.preventDefault(); checkBooking(); }
  });

  // Auto-update quote on package/addon change (for fallback static elements)
  document.querySelectorAll('input[name="site-package"]').forEach(el => {
    el.addEventListener('change', updateQuote);
  });
  document.querySelectorAll('.addon-select input').forEach(el => {
    el.addEventListener('change', updateQuote);
  });

  // Initial quote
  updateQuote();

  // Load live packages from server (overrides static HTML if successful)
  loadPackages();
}

document.addEventListener('DOMContentLoaded', init);
