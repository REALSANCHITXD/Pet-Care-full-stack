// ══════════════════════════════════════════════════════════
// VET FINDER
// ══════════════════════════════════════════════════════════
async function initVetFinder() {
    initMap();
    await loadVets();
}

function initMap() {
    if (state.mapInstance) return;
    state.mapInstance = L.map('vet-map').setView([20.5937, 78.9629], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18,
    }).addTo(state.mapInstance);
}

async function loadVets() {
    try {
        const res = await api.get('/vets');
        if (!res || !res.ok) { showToast('Could not load vets.', 'error'); return; }
        state.vets = await res.json();
        renderVetCards(state.vets);
        renderVetMarkers(state.vets);
    } catch { showToast('Server error loading vets.', 'error'); }
}

async function filterVets() {
    const specialty = document.getElementById('vet-specialty-filter').value.trim();
    if (!specialty) { loadVets(); return; }
    try {
        const res = await api.get(`/vets/search/specialties?specialties=${encodeURIComponent(specialty)}&clinic_name=`);
        if (!res || !res.ok) { showToast('Filter failed.', 'error'); return; }
        const vets = await res.json();
        state.vets = vets;
        renderVetCards(vets);
        renderVetMarkers(vets);
    } catch { showToast('Server error.', 'error'); }
}

function renderVetCards(vets) {
    const list = document.getElementById('vet-cards-list');
    if (!vets || vets.length === 0) {
        list.innerHTML = `<div class="empty-state"><div class="empty-icon">🏥</div><p>No vets found.</p></div>`;
        return;
    }
    list.innerHTML = vets.map(v => `
        <div class="vet-card" onclick="openVetPanel(${v.id})">
            <div class="vet-card-top">
                <div class="vet-avatar">🩺</div>
                <div>
                    <div class="vet-name">${escHtml(v.name)}</div>
                    <div class="vet-clinic">${escHtml(v.clinic_name || '')}</div>
                </div>
                <div class="vet-rating">
                    <div class="stars">${renderStars(v.rating)}</div>
                    <div class="score">${v.rating ? Number(v.rating).toFixed(1) : '—'}</div>
                </div>
            </div>
            <div class="vet-specialties">
                ${(v.specialties || '').split(',').filter(Boolean).map(s =>
                    `<span class="specialty-tag">${escHtml(s.trim())}</span>`
                ).join('')}
            </div>
        </div>
    `).join('');
}

function renderVetMarkers(vets) {
    if (!state.mapInstance) return;
    // Clear old markers
    state.mapMarkers.forEach(m => m.remove());
    state.mapMarkers = [];

    const validVets = vets.filter(v => v.latitude && v.longitude);
    validVets.forEach(v => {
        const marker = L.circleMarker([v.latitude, v.longitude], {
            radius: 10,
            fillColor: '#06b6d4',
            color: '#fff',
            weight: 2,
            fillOpacity: 0.85,
        }).addTo(state.mapInstance);

        marker.bindPopup(`
            <div class="vet-map-popup">
                <h3>🩺 ${escHtml(v.name)}</h3>
                <p>${escHtml(v.clinic_name || '')} • ⭐ ${v.rating || '—'}</p>
                <button class="popup-view-btn" onclick="openVetPanel(${v.id})">View & Book</button>
            </div>
        `);
        state.mapMarkers.push(marker);
    });

    if (validVets.length > 0) {
        const group = L.featureGroup(state.mapMarkers);
        state.mapInstance.fitBounds(group.getBounds().pad(0.2));
    }
}

function openVetPanel(vetId) {
    const vet = state.vets.find(v => v.id === vetId);
    if (!vet) return;
    state.selectedVet = vet;

    document.getElementById('so-name').textContent = vet.name;
    document.getElementById('so-clinic').textContent = vet.clinic_name || '';
    document.getElementById('so-rating').textContent = vet.rating ? `${Number(vet.rating).toFixed(1)} ⭐` : 'No rating';
    document.getElementById('so-stars').innerHTML = renderStars(vet.rating);
    document.getElementById('so-address').textContent = vet.address || 'Address not available';
    document.getElementById('so-specialties').textContent = vet.specialties || 'General Practice';
    document.getElementById('so-coords').textContent = vet.latitude && vet.longitude
        ? `${Number(vet.latitude).toFixed(4)}, ${Number(vet.longitude).toFixed(4)}`
        : 'Not available';

    document.getElementById('so-book-btn').onclick = () => openBookingModal(vet);
    document.getElementById('vet-slideover').classList.add('open');

    // Fly to marker on map
    if (vet.latitude && vet.longitude && state.mapInstance) {
        state.mapInstance.flyTo([vet.latitude, vet.longitude], 14, { duration: 1 });
    }
}

function closeVetPanel() {
    document.getElementById('vet-slideover').classList.remove('open');
    state.selectedVet = null;
}

function openBookingModal(vet) {
    state.bookingVetId = vet.id;
    document.getElementById('booking-vet-name').textContent = `${vet.name} — ${vet.clinic_name || ''}`;
    // Set min datetime to now
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('booking-datetime').min = now.toISOString().slice(0,16);
    document.getElementById('booking-modal').classList.add('open');
}

function closeBookingModal() {
    document.getElementById('booking-modal').classList.remove('open');
}

async function confirmBooking() {
    const dateTime = document.getElementById('booking-datetime').value;
    const reason = document.getElementById('booking-reason').value.trim();
    if (!dateTime) { showToast('Please select a date and time.', 'error'); return; }
    if (!state.user) return;

    try {
        const res = await api.post('/bookings', {
            user_id: state.user.id,
            vet_id: state.bookingVetId,
            appointment_time: new Date(dateTime).toISOString(),
            reason: reason || 'General consultation',
        });
        if (!res) return;
        const data = await res.json();
        if (!res.ok) { showToast(data.detail || 'Booking failed.', 'error'); return; }
        closeBookingModal();
        closeVetPanel();
        showToast('Appointment booked! 🏥', 'success');
    } catch { showToast('Server error.', 'error'); }
}