/**
 * KC Legacy Valeting - Customer Booking App
 * Connects to the backend API server to submit bookings
 */

// ── Configuration ──
const API_BASE = 'https://kclegeacy.pythonanywhere.com';

// ── Utility ──
function $(id) { return document.getElementById(id); }

function showMsg(id, text, type) {
  const el = $(id);
  el.textContent = text;
  el.className = 'msg ' + (type || '');
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ── API ──
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

// ── Quote Calculator ──
function calculateQuote() {
  const packageEl = document.querySelector('input[name="package"]:checked');
  if (!packageEl) return { total: 0, breakdown: [] };

  const [pkgName, pkgPrice] = packageEl.value.split('|');
  let total = parseInt(pkgPrice, 10);
  const breakdown = [`${pkgName}: &pound;${pkgPrice}`];

  document.querySelectorAll('.addon-card input:checked').forEach(cb => {
    const [addonName, addonPrice] = cb.value.split('|');
    const price = parseInt(addonPrice, 10);
    total += price;
    breakdown.push(`${addonName}: +&pound;${addonPrice}`);
  });

  return { total, breakdown };
}

function updateQuote() {
  const quote = calculateQuote();
  $('quote-price').textContent = quote.total;
  $('quote-breakdown').innerHTML = quote.breakdown.join('<br>');
}

// ── Form Handling ──
function getFormData() {
  const packageEl = document.querySelector('input[name="package"]:checked');
  const [pkgName, pkgPrice] = packageEl.value.split('|');

  const addons = [];
  document.querySelectorAll('.addon-card input:checked').forEach(cb => {
    const [name, price] = cb.value.split('|');
    addons.push({ name, price: parseInt(price, 10) });
  });

  return {
    name: $('cust-name').value.trim(),
    phone: $('cust-phone').value.trim(),
    email: $('cust-email').value.trim(),
    carMake: $('car-make').value.trim(),
    carReg: $('car-reg').value.trim(),
    date: $('booking-date').value,
    package: pkgName,
    packagePrice: parseInt(pkgPrice, 10),
    addons: addons,
    specialRequests: $('special-requests').value.trim(),
    totalPrice: calculateQuote().total
  };
}

function validateForm(data) {
  if (!data.name) return 'Please enter your name.';
  if (!data.phone) return 'Please enter your phone number.';
  if (!data.carMake) return 'Please enter your car make & model.';
  if (!data.date) return 'Please select a preferred date.';
  return null;
}

// ── Submit Booking ──
async function submitBooking(e) {
  e.preventDefault();

  const data = getFormData();
  const error = validateForm(data);
  if (error) {
    showMsg('form-msg', error, 'error');
    return;
  }

  showMsg('form-msg', 'Submitting booking...', '');

  try {
    const res = await fetch(`${API_BASE}/api/bookings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (res.ok) {
      const result = await res.json();
      showMsg('form-msg', 'Booking submitted successfully!', 'success');
      $('booking-form').classList.add('hidden');
      $('success-screen').classList.remove('hidden');
      $('success-screen').classList.add('active');
      $('ref-number').textContent = result.bookingId || '---';

      // Save reference to localStorage for easy lookup later
      if (result.bookingId) {
        const saved = JSON.parse(localStorage.getItem('kc_my_bookings') || '[]');
        saved.unshift({
          ref: result.bookingId,
          name: data.name,
          package: data.package,
          date: data.date,
          timestamp: new Date().toISOString()
        });
        // Keep only last 5
        if (saved.length > 5) saved.pop();
        localStorage.setItem('kc_my_bookings', JSON.stringify(saved));
        // Also save latest for quick check
        localStorage.setItem('kc_last_booking_ref', result.bookingId);
      }

      // 10-second countdown to auto-return
      let seconds = 10;
      const countdownEl = $('countdown');
      countdownEl.textContent = seconds;

      const timer = setInterval(() => {
        seconds--;
        countdownEl.textContent = seconds;
        if (seconds <= 0) {
          clearInterval(timer);
          resetForm();
        }
      }, 1000);

      // Wire up the Check Status button on success screen
      const checkBtn = $('check-status-btn');
      checkBtn.onclick = () => {
        clearInterval(timer);
        $('success-screen').classList.remove('active');
        $('check-ref').value = result.bookingId || '';
        $('check-booking').scrollIntoView({ behavior: 'smooth' });
        checkBooking();
      };

      // Also wire up the new-booking button to clear timer
      $('new-booking-btn').onclick = () => {
        clearInterval(timer);
        resetForm();
      };
    } else {
      const err = await res.json();
      showMsg('form-msg', 'Error: ' + (err.error || `HTTP ${res.status}`), 'error');
    }
  } catch (e) {
    showMsg('form-msg', 'Error: ' + e.message + '. Check your internet connection.', 'error');
  }
}

// ── Reset Form ──
function resetForm() {
  $('booking-form').reset();
  $('booking-form').classList.remove('hidden');
  $('success-screen').classList.remove('active');
  $('success-screen').classList.add('hidden');
  showMsg('form-msg', '', '');
  updateQuote();
}

// ── Check My Booking ──
async function checkBooking() {
  const ref = $('check-ref').value.trim().toLowerCase();
  if (!ref) {
    showMsg('check-msg', 'Please enter a booking reference', 'error');
    return;
  }

  showMsg('check-msg', 'Looking up...', '');
  $('check-result').classList.add('hidden');

  try {
    const res = await fetch(`${API_BASE}/api/bookings/ref/${encodeURIComponent(ref)}`);
    const data = await res.json();

    if (!data.found) {
      showMsg('check-msg', 'Booking not found. Check your reference number.', 'error');
      return;
    }

    // Parse the latest status from responses
    const responses = data.responses || [];
    const latestStatus = responses.length > 0
      ? responses[responses.length - 1].status
      : 'pending';

    // Show result
    $('check-result').classList.remove('hidden');
    const badge = $('check-status-badge');
    badge.textContent = latestStatus;
    badge.className = 'check-badge ' + latestStatus;

    // Show booking details (sanitised)
    $('check-details').textContent = data.content || 'No details available';

    // Show responses
    const respContainer = $('check-responses');
    if (responses.length > 0) {
      respContainer.innerHTML = responses.map(r => `
        <div class="check-response-card">
          <div class="check-response-time">${escapeHtml(r.timestamp)} &middot; Status: ${escapeHtml(r.status)}</div>
          <div class="check-response-text">${escapeHtml(r.message)}</div>
        </div>
      `).join('');
    } else {
      respContainer.innerHTML = '<p style="color:#888;font-size:0.8rem;text-align:center;">No responses yet. Check back later.</p>';
    }

    showMsg('check-msg', '', '');
  } catch (e) {
    showMsg('check-msg', 'Error: ' + e.message, 'error');
  }
}

// ── Init ──
function init() {
  // Set min date to today
  const today = new Date().toISOString().split('T')[0];
  $('booking-date').min = today;

  // Event listeners
  $('quote-btn').addEventListener('click', updateQuote);
  $('booking-form').addEventListener('submit', submitBooking);
  $('new-booking-btn').addEventListener('click', resetForm);
  $('check-btn').addEventListener('click', checkBooking);
  $('check-ref').addEventListener('keydown', e => {
    if (e.key === 'Enter') checkBooking();
  });

  // Auto-update quote on package/addon change
  document.querySelectorAll('input[name="package"]').forEach(el => {
    el.addEventListener('change', updateQuote);
  });
  document.querySelectorAll('.addon-card input').forEach(el => {
    el.addEventListener('change', updateQuote);
  });

  // Load saved bookings from localStorage
  loadSavedBookings();

  // Initial quote
  updateQuote();
}

// ── Load Saved Bookings ──
function loadSavedBookings() {
  const saved = JSON.parse(localStorage.getItem('kc_my_bookings') || '[]');
  const container = $('saved-bookings-list');
  if (!container) return;

  if (saved.length === 0) {
    container.innerHTML = '<p style="color:#888;font-size:0.8rem;text-align:center;">No saved bookings yet. Make a booking to see it here.</p>';
    return;
  }

  // Auto-fill the check input with the most recent booking
  const lastRef = saved[0].ref;
  $('check-ref').value = lastRef;

  container.innerHTML = saved.map(b => `
    <div class="saved-booking-chip" data-ref="${escapeHtml(b.ref)}">
      <span class="saved-ref">#${escapeHtml(b.ref)}</span>
      <span class="saved-info">${escapeHtml(b.package)} — ${escapeHtml(b.date)}</span>
    </div>
  `).join('');

  // Click to check
  container.querySelectorAll('.saved-booking-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      $('check-ref').value = chip.dataset.ref;
      checkBooking();
    });
  });
}

document.addEventListener('DOMContentLoaded', init);
