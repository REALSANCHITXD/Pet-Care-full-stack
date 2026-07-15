// ══════════════════════════════════════════════════════════
// BOOKINGS
// ══════════════════════════════════════════════════════════

async function loadBookings() {
    const grid = document.getElementById('bookings-grid');
    if (!grid) return;

    // Show loading state
    grid.innerHTML = `<div class="loading-skeleton" style="height:140px;border-radius:16px;grid-column:1/-1"></div>`;

    try {
        const res = await api.get('/bookings');

        // No bookings (404) → show empty state
        if (!res || res.status === 404) {
            renderBookings([]);
            return;
        }

        if (!res.ok) {
            grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">⚠️</div><p>Could not load bookings.</p></div>`;
            return;
        }

        const bookings = await res.json();
        renderBookings(bookings);
    } catch {
        grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">⚠️</div><p>Server error loading bookings.</p></div>`;
    }
}

async function renderBookings(bookings) {
    const grid = document.getElementById('bookings-grid');
    if (!bookings || bookings.length === 0) {
        grid.innerHTML = `<div class="empty-state" style="grid-column: 1/-1;"><div class="empty-icon">📅</div><p>You have no upcoming appointments.</p></div>`;
        return;
    }
    
    // Sort bookings by appointment time (closest first)
    bookings.sort((a, b) => new Date(a.appointment_time) - new Date(b.appointment_time));

    // Wait, the booking model has `vet_id` but not the vet's name. We might need to fetch vet details if they aren't included.
    // Let's try to map the vet_id to vet name if state.vets is populated, otherwise just show ID.
    // Ensure vets are loaded first so we have the names.
    if (!state.vets || state.vets.length === 0) {
        try {
            const vetRes = await api.get('/vets');
            if (vetRes && vetRes.ok) {
                state.vets = await vetRes.json();
            }
        } catch { /* silent */ }
    }

    grid.innerHTML = bookings.map(b => {
        const d = new Date(b.appointment_time);
        const dateStr = d.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
        const timeStr = d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
        
        const vet = (state.vets || []).find(v => v.id === b.vet_id);
        const vetName = vet ? vet.name : `Vet #${b.vet_id}`;
        const clinicName = vet && vet.clinic_name ? vet.clinic_name : '';
        
        const isPast = d < new Date();
        const statusBadge = isPast ? '<span style="color:var(--text-muted);font-size:0.8rem">Completed</span>' 
                                   : `<span style="color:var(--accent-teal);font-weight:bold;font-size:0.8rem;background:rgba(6,182,212,0.1);padding:2px 8px;border-radius:12px;">Upcoming</span>`;

        return `
        <div class="card" style="padding:20px;border-radius:16px;background:var(--bg-card);border:1px solid var(--border-light);display:flex;flex-direction:column;gap:12px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                    <h3 style="margin:0;font-size:1.1rem;color:var(--text-main)">🩺 ${escHtml(vetName)}</h3>
                    ${clinicName ? `<div style="font-size:0.85rem;color:var(--text-secondary);margin-top:2px">${escHtml(clinicName)}</div>` : ''}
                </div>
                ${statusBadge}
            </div>
            
            <div style="background:var(--bg-main);padding:12px;border-radius:8px;font-size:0.9rem;color:var(--text-main);">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                    <span style="opacity:0.7">📅</span> <strong>${dateStr}</strong> at <strong>${timeStr}</strong>
                </div>
                <div style="display:flex;align-items:flex-start;gap:8px;">
                    <span style="opacity:0.7">💬</span> <span style="color:var(--text-secondary)">${escHtml(b.reason || 'General consultation')}</span>
                </div>
            </div>
            
            ${!isPast ? `
            <div style="margin-top:auto;text-align:right">
                <button onclick="cancelBooking(${b.id})" style="background:transparent;border:1px solid var(--accent-rose);color:var(--accent-rose);padding:6px 12px;border-radius:8px;cursor:pointer;font-size:0.85rem;transition:all 0.2s;">
                    Cancel Appointment
                </button>
            </div>
            ` : ''}
        </div>
        `;
    }).join('');
}

async function cancelBooking(id) {
    if (!confirm('Are you sure you want to cancel this appointment?')) return;
    
    try {
        const res = await api.delete(`/bookings/${id}`);
        if (!res || !res.ok) {
            showToast('Failed to cancel booking.', 'error');
            return;
        }
        showToast('Appointment cancelled.', 'info');
        loadBookings();
    } catch {
        showToast('Server error.', 'error');
    }
}
