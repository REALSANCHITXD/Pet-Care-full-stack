/* ============================================================
   Dr. Paws — Dashboard Orchestrator
   Handles: Store, Vet Finder, AI Chat, Orders, Pets, Settings
   ============================================================ */

// ── Global State ──────────────────────────────────────────

// ── Boot ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    if (!localStorage.getItem('drpaws_token')) {
        window.location.href = 'index.html';
        return;
    }
    await loadUser();
    setupNav();
    setupChatInput();
    setupSearch();
    await loadProducts();
    await loadCart();
});

// ══════════════════════════════════════════════════════════
// USER & AUTH
// ══════════════════════════════════════════════════════════
async function loadUser() {
    try {
        const res = await api.get('/users/me');
        if (!res) return;
        // Try /users/me first; if not found, try /users
        if (res.ok) {
            state.user = await res.json();
        } else {
            // Fallback: get from token payload
            const token = localStorage.getItem('drpaws_token');
            const payload = JSON.parse(atob(token.split('.')[1]));
            state.user = { id: payload.user_id, role: payload.role, subscription_tier: 'free', name: 'User', email: '' };
            // Try fetching by id
            const res2 = await api.get(`/users/${payload.user_id}`);
            if (res2 && res2.ok) state.user = await res2.json();
        }
    } catch {
        const token = localStorage.getItem('drpaws_token');
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            state.user = { id: payload.user_id, role: payload.role, subscription_tier: 'free', name: 'User', email: '' };
        } catch { logout(); return; }
    }
    renderUserInfo();
}

function renderUserInfo() {
    const u = state.user;
    if (!u) return;
    const name = u.name || u.email || 'User';
    const initials = name.slice(0, 2).toUpperCase();

    document.getElementById('user-avatar').textContent = initials;
    document.getElementById('user-name').textContent = name;
    document.getElementById('user-email').textContent = u.email || '';

    const isPremium = u.subscription_tier === 'premium';
    document.getElementById('premium-badge-wrap').classList.toggle('hidden', !isPremium);
    document.getElementById('upgrade-link-wrap').classList.toggle('hidden', isPremium);

    // Settings tab
    document.getElementById('settings-name').textContent = name;
    document.getElementById('settings-email').textContent = u.email || '—';
    document.getElementById('settings-plan').textContent = isPremium ? '✨ Premium' : 'Free';
    document.getElementById('upgrade-banner').classList.toggle('hidden', isPremium);

    // Free tier query counter
    if (!isPremium) {
        document.getElementById('query-counter').classList.remove('hidden');
    }
}

function logout() {
    localStorage.clear();
    window.location.href = 'index.html';
}
document.getElementById('logout-btn').addEventListener('click', logout);

// ══════════════════════════════════════════════════════════
// NAVIGATION
// ══════════════════════════════════════════════════════════
function setupNav() {
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
}

function switchTab(tab) {
    state.currentTab = tab;
    // Update nav active state
    document.querySelectorAll('.nav-item').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
    // Show/hide sections
    document.querySelectorAll('.tab-section').forEach(s => s.classList.toggle('active', s.id === `tab-${tab}`));

    // Update header title
    const titles = { store:'Pet Store', vets:'Vet Finder', chat:'AI Vet Assistant', orders:'My Orders', bookings:'My Bookings', pets:'My Pets', settings:'Settings' };
    document.getElementById('header-title').textContent = titles[tab] || '';

    // Cart button only on store
    document.getElementById('cart-btn').classList.toggle('hidden', tab !== 'store');
    document.getElementById('search-bar-wrap').classList.toggle('hidden', tab !== 'store');

    // Lazy-load tab data
    if (tab === 'vets' && state.vets.length === 0) initVetFinder();
    if (tab === 'chat' && state.sessions.length === 0) loadSessions();
    if (tab === 'orders') loadOrders();
    if (tab === 'bookings') loadBookings();
    if (tab === 'pets') loadPets();
}